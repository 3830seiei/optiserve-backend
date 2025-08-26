"""routers/medical_equipment_analysis.py

医療機器分析設定に関するAPIエンドポイント定義

Note:
    - 本モジュールは、機器ごとの分析対象フラグと分類上書き設定を管理するAPIエンドポイントを定義しています。
    - 機器台帳（medical_equipment_ledger）のデフォルト設定に対する上書き情報を医療機関単位で管理します。
    - デフォルト値と同じ設定は保存せず、差分のみを管理することでデータ効率を向上させています。
    - 各設定には変更履歴（note）が記録され、変更理由と実施者を追跡可能です。
    - FastAPIを使用しており、SQLAlchemy ORMを介してSQLiteデータベース（本番ではPostgreSQL）と連携します。

ChangeLog:
    v1.0.0 (2025-08-14)
    - 初版作成
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Header
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from ..database import get_db
from ..utils.auth import AuthManager
from ..schemas.medical_equipment_analysis import (
    MedicalEquipmentAnalysisResponse,
    MedicalEquipmentAnalysisListResponse,
    MedicalEquipmentAnalysisQuery,
    AnalysisTargetUpdateRequest,
    AnalysisTargetUpdateResponse,
    ClassificationOverrideUpdateRequest,
    ClassificationOverrideUpdateResponse,
    DefaultRestoreResponse,
    ValidationErrorResponse,
    NoteHistoryItem
)
from ..models.pg_optigate.medical_equipment_ledger import MedicalEquipmentLedger
from ..models.pg_optigate.medical_equipment_analysis_setting import MedicalEquipmentAnalysisSetting
from ..models.pg_optigate.mst_equipment_classification import MstEquipmentClassification

router = APIRouter(prefix="/api/v1/medical-equipment-analysis-settings", tags=["equipment-analysis-overrides"])






def create_note_history_item(user_id: str, note: str) -> Dict[str, Any]:
    """履歴アイテムを作成"""
    return {
        "user_id": user_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "note": note
    }


def append_note_history(existing_note: str, new_item: Dict[str, Any]) -> str:
    """既存の履歴に新しいアイテムを追加"""
    try:
        history = json.loads(existing_note) if existing_note else []
    except (json.JSONDecodeError, TypeError):
        history = []
    
    history.append(new_item)
    return json.dumps(history, ensure_ascii=False)


def parse_note_history(note_json: str) -> List[NoteHistoryItem]:
    """JSON形式の履歴をパース"""
    try:
        if not note_json:
            return []
        history_data = json.loads(note_json)
        return [NoteHistoryItem(**item) for item in history_data]
    except (json.JSONDecodeError, TypeError, ValueError):
        return []


@router.get("", response_model=MedicalEquipmentAnalysisListResponse)
async def get_medical_equipment_analysis_settings(
    medical_id: Optional[int] = Query(None, description="医療機関ID（省略時は認証ユーザーの医療機関）"),
    classification_id: Optional[int] = Query(None, description="分類IDでフィルタ"),
    skip: int = Query(0, ge=0, description="スキップ件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得件数"),
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)
):
    """
    Get Medical Equipment Analysis Settings

    [Japanese]\n
    医療機器分析設定一覧を取得

    機器台帳のデフォルト設定と上書き設定を統合した現在有効な設定情報を取得します。
    分析対象フラグと分類上書きの両方の情報を含みます。

    検索例:
    - /medical-equipment-analysis-settings ← 認証ユーザーの医療機関の全件取得
    - /medical-equipment-analysis-settings?medical_id=5 ← 指定医療機関の全件取得
    - /medical-equipment-analysis-settings?classification_id=123 ← 指定分類でフィルタ

    ページング:
    - 001～100件 : ?skip=0&limit=100
    - 101～200件 : ?skip=100&limit=100
    - 201～300件 : ?skip=200&limit=100

    Args:
    - medical_id (int, optional): 医療機関ID（省略時は認証ユーザーの医療機関）
    - classification_id (int, optional): 分類IDでフィルタ（デフォルト分類または上書き分類）
    - skip (int, optional): スキップ件数（デフォルトは0）
    - limit (int, optional): 取得件数（デフォルトは100、最大1000件）

    Returns:
    - MedicalEquipmentAnalysisListResponse: 機器分析設定一覧と総件数、次ページ有無

    [English]\n
    Retrieve medical equipment analysis settings list

    Get currently effective settings that integrate default settings from equipment ledger 
    and override settings. Includes both analysis target flags and classification overrides.

    Search examples:
    - /medical-equipment-analysis-settings ← All records for authenticated user's medical facility
    - /medical-equipment-analysis-settings?medical_id=5 ← All records for specified medical facility
    - /medical-equipment-analysis-settings?classification_id=123 ← Filter by classification

    Pagination:
    - Records 001-100: ?skip=0&limit=100
    - Records 101-200: ?skip=100&limit=100
    - Records 201-300: ?skip=200&limit=100

    Args:
    - medical_id (int, optional): Medical facility ID (defaults to authenticated user's facility)
    - classification_id (int, optional): Filter by classification ID (default or override classification)
    - skip (int, optional): Number of records to skip (default: 0)
    - limit (int, optional): Number of records to retrieve (default: 100, max: 1000)

    Returns:
    - MedicalEquipmentAnalysisListResponse: List of equipment analysis settings with total count and next page flag
    """
    try:
        # 医療機関IDの決定
        if medical_id:
            # 指定された医療機関IDへのアクセス権限チェック
            AuthManager.require_medical_permission(current_user_id, medical_id, db)
            target_medical_id = medical_id
        else:
            # 認証ユーザーの医療機関IDを取得
            target_medical_id = AuthManager.get_user_medical_id(current_user_id, db)
            if target_medical_id is None:
                raise HTTPException(status_code=403, detail="医療機関ユーザーまたはシステム管理者である必要があります")
        
        # ベースクエリ構築
        base_query = db.query(
            MedicalEquipmentLedger,
            MedicalEquipmentAnalysisSetting,
            MstEquipmentClassification
        ).outerjoin(
            MedicalEquipmentAnalysisSetting,
            MedicalEquipmentLedger.ledger_id == MedicalEquipmentAnalysisSetting.ledger_id
        ).outerjoin(
            MstEquipmentClassification,
            MedicalEquipmentLedger.classification_id == MstEquipmentClassification.classification_id
        ).filter(
            MedicalEquipmentLedger.medical_id == target_medical_id
        )
        
        # 分類IDフィルタ
        if classification_id:
            base_query = base_query.filter(
                or_(
                    MedicalEquipmentLedger.classification_id == classification_id,
                    MedicalEquipmentAnalysisSetting.override_classification_id == classification_id
                )
            )
        
        # 総件数取得
        total_count = base_query.count()
        
        # データ取得（ページング適用）
        results = base_query.offset(skip).limit(limit).all()
        
        # レスポンス構築
        items = []
        for ledger, analysis_setting, classification in results:
            # 有効な値を決定
            effective_is_included = (
                analysis_setting.override_is_included 
                if analysis_setting else ledger.is_included
            )
            effective_classification_id = (
                analysis_setting.override_classification_id 
                if analysis_setting and analysis_setting.override_classification_id else ledger.classification_id
            )
            
            # 分類情報取得
            if effective_classification_id and effective_classification_id != ledger.classification_id:
                # 上書き分類の情報を取得
                override_classification = db.query(MstEquipmentClassification).filter(
                    MstEquipmentClassification.classification_id == effective_classification_id
                ).first()
                classification = override_classification if override_classification else classification
            
            item = MedicalEquipmentAnalysisResponse(
                # 機器台帳情報
                ledger_id=ledger.ledger_id,
                medical_id=ledger.medical_id,
                model_number=ledger.model_number,
                product_name=ledger.product_name,
                maker_name=ledger.maker_name,
                stock_quantity=ledger.stock_quantity,
                
                # デフォルト値
                default_is_included=ledger.is_included,
                default_classification_id=ledger.classification_id,
                
                # 有効値
                effective_is_included=effective_is_included,
                effective_classification_id=effective_classification_id,
                
                # 上書き設定
                has_override=analysis_setting is not None,
                override_is_included=analysis_setting.override_is_included if analysis_setting else None,
                override_classification_id=analysis_setting.override_classification_id if analysis_setting else None,
                
                # 分類情報
                classification_name=classification.classification_name if classification else None,
                classification_level=classification.classification_level if classification else None,
                
                # 履歴情報
                note_history=parse_note_history(analysis_setting.note if analysis_setting else ""),
                last_modified=analysis_setting.lastupdate if analysis_setting else None,
                last_modified_user_id=analysis_setting.update_user_id if analysis_setting else None
            )
            items.append(item)
        
        return MedicalEquipmentAnalysisListResponse(
            items=items,
            total_count=total_count,
            has_next=(skip + limit) < total_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データ取得エラー: {str(e)}")


@router.put("/{ledger_id}/analysis-target", response_model=AnalysisTargetUpdateResponse)
async def update_analysis_target(
    ledger_id: int = Path(..., description="機器台帳ID"),
    request: AnalysisTargetUpdateRequest = ...,
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)
):
    """
    Update Analysis Target Flag

    [Japanese]\n
    機器の分析対象フラグを更新

    機器台帳のデフォルト分析対象フラグを上書きします。
    デフォルト値と同じ値は設定できません（差分管理）。
    変更履歴が記録され、理由と実施者が追跡可能です。

    利用例:
    - PUT /medical-equipment-analysis-settings/123/analysis-target
    - Body: {"override_is_included": true, "note": "重要機器のため分析対象に追加"}

    Args:
    - ledger_id (int): 機器台帳ID
    - request (AnalysisTargetUpdateRequest): 更新リクエスト
      - override_is_included (bool): 上書きする分析対象フラグ
      - note (str): 変更理由・補足情報（必須、最大500文字）

    Returns:
    - AnalysisTargetUpdateResponse: 更新結果

    Raises:
    - 400: デフォルト値と同じ値を設定しようとした場合
    - 404: 指定された機器が存在しない場合

    [English]\n
    Update analysis target flag for equipment

    Override the default analysis target flag from equipment ledger.
    Cannot set the same value as default (differential management).
    Change history is recorded with reason and user tracking.

    Usage example:
    - PUT /medical-equipment-analysis-settings/123/analysis-target
    - Body: {"override_is_included": true, "note": "Added to analysis due to critical equipment"}

    Args:
    - ledger_id (int): Equipment ledger ID
    - request (AnalysisTargetUpdateRequest): Update request
      - override_is_included (bool): Analysis target flag to override
      - note (str): Reason for change/additional information (required, max 500 chars)

    Returns:
    - AnalysisTargetUpdateResponse: Update result

    Raises:
    - 400: When trying to set the same value as default
    - 404: When specified equipment does not exist
    """
    try:
        # current_user_idはパラメータで受け取り済み
        
        # 機器台帳の存在確認
        ledger = db.query(MedicalEquipmentLedger).filter(
            MedicalEquipmentLedger.ledger_id == ledger_id
        ).first()
        
        if not ledger:
            raise HTTPException(status_code=404, detail="指定された機器が見つかりません")
        
        # デフォルト値との比較
        if request.override_is_included == ledger.is_included:
            raise HTTPException(
                status_code=400, 
                detail=f"デフォルト値（{ledger.is_included}）と同じ値は設定できません。デフォルト値を使用する場合は設定を削除してください。"
            )
        
        # 既存設定の確認
        analysis_setting = db.query(MedicalEquipmentAnalysisSetting).filter(
            MedicalEquipmentAnalysisSetting.ledger_id == ledger_id
        ).first()
        
        current_time = datetime.now()
        note_item = create_note_history_item(current_user_id, request.note)
        
        if analysis_setting:
            # 既存設定を更新
            analysis_setting.override_is_included = request.override_is_included
            analysis_setting.note = append_note_history(analysis_setting.note, note_item)
            analysis_setting.update_user_id = current_user_id
            analysis_setting.lastupdate = current_time
        else:
            # 新規設定を作成
            analysis_setting = MedicalEquipmentAnalysisSetting(
                ledger_id=ledger_id,
                override_is_included=request.override_is_included,
                override_classification_id=None,
                note=json.dumps([note_item], ensure_ascii=False),
                reg_user_id=current_user_id,
                regdate=current_time,
                update_user_id=current_user_id,
                lastupdate=current_time
            )
            db.add(analysis_setting)
        
        db.commit()
        
        return AnalysisTargetUpdateResponse(
            ledger_id=ledger_id,
            override_is_included=request.override_is_included,
            effective_is_included=request.override_is_included,
            updated_at=current_time,
            message="分析対象フラグを更新しました"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新エラー: {str(e)}")


@router.put("/{ledger_id}/classification", response_model=ClassificationOverrideUpdateResponse)
async def update_classification_override(
    ledger_id: int = Path(..., description="機器台帳ID"),
    request: ClassificationOverrideUpdateRequest = ...,
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)
):
    """
    Update Classification Override

    [Japanese]\n
    機器の分類上書きを更新

    機器台帳のデフォルト分類を別の分類に上書きします。
    医療機関独自のルールで機器を別分類として分析したい場合に使用します。
    デフォルト値と同じ分類IDは設定できません（差分管理）。

    利用例:
    - PUT /medical-equipment-analysis-settings/123/classification
    - Body: {"override_classification_id": 456, "note": "院内ルールにより呼吸器分類に変更"}

    Args:
    - ledger_id (int): 機器台帳ID
    - request (ClassificationOverrideUpdateRequest): 更新リクエスト
      - override_classification_id (int): 上書きする分類ID
      - note (str): 変更理由・補足情報（必須、最大500文字）

    Returns:
    - ClassificationOverrideUpdateResponse: 更新結果（分類名含む）

    Raises:
    - 400: デフォルト値と同じ分類IDを設定しようとした場合、または存在しない分類IDを指定した場合
    - 404: 指定された機器が存在しない場合

    [English]\n
    Update classification override for equipment

    Override the default classification from equipment ledger with a different classification.
    Used when medical facilities want to analyze equipment under different classifications 
    according to their internal rules. Cannot set the same classification ID as default.

    Usage example:
    - PUT /medical-equipment-analysis-settings/123/classification
    - Body: {"override_classification_id": 456, "note": "Changed to respiratory classification per hospital rules"}

    Args:
    - ledger_id (int): Equipment ledger ID
    - request (ClassificationOverrideUpdateRequest): Update request
      - override_classification_id (int): Classification ID to override
      - note (str): Reason for change/additional information (required, max 500 chars)

    Returns:
    - ClassificationOverrideUpdateResponse: Update result (including classification name)

    Raises:
    - 400: When trying to set same classification ID as default, or invalid classification ID
    - 404: When specified equipment does not exist
    """
    try:
        # current_user_idはパラメータで受け取り済み
        
        # 機器台帳の存在確認
        ledger = db.query(MedicalEquipmentLedger).filter(
            MedicalEquipmentLedger.ledger_id == ledger_id
        ).first()
        
        if not ledger:
            raise HTTPException(status_code=404, detail="指定された機器が見つかりません")
        
        # デフォルト値との比較
        if request.override_classification_id == ledger.classification_id:
            raise HTTPException(
                status_code=400,
                detail=f"デフォルト値（{ledger.classification_id}）と同じ分類は設定できません。デフォルト値を使用する場合は設定を削除してください。"
            )
        
        # 指定された分類の存在確認
        target_classification = db.query(MstEquipmentClassification).filter(
            MstEquipmentClassification.classification_id == request.override_classification_id
        ).first()
        
        if not target_classification:
            raise HTTPException(status_code=400, detail="指定された分類IDが存在しません")
        
        # 既存設定の確認
        analysis_setting = db.query(MedicalEquipmentAnalysisSetting).filter(
            MedicalEquipmentAnalysisSetting.ledger_id == ledger_id
        ).first()
        
        current_time = datetime.now()
        note_item = create_note_history_item(current_user_id, request.note)
        
        if analysis_setting:
            # 既存設定を更新
            analysis_setting.override_classification_id = request.override_classification_id
            analysis_setting.note = append_note_history(analysis_setting.note, note_item)
            analysis_setting.update_user_id = current_user_id
            analysis_setting.lastupdate = current_time
        else:
            # 新規設定を作成
            analysis_setting = MedicalEquipmentAnalysisSetting(
                ledger_id=ledger_id,
                override_is_included=True,  # デフォルト値
                override_classification_id=request.override_classification_id,
                note=json.dumps([note_item], ensure_ascii=False),
                reg_user_id=current_user_id,
                regdate=current_time,
                update_user_id=current_user_id,
                lastupdate=current_time
            )
            db.add(analysis_setting)
        
        db.commit()
        
        return ClassificationOverrideUpdateResponse(
            ledger_id=ledger_id,
            override_classification_id=request.override_classification_id,
            effective_classification_id=request.override_classification_id,
            classification_name=target_classification.classification_name,
            updated_at=current_time,
            message="分類上書きを更新しました"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新エラー: {str(e)}")


@router.delete("", response_model=DefaultRestoreResponse)
async def restore_to_default_all(
    medical_id: int = Query(..., description="医療機関ID"),
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)
):
    """
    Restore All Settings to Default

    [Japanese]\n
    指定医療機関の全設定をデフォルトに復帰

    該当医療機関のすべての上書き設定（分析対象フラグ・分類上書き）を削除し、
    機器台帳のデフォルト設定に戻します。
    設定の変更履歴も完全に削除されます。

    利用例:
    - DELETE /medical-equipment-analysis-settings?medical_id=5

    Args:
    - medical_id (int): 医療機関ID

    Returns:
    - DefaultRestoreResponse: 復帰結果（削除件数、対象機器IDリスト）

    注意:
    - この操作は取り消せません
    - 該当医療機関のすべての上書き設定が削除されます
    - 変更履歴も完全に削除されます

    [English]\n
    Restore all settings to default for specified medical facility

    Delete all override settings (analysis target flags and classification overrides) 
    for the medical facility and revert to default settings from equipment ledger.
    Change history will also be completely deleted.

    Usage example:
    - DELETE /medical-equipment-analysis-settings?medical_id=5

    Args:
    - medical_id (int): Medical facility ID

    Returns:
    - DefaultRestoreResponse: Restore result (deletion count, affected equipment IDs)

    Warning:
    - This operation cannot be undone
    - All override settings for the medical facility will be deleted
    - Change history will also be completely deleted
    """
    try:
        # 指定された医療機関IDへのアクセス権限チェック
        AuthManager.require_medical_permission(current_user_id, medical_id, db)
        
        # 該当する設定を取得
        settings_to_delete = db.query(MedicalEquipmentAnalysisSetting).join(
            MedicalEquipmentLedger,
            MedicalEquipmentAnalysisSetting.ledger_id == MedicalEquipmentLedger.ledger_id
        ).filter(
            MedicalEquipmentLedger.medical_id == medical_id
        ).all()
        
        ledger_ids = [setting.ledger_id for setting in settings_to_delete]
        affected_count = len(settings_to_delete)
        
        # 設定を削除
        for setting in settings_to_delete:
            db.delete(setting)
        
        db.commit()
        
        return DefaultRestoreResponse(
            affected_count=affected_count,
            ledger_ids=ledger_ids,
            message=f"医療機関ID {medical_id} の {affected_count} 件の設定をデフォルトに復帰しました"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"復帰処理エラー: {str(e)}")


@router.delete("/{ledger_id}", response_model=DefaultRestoreResponse)
async def restore_to_default_single(
    ledger_id: int = Path(..., description="機器台帳ID"),
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)
):
    """
    Restore Single Equipment Setting to Default

    [Japanese]\n
    指定された機器の設定をデフォルトに復帰

    指定機器の上書き設定（分析対象フラグ・分類上書き）を削除し、
    機器台帳のデフォルト設定に戻します。
    該当機器の変更履歴も完全に削除されます。

    利用例:
    - DELETE /medical-equipment-analysis-settings/123

    Args:
    - ledger_id (int): 機器台帳ID

    Returns:
    - DefaultRestoreResponse: 復帰結果（削除件数=1、対象機器ID）

    Raises:
    - 404: 指定された機器が存在しない場合、または上書き設定が存在しない場合

    注意:
    - この操作は取り消せません
    - 該当機器の変更履歴も完全に削除されます

    [English]\n
    Restore single equipment setting to default

    Delete override settings (analysis target flag and classification override) 
    for specified equipment and revert to default settings from equipment ledger.
    Change history for the equipment will also be completely deleted.

    Usage example:
    - DELETE /medical-equipment-analysis-settings/123

    Args:
    - ledger_id (int): Equipment ledger ID

    Returns:
    - DefaultRestoreResponse: Restore result (deletion count=1, affected equipment ID)

    Raises:
    - 404: When specified equipment does not exist or has no override settings

    Warning:
    - This operation cannot be undone
    - Change history for the equipment will also be completely deleted
    """
    try:
        # 機器台帳の存在確認
        ledger = db.query(MedicalEquipmentLedger).filter(
            MedicalEquipmentLedger.ledger_id == ledger_id
        ).first()
        
        if not ledger:
            raise HTTPException(status_code=404, detail="指定された機器が見つかりません")
        
        # 設定の存在確認
        analysis_setting = db.query(MedicalEquipmentAnalysisSetting).filter(
            MedicalEquipmentAnalysisSetting.ledger_id == ledger_id
        ).first()
        
        if not analysis_setting:
            raise HTTPException(status_code=404, detail="該当機器に上書き設定が存在しません")
        
        # 設定を削除
        db.delete(analysis_setting)
        db.commit()
        
        return DefaultRestoreResponse(
            affected_count=1,
            ledger_ids=[ledger_id],
            message=f"機器ID {ledger_id} の設定をデフォルトに復帰しました"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"復帰処理エラー: {str(e)}")