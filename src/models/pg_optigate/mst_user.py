"""
mst_user.py

mst_user モデル定義ファイル

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


class MstUser(Base):
    """
    テーブル [mst_user] に対応する ORM クラス
    """
    __tablename__ = "mst_user"
    user_id = Column(Text, primary_key=True, nullable=False)
    user_name = Column(Text, nullable=False)
    entity_type = Column(Integer, nullable=False)
    entity_relation_id = Column(Integer, nullable=False)
    password = Column(Text, nullable=False)
    e_mail = Column(Text, nullable=False)
    phone_number = Column(Text)
    mobile_number = Column(Text, nullable=False)
    user_status = Column(Integer, nullable=False)
    inactive_reason_code = Column(Integer)
    inactive_reason_note = Column(Text)
    reg_user_id = Column(Text, nullable=False)
    regdate = Column(DateTime, nullable=False)
    update_user_id = Column(Text, nullable=False)
    lastupdate = Column(DateTime, nullable=False)