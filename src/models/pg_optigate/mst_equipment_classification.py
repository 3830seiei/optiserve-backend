"""
mst_equipment_classification.py

mst_equipment_classification モデル定義ファイル

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


class MstEquipmentClassification(Base):
    """
    テーブル [mst_equipment_classification] に対応する ORM クラス
    """
    __tablename__ = "mst_equipment_classification"
    classification_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    medical_id = Column(Integer)
    classification_level = Column(Integer, nullable=False)
    classification_name = Column(Text, nullable=False)
    parent_classification_id = Column(Integer)
    publication_classification_id = Column(Integer)
    reg_user_id = Column(Text, nullable=False)
    regdate = Column(DateTime, nullable=False)
    update_user_id = Column(Text, nullable=False)
    lastupdate = Column(DateTime, nullable=False)