"""Database connection and session management.

PoC版 OptiGateなので、DBはSQLiteを使用しています。
ちなみにProduction版ではPostgreSQLを使用します。

ChangeLog:
    v1.0.0 (2025-07-11)
        - 新規作成
    v1.1.0 (2025-08-26)
        - OS環境に応じた動的パス設定対応
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from .utils.path_config import path_config

# 環境変数による明示的なDATABASE_URL指定があれば優先、なければOS判定によるパス設定を使用
DATABASE_URL = os.environ.get("DATABASE_URL", path_config.get_database_url())

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """データベースセッションを取得するための依存性注入関数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
