""" schemas/file_management.py

ファイル管理統合スキーマ定義

Note:
    - 本モジュールは、ファイルアップロード・レポート配信の統合管理のためのスキーマです。
    - 月次運用での一括処理やバリデーション機能を提供します。
    - 複数ファイルの同時処理や通知機能に対応しています。

ChangeLog:
    v1.0.0 (2025-08-07)
    - 初版作成
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from fastapi import UploadFile
import re

class FileTypeInfo(BaseModel):
    """ファイル種別情報"""
    file_type: int
    description: str
    required_extension: Optional[str] = None

# ファイル種別定数
UPLOAD_FILE_TYPES = {
    1: FileTypeInfo(file_type=1, description="医療機器台帳", required_extension=".csv"),
    2: FileTypeInfo(file_type=2, description="貸出履歴", required_extension=".csv"),
    3: FileTypeInfo(file_type=3, description="故障履歴", required_extension=".csv")
}

REPORT_FILE_TYPES = {
    1: FileTypeInfo(file_type=1, description="分析レポート", required_extension=".pdf"),
    2: FileTypeInfo(file_type=2, description="故障リスト", required_extension=".xlsx"),
    3: FileTypeInfo(file_type=3, description="未実績リスト", required_extension=".xlsx")
}

class MonthlyFileStatus(BaseModel):
    """月次ファイル状況"""
    medical_id: int = Field(..., description="医療機関ID")
    target_month: str = Field(..., description="対象年月（YYYY-MM形式）")
    has_upload_files: bool = Field(..., description="アップロードファイル存在フラグ")
    has_report_files: bool = Field(..., description="レポートファイル存在フラグ")
    upload_file_count: int = Field(default=0, description="アップロードファイル数")
    report_file_count: int = Field(default=0, description="レポートファイル数")
    latest_upload_date: Optional[str] = None
    latest_report_date: Optional[str] = None

class FileValidationResult(BaseModel):
    """ファイルバリデーション結果"""
    is_valid: bool = Field(..., description="バリデーション結果")
    file_name: str = Field(..., description="ファイル名")
    file_type: int = Field(..., description="ファイル種別")
    errors: List[str] = Field(default=[], description="エラーメッセージ一覧")
    warnings: List[str] = Field(default=[], description="警告メッセージ一覧")

class BatchUploadProgress(BaseModel):
    """一括アップロード進捗"""
    total_files: int = Field(..., description="総ファイル数")
    processed_files: int = Field(..., description="処理済みファイル数")
    success_count: int = Field(default=0, description="成功件数")
    error_count: int = Field(default=0, description="エラー件数")
    current_file: Optional[str] = None
    status: str = Field(..., description="処理状況（processing, completed, error）")

class NotificationSettings(BaseModel):
    """通知設定"""
    medical_id: int = Field(..., description="医療機関ID")
    email_addresses: List[str] = Field(..., description="通知先メールアドレス一覧")
    send_upload_notification: bool = Field(default=True, description="アップロード通知送信フラグ")
    send_report_notification: bool = Field(default=True, description="レポート公開通知送信フラグ")

def validate_file_extension(filename: str, expected_extension: str) -> bool:
    """ファイル拡張子のバリデーション"""
    return filename.lower().endswith(expected_extension.lower())

def validate_target_month(target_month: str) -> bool:
    """対象年月のバリデーション"""
    return bool(re.match(r'^\d{4}-\d{2}$', target_month))

def get_file_type_description(file_type: int, is_upload: bool = True) -> str:
    """ファイル種別の説明を取得"""
    file_types = UPLOAD_FILE_TYPES if is_upload else REPORT_FILE_TYPES
    return file_types.get(file_type, FileTypeInfo(file_type=file_type, description="不明")).description

class SystemHealthCheck(BaseModel):
    """システム稼働状況"""
    timestamp: str = Field(..., description="チェック日時")
    upload_service_status: str = Field(..., description="アップロードサービス状況")
    report_service_status: str = Field(..., description="レポートサービス状況")
    notification_service_status: str = Field(..., description="通知サービス状況")
    storage_available_gb: float = Field(..., description="利用可能ストレージ容量（GB）")
    active_sessions: int = Field(default=0, description="アクティブセッション数")