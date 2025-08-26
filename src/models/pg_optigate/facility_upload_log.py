"""
facility_upload_log.py

facility_upload_log モデル定義ファイル

Note:
    - テーブル定義書 (YAML) をもとに、generate_dbdesign_artifacts.py により自動生成されます
    - Alembic のマイグレーションはこの ORM モデルを基に差分比較されます
    - 本ファイルは手動での編集は推奨されません（テンプレート修正で対応）

Changelog:
    v1.0.0 (2025-08-22):
    - 初版作成
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, Numeric, Text, JSON
#from dataaccess.CommonDatabaseConnect import Base
from ...database import Base  # macOS 開発環境


class FacilityUploadLog(Base):
    """
    テーブル [facility_upload_log] に対応する ORM クラス
    """
    __tablename__ = "facility_upload_log"
    uploadlog_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    medical_id = Column(Integer, nullable=False)
    file_type = Column(Integer, nullable=False)
    file_name = Column(Text, nullable=False)
    upload_datetime = Column(DateTime, nullable=False)
    upload_user_id = Column(Text, nullable=False)
    download_datetime = Column(DateTime)
    reg_user_id = Column(Text, nullable=False)
    regdate = Column(DateTime, nullable=False)
    update_user_id = Column(Text, nullable=False)
    lastupdate = Column(DateTime, nullable=False)