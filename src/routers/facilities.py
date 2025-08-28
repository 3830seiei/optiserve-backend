"""routers/facilities.py

医療機関関連のAPIエンドポイント定義

Note:
    - 本モジュールは、医療機関情報の取得、登録、更新などのAPIエンドポイントを定義しています。
    - 医療機関の削除機能は意図的に提供されていません。
    - FastAPIを使用しており、SQLAlchemy ORMを介してPostgreSQLデータベースと連携します。
    - 各エンドポイントは、Pydanticモデルを使用してリクエストとレスポンスのバリデーションを行います。

ChangeLog:
    v1.0.0 (2025-08-07)
    - 初版作成
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List
from ..database import SessionLocal
from ..models.pg_optigate.mst_medical_facility import MstMedicalFacility
from ..schemas.mst_medical_facility import MedicalFacility, MedicalFacilityCreate
from ..utils.auth import AuthManager
import logging

router = APIRouter(
    prefix="/api/v1/facilities",
    tags=["facilities"],
)

# 標準ロガーの取得
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[MedicalFacility])
def read_facilities(
    skip: int = 0,
    limit: int = 100,
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)):
    """
    Read Medical Facilities

    [Japanese]\n
    医療機関マスタ一覧取得

    - 全ての医療機関情報を取得します
    - skipとlimitパラメータでページネーション可能です
    - 1〜100件までの範囲で取得件数を指定できます

    例:
    - /facilities ← 全件取得（最大100件）
    - /facilities?skip=0&limit=50 ← 最初の50件
    - /facilities?skip=50&limit=50 ← 次の50件

    Args:
    - skip (int, optional): スキップ件数（デフォルトは0）
    - limit (int, optional): 取得件数（デフォルトは100、最大100件）
    - db (Session, optional): SQLAlchemyのDBセッション。デフォルトは依存関係で取得

    Returns:
    - List[MedicalFacility]: 医療機関情報のリスト

    [English]\n
    Retrieve medical facility list

    - Retrieves all medical facility information
    - Supports pagination with skip and limit parameters
    - Can specify the number of records to retrieve within the range of 1-100

    Examples:
    - /facilities ← Retrieve all records (maximum 100 records)
    - /facilities?skip=0&limit=50 ← First 50 records
    - /facilities?skip=50&limit=50 ← Next 50 records

    Args:
    - skip (int, optional): Number of records to skip (default is 0)
    - limit (int, optional): Number of records to retrieve (default is 100, maximum 100 records)
    - db (Session, optional): SQLAlchemy database session, obtained via dependency injection

    Returns:
    - List[MedicalFacility]: List of medical facility information
    """
    # 医療機関アクセス権限に基づいてフィルタリング
    query = db.query(MstMedicalFacility)
    filtered_query = AuthManager.filter_by_medical_permission(
        query, current_user_id, db, MstMedicalFacility.medical_id
    )
    return filtered_query.offset(skip).limit(limit).all()

@router.get("/{facility_id}", response_model=MedicalFacility)
def read_facility(
    facility_id: int,
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)):
    """
    Read Medical Facility by ID

    [Japanese]\n
    医療機関マスタ個別取得

    - 医療機関IDで指定された医療機関情報を取得します
    - 医療機関が存在しない場合は404エラーを返します

    Args:
    - facility_id (int): 医療機関ID
    - db (Session, optional): SQLAlchemyのDBセッション。デフォルトは依存関係で取得

    Returns:
    - MedicalFacility: 医療機関情報

    [English]\n
    Retrieve medical facility by ID

    - Retrieves medical facility information specified by facility ID
    - Returns 404 error if the medical facility does not exist

    Args:
    - facility_id (int): Medical facility ID
    - db (Session, optional): SQLAlchemy database session, obtained via dependency injection

    Returns:
    - MedicalFacility: Medical facility information
    """
    # 医療機関アクセス権限チェック
    AuthManager.require_medical_permission(current_user_id, facility_id, db)
    
    facility = db.query(MstMedicalFacility).filter(MstMedicalFacility.medical_id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail="Medical facility not found")
    return facility

@router.post("/", response_model=MedicalFacility)
def create_facility(
    facility: MedicalFacilityCreate,
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)):
    """
    Create a new medical facility

    [Japanese]\n
    医療機関マスタ新規登録

    - 新しい医療機関情報を登録します（管理者権限が必要）
    - 登録時にシステム日時が自動で設定されます
    - エラーが発生した場合は自動でrollbackされます

    Args:
    - facility (MedicalFacilityCreate): 新規登録する医療機関情報
    - db (Session, optional): SQLAlchemyのDBセッション。デフォルトは依存関係で取得

    Returns:
    - MedicalFacility: 登録された医療機関情報

    [English]\n
    Create a new medical facility

    - Registers new medical facility information (requires admin privileges)
    - System datetime is automatically set during registration
    - Automatically rolls back if an error occurs

    Args:
    - facility (MedicalFacilityCreate): Medical facility information to register
    - db (Session, optional): SQLAlchemy database session, obtained via dependency injection

    Returns:
    - MedicalFacility: Registered medical facility information
    """
    try:
        # 管理者権限チェック
        AuthManager.require_admin_permission(current_user_id, db)
        
        logger.info(f"医療機関作成開始: {facility.medical_name}")

        # リクエストデータのログ出力
        facility_data = facility.model_dump()
        logger.debug(f"リクエストデータ: {facility_data}")

        # DBオブジェクト作成
        logger.debug("DBオブジェクト作成開始")
        now = datetime.now()
        db_facility = MstMedicalFacility(
            medical_name=facility_data.get("medical_name"),
            address_postal_code=facility_data.get("address_postal_code"),
            address_prefecture=facility_data.get("address_prefecture"),
            address_city=facility_data.get("address_city"),
            address_line1=facility_data.get("address_line1"),
            address_line2=facility_data.get("address_line2"),
            phone_number=facility_data.get("phone_number"),
            reg_user_id=current_user_id,
            regdate=now,
            update_user_id=current_user_id,
            lastupdate=now
        )
        logger.debug("DBオブジェクト作成完了")

        # DB保存処理
        logger.debug("DB保存処理開始")
        db.add(db_facility)
        db.commit()
        logger.debug("DB保存処理完了")

        db.refresh(db_facility)
        logger.info(f"医療機関作成完了: ID={db_facility.medical_id}")

        return db_facility

    except Exception as e:
        logger.error(f"医療機関作成エラー: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/{facility_id}", response_model=MedicalFacility)
def update_facility(
    facility_id: int,
    facility: MedicalFacilityCreate,
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)):
    """
    Update an existing medical facility

    [Japanese]\n
    既存医療機関マスタ情報更新

    - 医療機関IDで指定された医療機関情報を更新します（管理者権限が必要）
    - 更新時にlastupdateが自動で現在時刻に設定されます
    - 医療機関が存在しない場合は404エラーを返します

    Args:
    - facility_id (int): 医療機関ID
    - facility (MedicalFacilityCreate): 更新する医療機関情報
    - db (Session, optional): SQLAlchemyのDBセッション。デフォルトは依存関係で取得

    Returns:
    - MedicalFacility: 更新された医療機関情報

    [English]\n
    Update an existing medical facility

    - Updates medical facility information specified by facility ID (requires admin privileges)
    - lastupdate is automatically set to current time during update
    - Returns 404 error if the medical facility does not exist

    Args:
    - facility_id (int): Medical facility ID
    - facility (MedicalFacilityCreate): Medical facility information to update
    - db (Session, optional): SQLAlchemy database session, obtained via dependency injection

    Returns:
    - MedicalFacility: Updated medical facility information
    """
    # 管理者権限チェック
    AuthManager.require_admin_permission(current_user_id, db)
    
    db_facility = db.query(MstMedicalFacility).filter(MstMedicalFacility.medical_id == facility_id).first()
    if not db_facility:
        raise HTTPException(status_code=404, detail="Medical facility not found")
    for field, value in facility.model_dump().items():
        setattr(db_facility, field, value)
    # システム日時と更新ユーザーIDをセット
    db_facility.update_user_id = current_user_id
    db_facility.lastupdate = datetime.now()
    db.commit()
    db.refresh(db_facility)
    return db_facility

# 医療機関マスタの削除は機能としては存在させないため、コメントアウトしています。
#@router.delete("/{facility_id}")
#def delete_facility(facility_id: int, db: Session = Depends(get_db)):
#    """
#    医療機関マスタ削除
#    """
#    db_facility = db.query(MstMedicalFacility).filter(MstMedicalFacility.medical_facility_id == facility_id).first()
#    if not db_facility:
#        raise HTTPException(status_code=404, detail="Medical facility not found")
#    db.delete(db_facility)
#    db.commit()
#    return {"result": "ok"}
