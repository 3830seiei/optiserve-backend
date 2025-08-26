"""routers/file_management.py

ファイル管理関連のAPIエンドポイント定義

Note:
    - 本モジュールは、医療機関からのファイルアップロードとシステム生成レポートのダウンロード機能を提供します。
    - 月次運用に対応し、3種類のファイル（医療機器台帳・貸出履歴・故障履歴）の同時アップロードをサポートします。
    - 3種類のレポート（分析レポート・故障リスト・未実績リスト）の配信機能を提供します。
    - ファイルの実体はローカルファイルシステムまたは将来的にはAWS S3に保存されます。
    - 履歴管理はfacility_upload_logとreport_publication_logテーブルで行います。
    - 通知機能により、アップロード完了時とレポート公開時に自動でメール通知を送信します。

ChangeLog:
    v1.0.0 (2025-08-07)
    - 初版作成
    v1.1.0 (2025-08-26)
    - OS環境に応じた動的パス設定対応
"""
import shutil
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Header
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import SessionLocal
from src.models.pg_optigate.facility_upload_log import FacilityUploadLog
from src.models.pg_optigate.mst_medical_facility import MstMedicalFacility
from src.models.pg_optigate.user_entity_link import UserEntityLink
from src.models.pg_optigate.report_publication_log import ReportPublicationLog
from src.schemas.facility_upload import (
    FacilityUpload,
    FileUploadResponse
)
from src.schemas.report_publication import (
    MonthlyReportPublishResponse,
    AvailableReport,
    ReportPublication
)
from src.schemas.file_management import (
    MonthlyFileStatus,
    validate_file_extension
)
from ..utils.auth import AuthManager
from ..utils.path_config import path_config
# from smds_core.logger import Logger  # 一時的にコメントアウト
import logging

router = APIRouter(
    prefix="/api/v1/files",
    tags=["file-management"],
)

# シングルトンロガーの取得（一時的にPython標準ライブラリ使用）
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ファイル保存パス設定（OS環境に応じて動的設定）
FILES_BASE_PATH = path_config.files_base_path
UPLOADS_PATH = path_config.uploads_path
REPORTS_PATH = path_config.reports_path

# オンプレミスレポート保存パス
ONPRE_REPORTS_PATH = path_config.onpre_reports_path

# 必要なディレクトリを作成
path_config.ensure_directories()

# システム用APIキー（本番環境では環境変数から取得推奨）
SYSTEM_API_KEY = "optiserve-internal-system-key-2025"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def ensure_directory_exists(path: Path):
    """ディレクトリが存在しない場合は作成"""
    path.mkdir(parents=True, exist_ok=True)

def verify_system_key(x_system_key: str = Header(None, alias="X-System-Key")):
    """システム用APIキーの認証"""
    if not x_system_key or x_system_key != SYSTEM_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="System API key is required for this endpoint"
        )
    return x_system_key

def get_upload_file_path(medical_id: int, file_type: int) -> Path:
    """アップロードファイルのパスを生成（医療機関単位・1世代保管）"""
    file_extensions = {1: ".csv", 2: ".csv", 3: ".csv"}  # 医療機器台帳、貸出履歴、故障履歴
    file_names = {1: "equipment", 2: "rental", 3: "failure"}
    
    filename = f"{file_names[file_type]}{file_extensions[file_type]}"
    return UPLOADS_PATH / str(medical_id) / filename

def get_report_file_path(medical_id: int, publication_ym: str, file_type: int) -> Path:
    """レポートファイルのパスを生成（年/月階層構造）"""
    file_extensions = {1: ".pdf", 2: ".xlsx", 3: ".xlsx"}  # 分析レポート、故障リスト、未実績リスト
    file_names = {1: "analysis_report", 2: "failure_list", 3: "unachieved_list"}
    
    # YYYY-MM形式から年と月を分離（月は0埋め2桁）
    year, month = publication_ym.split("-")
    month_int = int(month)
    month_padded = f"{month_int:02d}"  # 月を0埋め2桁に
    filename = f"{file_names[file_type]}{file_extensions[file_type]}"
    return REPORTS_PATH / str(medical_id) / year / month_padded / filename

def get_onpremise_report_files(hpcode: int, year: int, month: int) -> List[Path]:
    """オンプレミスで生成されたレポートファイル一覧を取得"""
    # 月を0埋め2桁に変換してパス生成
    month_padded = f"{month:02d}"
    onpre_path = ONPRE_REPORTS_PATH / str(hpcode) / str(year) / month_padded
    if not onpre_path.exists():
        return []
    
    # ディレクトリ内の全ファイルを取得（拡張子フィルタなし）
    files = []
    for file_path in onpre_path.iterdir():
        if file_path.is_file():
            files.append(file_path)
    return files

def copy_onpremise_reports_to_publication(hpcode: int, publication_ym: str) -> List[str]:
    """オンプレミスレポートを公開ディレクトリにコピー（年/月階層構造）"""
    year, month = publication_ym.split("-")
    year_int = int(year)
    month_int = int(month)
    
    # オンプレミスレポートファイル一覧取得
    onpre_files = get_onpremise_report_files(hpcode, year_int, month_int)
    if not onpre_files:
        return []
    
    # コピー先ディレクトリ準備（年/月階層構造、月は0埋め2桁）
    month_padded = f"{month_int:02d}"  # 月を0埋め2桁に
    dest_dir = REPORTS_PATH / str(hpcode) / year / month_padded
    ensure_directory_exists(dest_dir)
    
    copied_files = []
    for source_file in onpre_files:
        dest_file = dest_dir / source_file.name
        shutil.copy2(source_file, dest_file)
        copied_files.append(source_file.name)
        logger.info(f"レポートファイルコピー完了: {source_file} -> {dest_file}")
    
    return copied_files

async def send_notification_email(medical_id: int, notification_type: str, target_month: str):
    """通知メール送信（将来実装）"""
    try:
        # user_entity_linkからnotification_email_listを取得
        db = SessionLocal()
        try:
            link = db.query(UserEntityLink).filter(
                UserEntityLink.entity_type == 1,
                UserEntityLink.entity_relation_id == medical_id
            ).first()
            
            if link is not None and hasattr(link, 'notification_email_list') and link.notification_email_list:
                # TODO: 実際のメール送信実装
                logger.info(f"通知メール送信予定: {notification_type}, 医療機関ID={medical_id}, 対象月={target_month}")
                logger.debug(f"送信先: {link.notification_email_list}")
                return True
            else:
                logger.warning(f"通知先メールアドレスが設定されていません: 医療機関ID={medical_id}")
                return False
        finally:
            db.close()
    except Exception as e:
        logger.error(f"通知メール送信エラー: {e}")
        return False

@router.post("/upload-files/{medical_id}", response_model=FileUploadResponse)
async def upload_files(
    medical_id: int,
    upload_user_id: str = Form(..., description="アップロードを行うユーザーID"),
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    equipment_file: UploadFile = File(..., description="医療機器台帳ファイル"),
    rental_file: UploadFile = File(..., description="貸出履歴ファイル"),
    failure_file: UploadFile = File(..., description="故障履歴ファイル"),
    db: Session = Depends(get_db)
):
    """
    Upload Files from Medical Facility

    [Japanese]
    医療機関ファイル一括アップロード

    - 医療機関から提供される3種類のファイルを同時にアップロードします
    - 再アップロードは既存ファイルを上書きします（最新1世代のみ保持）
    - アップロード完了時に通知メールを送信します
    - 全てのアップロード実行履歴をDBに記録します（ファイル名変更なし）

    Args:
    - medical_id (int): 医療機関ID
    - upload_user_id (str): アップロードを行うユーザーID
    - equipment_file (UploadFile): 医療機器台帳ファイル（CSV）
    - rental_file (UploadFile): 貸出履歴ファイル（CSV）
    - failure_file (UploadFile): 故障履歴ファイル（CSV）

    Returns:
    - MonthlyUploadResponse: アップロード結果とファイル一覧

    [English]
    Upload files from medical facilities

    - Uploads 3 types of files provided by medical facilities
    - Re-uploads will overwrite existing files (keeps only latest generation)
    - Sends notification email upon upload completion
    - Records all upload history in database (no filename modification)

    Args:
    - medical_id (int): Medical facility ID
    - upload_user_id (str): ID of the user performing the upload
    - equipment_file (UploadFile): Medical equipment list file (CSV)
    - rental_file (UploadFile): Rental history file (CSV)  
    - failure_file (UploadFile): Failure history file (CSV)

    Returns:
    - MonthlyUploadResponse: Upload result and file list
    """
    try:
        # 医療機関アクセス権限チェック
        AuthManager.require_medical_permission(current_user_id, medical_id, db)
        
        logger.info(f"ファイルアップロード開始: 医療機関ID={medical_id}")
        
        # 医療機関の存在チェック
        medical_facility = db.query(MstMedicalFacility).filter(
            MstMedicalFacility.medical_id == medical_id
        ).first()
        if not medical_facility:
            raise HTTPException(
                status_code=400,
                detail=f"医療機関ID（medical_id） {medical_id} は存在しません"
            )
        
        # アップロードファイル情報
        upload_files = [
            (1, equipment_file, "医療機器台帳"),
            (2, rental_file, "貸出履歴"),
            (3, failure_file, "故障履歴")
        ]
        
        uploaded_records = []
        upload_datetime = datetime.now()
        
        for file_type, upload_file, file_description in upload_files:
            if not upload_file or not upload_file.filename:
                raise HTTPException(
                    status_code=400,
                    detail=f"{file_description}ファイルが指定されていません"
                )
            
            # ファイル拡張子チェック
            if not validate_file_extension(upload_file.filename, ".csv"):
                raise HTTPException(
                    status_code=400,
                    detail=f"{file_description}ファイルはCSV形式である必要があります"
                )
            
            # ファイル保存パス（医療機関単位・1世代保管）
            file_path = get_upload_file_path(medical_id, file_type)
            ensure_directory_exists(file_path.parent)
            
            # ファイル保存（上書き）
            with open(file_path, "wb") as buffer:
                content = await upload_file.read()
                buffer.write(content)
            
            # DB履歴記録（全てのアップロード履歴を追加・ファイル名変更なし）
            db_record = FacilityUploadLog(
                medical_id=medical_id,
                file_type=file_type,
                file_name=upload_file.filename,  # 元のファイル名をそのまま記録
                upload_datetime=upload_datetime,
                upload_user_id=upload_user_id,
                reg_user_id=current_user_id,
                regdate=upload_datetime,
                update_user_id=current_user_id,
                lastupdate=upload_datetime
            )
            db.add(db_record)
            db.commit()
            db.refresh(db_record)
            uploaded_records.append(db_record)
            
            logger.info(f"ファイル保存完了: {file_description} ({upload_file.filename}) -> {file_path}")
        
        # 通知メール送信
        notification_sent = await send_notification_email(
            medical_id, "upload", datetime.now().strftime("%Y-%m")
        )
        
        logger.info(f"ファイルアップロード完了: 医療機関ID={medical_id}, {len(uploaded_records)}件")
        
        return FileUploadResponse(
            medical_id=medical_id,
            target_month=datetime.now().strftime("%Y-%m"),  # 実行月を記録
            upload_datetime=upload_datetime.isoformat(),
            uploaded_files=[FacilityUpload.model_validate(record) for record in uploaded_records],
            notification_sent=notification_sent
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"月次ファイルアップロードエラー: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/upload-status/{medical_id}", response_model=List[MonthlyFileStatus])
async def get_upload_status(
    medical_id: int,
    months: Optional[int] = 6,  # デフォルト6ヶ月分
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)
):
    """
    Get Upload File Status

    [Japanese]
    アップロードファイル状況取得

    - 指定医療機関の月別アップロード状況を取得します
    - 直近N ヶ月分の状況を一覧表示できます

    Args:
    - medical_id (int): 医療機関ID
    - months (int, optional): 取得対象月数（デフォルト6ヶ月）

    Returns:
    - List[MonthlyFileStatus]: 月別ファイル状況一覧

    [English]
    Get upload file status for specified medical facility

    Args:
    - medical_id (int): Medical facility ID
    - months (int, optional): Number of months to retrieve (default 6 months)

    Returns:
    - List[MonthlyFileStatus]: Monthly file status list
    """
    # TODO: 実装
    # 指定医療機関の月別アップロード状況をDBから取得
    return []

@router.get("/reports/available/{medical_id}", response_model=List[AvailableReport])
async def get_available_reports(
    medical_id: int,
    months: Optional[int] = 12,  # デフォルト12ヶ月分
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)
):
    """
    Get Available Reports

    [Japanese]
    ダウンロード可能レポート一覧取得

    - 指定医療機関向けに公開されているレポート一覧を取得します
    - ダウンロード済み/未ダウンロード状況も含めて表示します

    Args:
    - medical_id (int): 医療機関ID
    - months (int, optional): 取得対象月数（デフォルト12ヶ月）

    Returns:
    - List[AvailableReport]: ダウンロード可能レポート一覧

    [English]  
    Get available reports for specified medical facility

    Args:
    - medical_id (int): Medical facility ID
    - months (int, optional): Number of months to retrieve (default 12 months)

    Returns:
    - List[AvailableReport]: Available report list
    """
    # TODO: 実装
    # 指定医療機関向けのレポート一覧をDBから取得
    return []

@router.get("/reports/download/{publication_id}")
async def download_report(
    publication_id: int,
    user_id: str,
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)
):
    """
    Download Report File

    [Japanese]
    レポートファイルダウンロード

    - 指定されたレポートファイルをダウンロードします
    - 初回ダウンロード時にダウンロード履歴を記録します

    Args:
    - publication_id (int): レポート公開ID
    - user_id (str): ダウンロードを行うユーザーID

    Returns:
    - FileResponse: レポートファイル

    [English]
    Download specified report file

    Args:
    - publication_id (int): Report publication ID
    - user_id (str): ID of user downloading the report

    Returns:
    - FileResponse: Report file
    """
    try:
        logger.info(f"レポートダウンロード開始: publication_id={publication_id}, user_id={user_id}")
        
        # レポート公開情報を取得
        report_publication = db.query(ReportPublicationLog).filter(
            ReportPublicationLog.publication_id == publication_id
        ).first()
        
        if not report_publication:
            raise HTTPException(
                status_code=404,
                detail=f"指定されたレポート公開ID {publication_id} は存在しません"
            )
        
        # レポートファイルのパスを構築（年/月階層構造）
        year, month = report_publication.publication_ym.split("-")
        month_int = int(month)
        month_padded = f"{month_int:02d}"
        
        file_path = REPORTS_PATH / str(report_publication.medical_id) / year / month_padded / report_publication.file_name
        
        # ファイル存在チェック
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"レポートファイルが見つかりません: {report_publication.file_name}"
            )
        
        # 初回ダウンロード時のみDB更新（download_datetimeがNoneの場合）
        if not report_publication.download_datetime:
            download_time = datetime.now()
            report_publication.download_user_id = user_id
            report_publication.download_datetime = download_time
            report_publication.update_user_id = current_user_id
            report_publication.lastupdate = download_time
            db.commit()
            logger.info(f"初回ダウンロード記録: publication_id={publication_id}, user_id={user_id}, download_datetime={download_time}")
        else:
            logger.info(f"既存ダウンロード記録あり: publication_id={publication_id}, 初回ダウンロード={report_publication.download_datetime}")
        
        # ファイル配信
        logger.info(f"レポートファイル配信: {file_path}")
        
        # MIMEタイプ設定
        media_type = "application/octet-stream"
        if file_path.suffix.lower() == ".pdf":
            media_type = "application/pdf"
        elif file_path.suffix.lower() in [".xlsx", ".xls"]:
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif file_path.suffix.lower() == ".pptx":
            media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        
        return FileResponse(
            path=file_path,
            filename=report_publication.file_name,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"レポートダウンロードエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# システム内部用ダウンロードエンドポイント
@router.get("/system/fetch-uploaded/{medical_id}")
async def fetch_uploaded_file(
    medical_id: int,
    file_type: int,
    system_key: str = Depends(verify_system_key),
    db: Session = Depends(get_db)
):
    """
    Fetch Uploaded File for Internal System
    
    [Japanese]
    オンプレミスシステム用ファイル取得
    
    - アップロードされたファイルをオンプレミスシステムが取得するためのAPI
    - ダウンロード時にfacility_upload_logのdownload_datetimeを更新
    - システム認証キーが必要（一般ユーザーからのアクセス制限）
    
    Args:
    - medical_id (int): 医療機関ID
    - file_type (int): ファイル種別（1: 医療機器台帳, 2: 貸出履歴, 3: 故障履歴）
    - X-System-Key (header): システム認証キー
    
    Returns:
    - FileResponse: 対象ファイル
    
    [English]
    Fetch uploaded files for internal on-premise system
    
    Args:
    - medical_id (int): Medical facility ID
    - file_type (int): File type (1: Equipment, 2: Rental, 3: Failure)
    - X-System-Key (header): System authentication key
    
    Returns:
    - FileResponse: Target file
    """
    try:
        logger.info(f"システムファイル取得開始: 医療機関ID={medical_id}, ファイル種別={file_type}")
        
        # ファイル種別バリデーション
        if file_type not in [1, 2, 3]:
            raise HTTPException(
                status_code=400,
                detail="ファイル種別（file_type）は1-3の値のみ有効です（1: 医療機器台帳, 2: 貸出履歴, 3: 故障履歴）"
            )
        
        # 医療機関の存在チェック
        medical_facility = db.query(MstMedicalFacility).filter(
            MstMedicalFacility.medical_id == medical_id
        ).first()
        if not medical_facility:
            raise HTTPException(
                status_code=404,
                detail=f"医療機関ID {medical_id} は存在しません"
            )
        
        # ファイルパス取得
        file_path = get_upload_file_path(medical_id, file_type)
        
        # ファイル存在チェック
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"指定されたファイルが存在しません: 医療機関ID={medical_id}, ファイル種別={file_type}"
            )
        
        # DB履歴レコード取得（最新のアップロードレコード）
        latest_upload = db.query(FacilityUploadLog).filter(
            FacilityUploadLog.medical_id == medical_id,
            FacilityUploadLog.file_type == file_type
        ).order_by(FacilityUploadLog.upload_datetime.desc()).first()
        
        if latest_upload:
            # ダウンロード日時を更新
            download_time = datetime.now()
            latest_upload.download_datetime = download_time
            latest_upload.update_user_id = 0  # システム用アクセスのため
            latest_upload.lastupdate = download_time
            db.commit()
            
            logger.info(f"ダウンロード日時更新: uploadlog_id={latest_upload.uploadlog_id}, download_datetime={download_time}")
        else:
            logger.warning(f"対応するアップロードレコードが見つかりません: 医療機関ID={medical_id}, ファイル種別={file_type}")
        
        # ファイル名とMIMEタイプ設定
        file_names = {1: "equipment.csv", 2: "rental.csv", 3: "failure.csv"}
        filename = file_names[file_type]
        
        logger.info(f"システムファイル取得完了: {filename}")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="text/csv"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"システムファイル取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# システム管理者用エンドポイント
@router.post("/reports/publish/{medical_id}", response_model=MonthlyReportPublishResponse)
async def publish_monthly_reports(
    medical_id: int,
    publication_ym: str = Form(..., description="公開年月（YYYY-MM形式）"),
    system_key: str = Depends(verify_system_key),
    db: Session = Depends(get_db)
):
    """
    Publish Monthly Reports (System Only)

    [Japanese]
    月次レポート一括公開（システム管理者用）

    - システム側で生成されたレポートを一括公開します
    - 公開完了時に通知メールを送信します
    - システム認証キーが必要（一般ユーザーからのアクセス制限）

    Args:
    - medical_id (int): 医療機関ID
    - publication_ym (str): 公開年月（YYYY-MM形式）
    - X-System-Key (header): システム認証キー

    Returns:
    - MonthlyReportPublishResponse: 公開結果

    [English]
    Publish monthly reports (System use only)

    Args:
    - medical_id (int): Medical facility ID
    - publication_ym (str): Publication month (YYYY-MM format)  
    - X-System-Key (header): System authentication key

    Returns:
    - MonthlyReportPublishResponse: Publication result
    """
    try:
        logger.info(f"月次レポート公開開始: 医療機関ID={medical_id}, 公開年月={publication_ym}")
        
        # 医療機関の存在チェック
        medical_facility = db.query(MstMedicalFacility).filter(
            MstMedicalFacility.medical_id == medical_id
        ).first()
        if not medical_facility:
            raise HTTPException(
                status_code=404,
                detail=f"医療機関ID {medical_id} は存在しません"
            )
        
        # 公開年月フォーマットチェック
        if not publication_ym or len(publication_ym) != 7 or publication_ym[4] != "-":
            raise HTTPException(
                status_code=400,
                detail="公開年月は YYYY-MM 形式で指定してください"
            )
        
        # オンプレミスレポートをコピー
        copied_files = copy_onpremise_reports_to_publication(medical_id, publication_ym)
        if not copied_files:
            raise HTTPException(
                status_code=404,
                detail=f"オンプレミスレポートが見つかりません: 医療機関ID={medical_id}, 年月={publication_ym}"
            )
        
        # DB履歴記録
        published_records = []
        publication_datetime = datetime.now()
        
        # 各コピーされたファイルについてレコード作成
        for filename in copied_files:
            # ファイル種別を推定（簡易実装）
            if filename.lower().endswith('.pptx') or filename.lower().endswith('.pdf'):
                file_type = 1  # 分析レポート
            elif 'failure' in filename.lower() or '故障' in filename:
                file_type = 2  # 故障リスト
            else:
                file_type = 3  # 未実績リスト（その他）
            
            db_record = ReportPublicationLog(
                medical_id=medical_id,
                file_type=file_type,
                file_name=filename,
                publication_ym=publication_ym,
                upload_datetime=publication_datetime,  # publication_datetimeではなくupload_datetime
                download_user_id=0,  # システム公開のため0
                reg_user_id=0,  # システム公開のため0
                regdate=publication_datetime,
                update_user_id=0,  # システム公開のため0
                lastupdate=publication_datetime
            )
            db.add(db_record)
            db.commit()
            db.refresh(db_record)
            published_records.append(db_record)
            
            logger.info(f"レポート公開記録作成: {filename} (ファイル種別={file_type})")
        
        # 通知メール送信
        notification_sent = await send_notification_email(
            medical_id, "report_published", publication_ym
        )
        
        logger.info(f"月次レポート公開完了: 医療機関ID={medical_id}, {len(published_records)}件公開")
        
        return MonthlyReportPublishResponse(
            medical_id=medical_id,
            publication_ym=publication_ym,
            publish_datetime=publication_datetime.isoformat(),
            published_reports=[ReportPublication(
                medical_id=record.medical_id,
                publication_ym=record.publication_ym,
                file_type=record.file_type,
                file_name=record.file_name,
                download_user_id=record.download_user_id,
                publication_id=record.publication_id,
                upload_datetime=record.upload_datetime,
                download_datetime=record.download_datetime,
                regdate=record.regdate,
                lastupdate=record.lastupdate
            ) for record in published_records],
            notification_sent=notification_sent
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"月次レポート公開エラー: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")