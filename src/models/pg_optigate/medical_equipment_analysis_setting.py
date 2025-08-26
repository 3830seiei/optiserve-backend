"""
medical_equipment_analysis_setting.py

medical_equipment_analysis_setting モデル定義ファイル

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


class MedicalEquipmentAnalysisSetting(Base):
    """
    テーブル [medical_equipment_analysis_setting] に対応する ORM クラス
    """
    __tablename__ = "medical_equipment_analysis_setting"
    ledger_id = Column(Integer, primary_key=True, nullable=False)
    override_is_included = Column(Boolean, nullable=False)
    override_classification_id = Column(Integer)
    note = Column(JSON, nullable=False)
    reg_user_id = Column(Text, nullable=False)
    regdate = Column(DateTime, nullable=False)
    update_user_id = Column(Text, nullable=False)
    lastupdate = Column(DateTime, nullable=False)