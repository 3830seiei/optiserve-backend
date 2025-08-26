"""
medical_equipment_analysis.py

医療機器分析設定関連のスキーマ定義

- 取得用の複合スキーマ（medical_equipment_ledger + analysis_setting + classification）
- 更新用のリクエスト・レスポンススキーマ
- note履歴管理用のスキーマ
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# Note履歴管理用のスキーマ
class NoteHistoryItem(BaseModel):
    """履歴アイテム"""
    user_id: str = Field(..., description="変更ユーザーID")
    timestamp: str = Field(..., description="変更日時 (YYYY-MM-DD HH:MM:SS)")
    note: str = Field(..., description="補足情報・変更理由")


# 取得用の複合スキーマ
class MedicalEquipmentAnalysisResponse(BaseModel):
    """医療機器分析設定の取得レスポンス"""
    
    # 機器台帳情報
    ledger_id: int = Field(..., description="機器台帳ID")
    medical_id: int = Field(..., description="医療機関ID")
    model_number: str = Field(..., description="型番")
    product_name: Optional[str] = Field(None, description="製品名")
    maker_name: Optional[str] = Field(None, description="メーカー名")
    stock_quantity: int = Field(..., description="保有台数")
    
    # 元の設定値（デフォルト）
    default_is_included: bool = Field(..., description="デフォルトの分析対象フラグ")
    default_classification_id: Optional[int] = Field(None, description="デフォルトの分類ID")
    
    # 現在の有効値（上書き設定を考慮）
    effective_is_included: bool = Field(..., description="有効な分析対象フラグ")
    effective_classification_id: Optional[int] = Field(None, description="有効な分類ID")
    
    # 上書き設定情報
    has_override: bool = Field(..., description="上書き設定の有無")
    override_is_included: Optional[bool] = Field(None, description="上書きされた分析対象フラグ")
    override_classification_id: Optional[int] = Field(None, description="上書きされた分類ID")
    
    # 分類情報
    classification_name: Optional[str] = Field(None, description="分類名")
    classification_level: Optional[int] = Field(None, description="分類レベル")
    
    # 履歴・管理情報
    note_history: List[NoteHistoryItem] = Field(default_factory=list, description="変更履歴")
    last_modified: Optional[datetime] = Field(None, description="最終更新日時")
    last_modified_user_id: Optional[str] = Field(None, description="最終更新ユーザーID")


class MedicalEquipmentAnalysisListResponse(BaseModel):
    """医療機器分析設定の一覧取得レスポンス"""
    items: List[MedicalEquipmentAnalysisResponse] = Field(..., description="機器分析設定一覧")
    total_count: int = Field(..., description="総件数")
    has_next: bool = Field(..., description="次ページの有無")


# 分析対象更新用スキーマ
class AnalysisTargetUpdateRequest(BaseModel):
    """分析対象フラグ更新リクエスト"""
    override_is_included: bool = Field(..., description="上書きする分析対象フラグ")
    note: str = Field(..., min_length=1, max_length=500, description="変更理由・補足情報")
    
    @validator('note')
    def validate_note(cls, v):
        if not v or not v.strip():
            raise ValueError('変更理由は必須です')
        return v.strip()


class AnalysisTargetUpdateResponse(BaseModel):
    """分析対象フラグ更新レスポンス"""
    ledger_id: int = Field(..., description="更新された機器台帳ID")
    override_is_included: bool = Field(..., description="設定された分析対象フラグ")
    effective_is_included: bool = Field(..., description="有効になった分析対象フラグ")
    updated_at: datetime = Field(..., description="更新日時")
    message: str = Field(..., description="更新結果メッセージ")


# 分類上書き更新用スキーマ
class ClassificationOverrideUpdateRequest(BaseModel):
    """分類上書き更新リクエスト"""
    override_classification_id: int = Field(..., description="上書きする分類ID")
    note: str = Field(..., min_length=1, max_length=500, description="変更理由・補足情報")
    
    @validator('note')
    def validate_note(cls, v):
        if not v or not v.strip():
            raise ValueError('変更理由は必須です')
        return v.strip()


class ClassificationOverrideUpdateResponse(BaseModel):
    """分類上書き更新レスポンス"""
    ledger_id: int = Field(..., description="更新された機器台帳ID")
    override_classification_id: int = Field(..., description="設定された分類ID")
    effective_classification_id: int = Field(..., description="有効になった分類ID")
    classification_name: str = Field(..., description="分類名")
    updated_at: datetime = Field(..., description="更新日時")
    message: str = Field(..., description="更新結果メッセージ")


# デフォルト復帰用スキーマ
class DefaultRestoreResponse(BaseModel):
    """デフォルト復帰レスポンス"""
    affected_count: int = Field(..., description="削除された設定数")
    ledger_ids: List[int] = Field(..., description="影響を受けた機器台帳IDリスト")
    message: str = Field(..., description="処理結果メッセージ")


# エラーレスポンス
class ValidationErrorResponse(BaseModel):
    """バリデーションエラーレスポンス"""
    error_type: str = Field(..., description="エラータイプ")
    message: str = Field(..., description="エラーメッセージ")
    details: Optional[Dict[str, Any]] = Field(None, description="詳細情報")


# 取得用のクエリパラメータ
class MedicalEquipmentAnalysisQuery(BaseModel):
    """検索クエリパラメータ"""
    medical_id: int = Field(..., description="医療機関ID")
    classification_id: Optional[int] = Field(None, description="分類IDでフィルタ")
    skip: int = Field(0, ge=0, description="スキップ件数")
    limit: int = Field(100, ge=1, le=1000, description="取得件数")
    
    @validator('limit')
    def validate_limit(cls, v):
        if v > 1000:
            raise ValueError('取得件数は最大1000件です')
        return v