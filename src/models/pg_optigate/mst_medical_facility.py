"""
mst_medical_facility.py

mst_medical_facility モデル定義ファイル

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


class MstMedicalFacility(Base):
    """
    テーブル [mst_medical_facility] に対応する ORM クラス
    """
    __tablename__ = "mst_medical_facility"
    medical_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    medical_name = Column(Text, nullable=False)
    address_postal_code = Column(Text)
    address_prefecture = Column(Text)
    address_city = Column(Text)
    address_line1 = Column(Text)
    address_line2 = Column(Text)
    phone_number = Column(Text)
    reg_user_id = Column(Text, nullable=False)
    regdate = Column(DateTime, nullable=False)
    update_user_id = Column(Text, nullable=False)
    lastupdate = Column(DateTime, nullable=False)