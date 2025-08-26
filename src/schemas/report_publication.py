""" schemas/report_publication.py

レポート公開・配信情報の Pydantic スキーマ定義

Note:
    - 本モジュールは、システム生成レポートの公開・配信機能のためのPydanticモデル定義です。
    - 月次運用に対応し、3種類のレポート（分析レポート・故障リスト・未実績リスト）の配信をサポートします。
    - report_publication_logテーブルとの連携を前提としています。

ChangeLog:
    v1.0.0 (2025-08-07)
    - 初版作成
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re

class ReportPublicationBase(BaseModel):
    """レポート公開基底モデル"""
    medical_id: int = Field(..., description="医療機関ID")
    publication_ym: str = Field(..., description="レポート公開年月（YYYY-MM形式）")
    file_type: int = Field(..., description="ファイル種別（1: 分析レポート, 2: 故障リスト, 3: 未実績リスト）")
    file_name: str = Field(..., description="公開したファイル名")
    download_user_id: str = Field(..., description="ダウンロードを行ったユーザーID")
    
    @field_validator('publication_ym')
    def validate_publication_ym(cls, v):
        """公開年月のバリデーション（YYYY-MM形式）"""
        if not re.match(r'^\d{4}-\d{2}$', v):
            raise ValueError('公開年月（publication_ym）はYYYY-MM形式で入力してください（例: 2025-01）')
        return v
    
    @field_validator('file_type')
    def validate_file_type(cls, v):
        """ファイル種別のバリデーション"""
        if v not in [1, 2, 3]:
            raise ValueError('ファイル種別（file_type）は1-3の値のみ有効です（1: 分析レポート, 2: 故障リスト, 3: 未実績リスト）')
        return v

class ReportPublicationCreate(ReportPublicationBase):
    """レポート公開作成用モデル"""
    pass

class MonthlyReportPublishRequest(BaseModel):
    """月次レポート一括公開用リクエストモデル"""
    medical_id: int = Field(..., description="医療機関ID")
    publication_ym: str = Field(..., description="公開年月（YYYY-MM形式）")
    
    @field_validator('publication_ym')
    def validate_publication_ym(cls, v):
        """公開年月のバリデーション（YYYY-MM形式）"""
        if not re.match(r'^\d{4}-\d{2}$', v):
            raise ValueError('公開年月（publication_ym）はYYYY-MM形式で入力してください（例: 2025-01）')
        return v

class ReportDownloadRequest(BaseModel):
    """レポートダウンロード用リクエストモデル"""
    user_id: str = Field(..., description="ダウンロードを行うユーザーID")

class ReportPublication(ReportPublicationBase):
    """レポート公開情報レスポンスモデル"""
    publication_id: int = Field(..., description="レポート公開ID")
    upload_datetime: Optional[str] = None  # サイトへの更新日時（ISO文字列）
    download_datetime: Optional[str] = None  # ユーザーのダウンロード日時
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

class MonthlyReportPublishResponse(BaseModel):
    """月次レポート一括公開レスポンスモデル"""
    medical_id: int = Field(..., description="医療機関ID")
    publication_ym: str = Field(..., description="公開年月（YYYY-MM形式）")
    publish_datetime: str = Field(..., description="公開完了日時")
    published_reports: List[ReportPublication] = Field(..., description="公開されたレポート一覧")
    notification_sent: bool = Field(..., description="通知メール送信完了フラグ")
    
    class Config:
        from_attributes = True

class AvailableReport(BaseModel):
    """ダウンロード可能レポート情報モデル"""
    publication_id: int = Field(..., description="レポート公開ID")
    medical_id: int = Field(..., description="医療機関ID")
    publication_ym: str = Field(..., description="レポート公開年月")
    file_type: int = Field(..., description="ファイル種別")
    file_name: str = Field(..., description="ファイル名")
    upload_datetime: str = Field(..., description="公開日時")
    is_downloaded: bool = Field(..., description="ダウンロード済みフラグ")
    download_datetime: Optional[str] = None  # 初回ダウンロード日時
    
    class Config:
        from_attributes = True