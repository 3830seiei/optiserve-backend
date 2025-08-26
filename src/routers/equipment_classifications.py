"""routers/equipment_classifications.py

機器分類・レポート出力選択関連のAPIエンドポイント定義

Note:
    - 本モジュールは、機器分類マスタの照会とレポート出力用機器分類選択機能を提供します。
    - 医療機関向けのレポート作成時の機器分類選択をサポートします。
    - user_entity_link.count_reportout_classificationに基づく選択数制限を管理します。

ChangeLog:
    v1.0.0 (2025-08-08)
    - 初版作成
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session

from ..database import SessionLocal
from src.models.pg_optigate.mst_equipment_classification import MstEquipmentClassification
from src.models.pg_optigate.equipment_classification_report_selection import EquipmentClassificationReportSelection
from src.models.pg_optigate.mst_medical_facility import MstMedicalFacility
from src.models.pg_optigate.user_entity_link import UserEntityLink
from src.schemas.equipment_classification import (
    EquipmentClassification,
    EquipmentClassificationListResponse,
    ReportSelectionResponse,
    ReportSelectionRequest,
    ReportSelectionCreateResponse,
    ReportSelectionDeleteResponse,
    ReportSelectionItem
)
from ..utils.auth import AuthManager
import logging

router = APIRouter(
    prefix="/api/v1/equipment-classifications",
    tags=["equipment-classifications"],
)

# ロガー設定
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{medical_id}", response_model=EquipmentClassificationListResponse)
async def get_equipment_classifications(
    medical_id: int,
    skip: int = Query(0, ge=0, description="スキップ件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得件数（最大1000件）"),
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)
):
    """
    Get Equipment Classifications

    [Japanese]
    機器分類一覧取得

    - 指定医療機関の機器分類一覧を取得します
    - ページネーション対応（skip/limit）
    - 階層順序（level, parent_id, classification_name）でソートされます

    Args:
    - medical_id (int): 医療機関ID
    - skip (int, optional): スキップ件数（デフォルト0）
    - limit (int, optional): 取得件数（デフォルト100、最大1000）

    Returns:
    - EquipmentClassificationListResponse: 機器分類一覧レスポンス

    [English]
    Get equipment classifications for specified medical facility

    Args:
    - medical_id (int): Medical facility ID
    - skip (int, optional): Number of records to skip (default 0)
    - limit (int, optional): Number of records to retrieve (default 100, max 1000)

    Returns:
    - EquipmentClassificationListResponse: Equipment classification list response
    """
    try:
        # 医療機関アクセス権限チェック
        AuthManager.require_medical_permission(current_user_id, medical_id, db)
        
        logger.info(f"機器分類一覧取得開始: medical_id={medical_id}, skip={skip}, limit={limit}")
        
        # 医療機関の存在チェック
        medical_facility = db.query(MstMedicalFacility).filter(
            MstMedicalFacility.medical_id == medical_id
        ).first()
        if not medical_facility:
            raise HTTPException(
                status_code=404,
                detail=f"医療機関ID {medical_id} は存在しません"
            )
        
        # 総件数取得
        total = db.query(MstEquipmentClassification).filter(
            MstEquipmentClassification.medical_id == medical_id
        ).count()
        
        # 機器分類一覧取得（階層順序でソート）
        classifications = db.query(MstEquipmentClassification).filter(
            MstEquipmentClassification.medical_id == medical_id
        ).order_by(
            MstEquipmentClassification.classification_level,
            MstEquipmentClassification.parent_classification_id,
            MstEquipmentClassification.classification_name
        ).offset(skip).limit(limit).all()
        
        # レスポンス作成
        items = [EquipmentClassification.model_validate(c) for c in classifications]
        
        logger.info(f"機器分類一覧取得完了: total={total}, 取得件数={len(items)}")
        
        return EquipmentClassificationListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=items
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"機器分類一覧取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/report-selection/{medical_id}", response_model=ReportSelectionResponse)
async def get_report_selection(
    medical_id: int,
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)
):
    """
    Get Report Selection Configuration

    [Japanese]
    レポート出力用機器分類選択情報取得

    - 指定医療機関のレポート出力用機器分類選択情報を取得します
    - user_entity_link.count_reportout_classificationに基づく最大選択数を含みます
    - rank順でソートされます

    Args:
    - medical_id (int): 医療機関ID

    Returns:
    - ReportSelectionResponse: レポート選択情報レスポンス

    [English]
    Get report selection configuration for specified medical facility

    Args:
    - medical_id (int): Medical facility ID

    Returns:
    - ReportSelectionResponse: Report selection response
    """
    try:
        # 医療機関アクセス権限チェック
        AuthManager.require_medical_permission(current_user_id, medical_id, db)
        
        logger.info(f"レポート選択情報取得開始: medical_id={medical_id}")
        
        # 医療機関の存在チェック
        medical_facility = db.query(MstMedicalFacility).filter(
            MstMedicalFacility.medical_id == medical_id
        ).first()
        if not medical_facility:
            raise HTTPException(
                status_code=404,
                detail=f"医療機関ID {medical_id} は存在しません"
            )
        
        # 最大選択数取得
        user_entity_link = db.query(UserEntityLink).filter(
            UserEntityLink.entity_type == 1,
            UserEntityLink.entity_relation_id == medical_id
        ).first()
        
        max_count = user_entity_link.count_reportout_classification if user_entity_link else 5  # デフォルト5
        
        # レポート選択情報取得（rank順、最大数まで）
        selections_query = db.query(
            EquipmentClassificationReportSelection,
            MstEquipmentClassification.classification_name
        ).join(
            MstEquipmentClassification,
            EquipmentClassificationReportSelection.classification_id == MstEquipmentClassification.classification_id
        ).filter(
            EquipmentClassificationReportSelection.medical_id == medical_id
        ).order_by(
            EquipmentClassificationReportSelection.rank
        ).limit(max_count)
        
        selection_results = selections_query.all()
        
        # レスポンス作成
        selections = [
            ReportSelectionItem(
                rank=result[0].rank,
                classification_id=result[0].classification_id,
                classification_name=result[1]
            )
            for result in selection_results
        ]
        
        logger.info(f"レポート選択情報取得完了: medical_id={medical_id}, 選択数={len(selections)}, 最大数={max_count}, 選択内容={[s.classification_name for s in selections]}")
        
        return ReportSelectionResponse(
            medical_id=medical_id,
            max_count=max_count,
            selections=selections
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"レポート選択情報取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/report-selection/{medical_id}", response_model=ReportSelectionCreateResponse)
async def create_report_selection(
    medical_id: int,
    request: ReportSelectionRequest,
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)
):
    """
    Create Report Selection Configuration

    [Japanese]
    レポート出力用機器分類選択情報登録

    - 指定医療機関のレポート出力用機器分類選択情報を登録します
    - 既存の選択情報は削除され、新しい情報で置き換えられます
    - classification_ids の順序がrank順になります

    Args:
    - medical_id (int): 医療機関ID
    - request (ReportSelectionRequest): 登録リクエスト

    Returns:
    - ReportSelectionCreateResponse: 登録結果レスポンス

    [English]
    Create report selection configuration for specified medical facility

    Args:
    - medical_id (int): Medical facility ID
    - request (ReportSelectionRequest): Registration request

    Returns:
    - ReportSelectionCreateResponse: Registration result response
    """
    try:
        # 医療機関アクセス権限チェック
        AuthManager.require_medical_permission(current_user_id, medical_id, db)
        
        logger.info(f"レポート選択情報登録開始: medical_id={medical_id}, 分類数={len(request.classification_ids)}")
        
        # 医療機関の存在チェック
        medical_facility = db.query(MstMedicalFacility).filter(
            MstMedicalFacility.medical_id == medical_id
        ).first()
        if not medical_facility:
            raise HTTPException(
                status_code=404,
                detail=f"医療機関ID {medical_id} は存在しません"
            )
        
        # 機器分類IDの存在チェック
        existing_classifications = db.query(MstEquipmentClassification.classification_id).filter(
            MstEquipmentClassification.classification_id.in_(request.classification_ids),
            MstEquipmentClassification.medical_id == medical_id
        ).all()
        
        existing_ids = set(row[0] for row in existing_classifications)
        missing_ids = set(request.classification_ids) - existing_ids
        
        if missing_ids:
            raise HTTPException(
                status_code=400,
                detail=f"指定された機器分類IDが存在しません: {list(missing_ids)}"
            )
        
        # 既存の選択情報を削除
        deleted_count = db.query(EquipmentClassificationReportSelection).filter(
            EquipmentClassificationReportSelection.medical_id == medical_id
        ).delete(synchronize_session=False)
        
        # 新しい選択情報を登録
        current_time = datetime.now()
        created_records = []
        
        for rank, classification_id in enumerate(request.classification_ids, 1):
            record = EquipmentClassificationReportSelection(
                medical_id=medical_id,
                rank=rank,
                classification_id=classification_id,
                reg_user_id=current_user_id,
                regdate=current_time,
                update_user_id=current_user_id,
                lastupdate=current_time
            )
            db.add(record)
            created_records.append(record)
        
        db.commit()
        
        # レスポンス用に機器分類名を取得
        classification_names = db.query(
            MstEquipmentClassification.classification_id,
            MstEquipmentClassification.classification_name
        ).filter(
            MstEquipmentClassification.classification_id.in_(request.classification_ids)
        ).all()
        
        name_map = {row[0]: row[1] for row in classification_names}
        
        selections = [
            ReportSelectionItem(
                rank=record.rank,
                classification_id=record.classification_id,
                classification_name=name_map[record.classification_id]
            )
            for record in created_records
        ]
        
        logger.info(f"レポート選択情報登録完了: medical_id={medical_id}, 削除数={deleted_count}, 作成数={len(created_records)}")
        
        return ReportSelectionCreateResponse(
            medical_id=medical_id,
            created_count=len(created_records),
            selections=selections
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"レポート選択情報登録エラー: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/report-selection/{medical_id}", response_model=ReportSelectionDeleteResponse)
async def delete_report_selection(
    medical_id: int,
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)
):
    """
    Delete Report Selection Configuration

    [Japanese]
    レポート出力用機器分類選択情報削除

    - 指定医療機関のレポート出力用機器分類選択情報を全て削除します
    - テーブルから実際にレコードを削除します

    Args:
    - medical_id (int): 医療機関ID

    Returns:
    - ReportSelectionDeleteResponse: 削除結果レスポンス

    [English]
    Delete report selection configuration for specified medical facility

    Args:
    - medical_id (int): Medical facility ID

    Returns:
    - ReportSelectionDeleteResponse: Deletion result response
    """
    try:
        # 医療機関アクセス権限チェック
        AuthManager.require_medical_permission(current_user_id, medical_id, db)
        
        logger.info(f"レポート選択情報削除開始: medical_id={medical_id}")
        
        # 医療機関の存在チェック
        medical_facility = db.query(MstMedicalFacility).filter(
            MstMedicalFacility.medical_id == medical_id
        ).first()
        if not medical_facility:
            raise HTTPException(
                status_code=404,
                detail=f"医療機関ID {medical_id} は存在しません"
            )
        
        # 選択情報を削除
        deleted_count = db.query(EquipmentClassificationReportSelection).filter(
            EquipmentClassificationReportSelection.medical_id == medical_id
        ).delete(synchronize_session=False)
        
        db.commit()
        
        logger.info(f"レポート選択情報削除完了: medical_id={medical_id}, 削除数={deleted_count}")
        
        return ReportSelectionDeleteResponse(
            medical_id=medical_id,
            deleted_count=deleted_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"レポート選択情報削除エラー: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")