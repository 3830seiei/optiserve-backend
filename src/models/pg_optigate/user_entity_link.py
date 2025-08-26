"""
user_entity_link.py

user_entity_link モデル定義ファイル

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


class UserEntityLink(Base):
    """
    テーブル [user_entity_link] に対応する ORM クラス
    """
    __tablename__ = "user_entity_link"
    entity_type = Column(Integer, primary_key=True, nullable=False)
    entity_relation_id = Column(Integer, primary_key=True, nullable=False)
    entity_name = Column(Text, nullable=False)
    entity_address_postal_code = Column(Text)
    entity_address_prefecture = Column(Text)
    entity_address_city = Column(Text)
    entity_address_line1 = Column(Text)
    entity_address_line2 = Column(Text)
    entity_phone_number = Column(Text)
    notification_email_list = Column(JSON, nullable=False)
    count_reportout_classification = Column(Integer, nullable=False)
    analiris_classification_level = Column(Integer, nullable=False)
    reg_user_id = Column(Text, nullable=False)
    regdate = Column(DateTime, nullable=False)
    update_user_id = Column(Text, nullable=False)
    lastupdate = Column(DateTime, nullable=False)