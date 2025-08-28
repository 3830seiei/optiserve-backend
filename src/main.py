"""Main entry point for the FastAPI application.

OptiServe PoC用FastAPIサーバ

Changelog:
    v0.1.0 (2025-07-16)
    - Initial version
    - auth, usersのみ
    v0.2.0 (2025-08-06)
    - smds_core.loggerを追加
    v0.3.0 (2025-08-18)
    - CORSミドルウェアを追加
"""
from fastapi import FastAPI
from src.routers import auth, users, facilities, user_entity_links, file_management, equipment_classifications, medical_equipment_analysis
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from pathlib import Path

# ログ設定
def setup_logging():
    """標準loggingでログ設定を初期化"""
    log_dir = Path("./log")
    log_dir.mkdir(exist_ok=True)
    
    # ログファイル名は日付付きで生成
    from datetime import datetime
    log_file = log_dir / f"OptiServe_{datetime.now().strftime('%Y%m%d')}.log"
    
    # ロギング設定
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s][%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# ロガー初期化
logger = setup_logging()
logger.info("OptiServe APIサーバー起動")

app = FastAPI(
    title="OptiServe PoC API",
    description="OptiServe PoC用FastAPIサーバ",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開発のために全てのオリジンを許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(facilities.router)
app.include_router(user_entity_links.router)
app.include_router(file_management.router)
app.include_router(equipment_classifications.router)
app.include_router(medical_equipment_analysis.router)
