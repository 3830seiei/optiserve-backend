""" schemas/equipment_classification.py

機器分類・レポート出力選択情報の Pydantic スキーマ定義

Note:
    - 本モジュールは、機器分類マスタとレポート出力用機器分類選択のPydanticモデル定義です。
    - mst_equipment_classificationとequipment_classification_report_selectionテーブルとの連携を前提としています。

ChangeLog:
    v1.0.0 (2025-08-08)
    - 初版作成
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class EquipmentClassificationBase(BaseModel):
    """機器分類基底モデル"""
    medical_id: Optional[int] = Field(None, description="医療機関ID（NULLの場合は公開用分類）")
    classification_level: int = Field(..., description="分類レベル（1:大分類, 2:中分類, 3:小分類）")
    classification_name: str = Field(..., description="機器分類名")
    parent_classification_id: Optional[int] = Field(None, description="親分類ID")
    publication_classification_id: Optional[int] = Field(None, description="公開用機器分類ID")
    
    @field_validator('classification_level')
    def validate_classification_level(cls, v):
        """分類レベルのバリデーション"""
        if v not in [1, 2, 3]:
            raise ValueError('classification_level は1-3の値のみ有効です（1: 大分類, 2: 中分類, 3: 小分類）')
        return v

class EquipmentClassificationCreate(EquipmentClassificationBase):
    """機器分類作成用モデル"""
    pass

class EquipmentClassification(EquipmentClassificationBase):
    """機器分類情報レスポンスモデル"""
    classification_id: int = Field(..., description="機器分類ID")
    regdate: Optional[str] = None  # ISO文字列として返す
    lastupdate: Optional[str] = None
    
    @field_validator('regdate', mode='before')
    def convert_regdate(cls, v):
        """datetime型をISO文字列に変換"""
        if isinstance(v, datetime):
            return v.isoformat()
        return v
    
    @field_validator('lastupdate', mode='before')
    def convert_lastupdate(cls, v):
        """datetime型をISO文字串に変換"""
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    class Config:
        from_attributes = True

class EquipmentClassificationListResponse(BaseModel):
    """機器分類一覧レスポンスモデル"""
    total: int = Field(..., description="総件数")
    skip: int = Field(..., description="スキップ件数")
    limit: int = Field(..., description="取得件数")
    items: List[EquipmentClassification] = Field(..., description="機器分類一覧")

class ReportSelectionItem(BaseModel):
    """レポート選択項目モデル"""
    rank: int = Field(..., description="表示順序")
    classification_id: int = Field(..., description="機器分類ID")
    classification_name: str = Field(..., description="機器分類名")

class ReportSelectionResponse(BaseModel):
    """レポート選択情報レスポンスモデル"""
    medical_id: int = Field(..., description="医療機関ID")
    max_count: int = Field(..., description="最大選択可能件数")
    selections: List[ReportSelectionItem] = Field(..., description="選択済み機器分類一覧")

class ReportSelectionRequest(BaseModel):
    """レポート選択情報登録リクエストモデル"""
    classification_ids: List[int] = Field(..., description="機器分類ID一覧（rank順）")
    
    @field_validator('classification_ids')
    def validate_classification_ids(cls, v):
        """機器分類IDリストのバリデーション"""
        if not v:
            raise ValueError('classification_ids は1件以上指定してください')
        if len(v) != len(set(v)):
            raise ValueError('classification_ids に重複があります')
        return v

class ReportSelectionCreateResponse(BaseModel):
    """レポート選択情報登録レスポンスモデル"""
    medical_id: int = Field(..., description="医療機関ID")
    created_count: int = Field(..., description="登録件数")
    selections: List[ReportSelectionItem] = Field(..., description="登録済み機器分類一覧")

class ReportSelectionDeleteResponse(BaseModel):
    """レポート選択情報削除レスポンスモデル"""
    medical_id: int = Field(..., description="医療機関ID")
    deleted_count: int = Field(..., description="削除件数")