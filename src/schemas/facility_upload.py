""" schemas/facility_upload.py

医療機関ファイルアップロード情報の Pydantic スキーマ定義

Note:
    - 本モジュールは、ファイルアップロード機能のためのPydanticモデル定義です。
    - 月次運用に対応し、3種類のファイル（医療機器台帳・貸出履歴・故障履歴）の同時アップロードをサポートします。
    - facility_upload_logテーブルとの連携を前提としています。

ChangeLog:
    v1.0.0 (2025-08-07)
    - 初版作成
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re

class FacilityUploadBase(BaseModel):
    """ファイルアップロード基底モデル"""
    medical_id: int = Field(..., description="医療機関ID")
    file_type: int = Field(..., description="ファイル種別（1: 医療機器台帳, 2: 貸出履歴, 3: 故障履歴）")
    file_name: str = Field(..., description="アップロードされたファイル名")
    upload_user_id: str = Field(..., description="アップロードを行ったユーザーID")
    
    @field_validator('file_type')
    def validate_file_type(cls, v):
        """ファイル種別のバリデーション"""
        if v not in [1, 2, 3]:
            raise ValueError('ファイル種別（file_type）は1-3の値のみ有効です（1: 医療機器台帳, 2: 貸出履歴, 3: 故障履歴）')
        return v

class FacilityUploadCreate(FacilityUploadBase):
    """ファイルアップロード作成用モデル"""
    pass

class FileUploadRequest(BaseModel):
    """ファイルアップロード用リクエストモデル"""
    medical_id: int = Field(..., description="医療機関ID")
    upload_user_id: str = Field(..., description="アップロードを行ったユーザーID")

class FacilityUpload(FacilityUploadBase):
    """ファイルアップロード情報レスポンスモデル"""
    uploadlog_id: int = Field(..., description="アップロードログID")
    upload_datetime: Optional[str] = None  # ISO文字列として返す
    download_datetime: Optional[str] = None  # システム側ダウンロード日時
    regdate: Optional[str] = None  # ISO文字列として返す
    lastupdate: Optional[str] = None
    
    @field_validator('upload_datetime', mode='before')
    def convert_upload_datetime(cls, v):
        """datetime型をISO文字列に変換"""
        if isinstance(v, datetime):
            return v.isoformat()
        return v
    
    @field_validator('download_datetime', mode='before')  
    def convert_download_datetime(cls, v):
        """datetime型をISO文字列に変換"""
        if isinstance(v, datetime):
            return v.isoformat()
        return v
        
    @field_validator('regdate', mode='before')
    def convert_regdate(cls, v):
        """datetime型をISO文字列に変換"""
        if isinstance(v, datetime):
            return v.isoformat()
        return v
    
    @field_validator('lastupdate', mode='before')
    def convert_lastupdate(cls, v):
        """datetime型をISO文字列に変換"""
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    class Config:
        from_attributes = True

class FileUploadResponse(BaseModel):
    """ファイルアップロードレスポンスモデル"""
    medical_id: int = Field(..., description="医療機関ID")
    target_month: str = Field(..., description="アップロード実行年月（YYYY-MM形式）")
    upload_datetime: str = Field(..., description="アップロード完了日時")
    uploaded_files: List[FacilityUpload] = Field(..., description="アップロードされたファイル一覧")
    notification_sent: bool = Field(..., description="通知メール送信完了フラグ")
    
    class Config:
        from_attributes = True