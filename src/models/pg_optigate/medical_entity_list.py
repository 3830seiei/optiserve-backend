"""
medical_entity_list.py

medical_entity_list モデル定義ファイル

Note:
    - テーブル定義書 (YAML) をもとに、generate_dbdesign_artifacts.py により自動生成されます
    - Alembic のマイグレーションはこの ORM モデルを基に差分比較されます
    - 本ファイルは手動での編集は推奨されません（テンプレート修正で対応）

Changelog:
    v1.0.0 (2025-07-16):
    - 初版作成
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, Numeric, Text, JSON
from ...database import Base


class MedicalEntityList(Base):
    """
    テーブル [medical_entity_list] に対応する ORM クラス
    """
    __tablename__ = "medical_entity_list"
    equipment_id = Column(
        Integer, primary_key=True
        , autoincrement=True
        , nullable=False
    )
    medical_id = Column(
        Integer

        , nullable=False
    )
    facility_equipment_number = Column(
        Text

        , nullable=False
    )
    classification_id_level1 = Column(
        Integer

        , nullable=False
    )
    classification_id_level2 = Column(
        Integer


    )
    classification_id_level3 = Column(
        Integer


    )
    jahid_product_id = Column(
        Integer


    )
    medie_product_id = Column(
        Integer


    )
    product_name = Column(
        Text

        , nullable=False
    )
    product_maker_name = Column(
        Text


    )
    date_purchase = Column(
        Date


    )
    date_disposal = Column(
        Date


    )
    regdate = Column(
        DateTime

        , nullable=False
    )
    lastupdate = Column(
        DateTime

        , nullable=False
    )
