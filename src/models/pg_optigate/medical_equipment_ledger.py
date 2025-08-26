"""
medical_equipment_ledger.py

medical_equipment_ledger モデル定義ファイル

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


class MedicalEquipmentLedger(Base):
    """
    テーブル [medical_equipment_ledger] に対応する ORM クラス
    """
    __tablename__ = "medical_equipment_ledger"
    ledger_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    medical_id = Column(Integer, nullable=False)
    model_number = Column(Text, nullable=False)
    product_name = Column(Text)
    maker_name = Column(Text)
    classification_id = Column(Integer)
    stock_quantity = Column(Integer, nullable=False)
    is_included = Column(Boolean, nullable=False)
    reg_user_id = Column(Text, nullable=False)
    regdate = Column(DateTime, nullable=False)
    update_user_id = Column(Text, nullable=False)
    lastupdate = Column(DateTime, nullable=False)