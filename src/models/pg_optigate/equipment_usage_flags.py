"""
equipment_usage_flags.py

equipment_usage_flags モデル定義ファイル

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


class EquipmentUsageFlags(Base):
    """
    テーブル [equipment_usage_flags] に対応する ORM クラス
    """
    __tablename__ = "equipment_usage_flags"
    medical_id = Column(
        Integer, primary_key=True

        , nullable=False
    )
    equipment_id = Column(
        Integer, primary_key=True

        , nullable=False
    )
    is_active = Column(
        Boolean

        , nullable=False
    )
    regdate = Column(
        DateTime

        , nullable=False
    )
    lastupdate = Column(
        DateTime

        , nullable=False
    )
