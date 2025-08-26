from pydantic import BaseModel, Field, validator
from typing import Optional, Union, List
from datetime import datetime
import json

class UserEntityLinkBase(BaseModel):
    entity_type: int = Field(..., description="エンティティ種別")
    entity_relation_id: int = Field(..., description="エンティティID")
    entity_name: str = Field(..., description="エンティティ名")
    notification_email_list: Union[str, List[str]] = Field(..., description="通知用メールリスト（JSONまたは配列）")
    count_reportout_classification: int = Field(..., description="レポート公開の分類数")
    analiris_classification_level: int = Field(..., description="分析レポートの分類レベル")
    
    @validator('notification_email_list', pre=True)
    def convert_notification_email_list(cls, v):
        """JSONリストを文字列に変換"""
        if isinstance(v, list):
            return json.dumps(v)
        return v
    
    @validator('analiris_classification_level')
    def validate_analiris_classification_level(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError('分析レポート分類レベル（analiris_classification_level）は1-3の値のみ有効です')
        return v

class UserEntityLinkCreate(UserEntityLinkBase):
    pass

class UserEntityLink(UserEntityLinkBase):
    # 複合主キーに対応（entity_type + entity_relation_idの組み合わせが主キー）
    # レスポンスモデルでは追加フィールドを含む
    entity_address_postal_code: Optional[str] = None
    entity_address_prefecture: Optional[str] = None
    entity_address_city: Optional[str] = None
    entity_address_line1: Optional[str] = None
    entity_address_line2: Optional[str] = None
    entity_phone_number: Optional[str] = None
    regdate: Optional[str] = None  # ISO文字列として返す
    lastupdate: Optional[str] = None
    
    @validator('regdate', pre=True)
    def convert_regdate(cls, v):
        """datetime型をISO文字列に変換"""
        if isinstance(v, datetime):
            return v.isoformat()
        return v
    
    @validator('lastupdate', pre=True)
    def convert_lastupdate(cls, v):
        """datetime型をISO文字列に変換"""
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    class Config:
        from_attributes = True
