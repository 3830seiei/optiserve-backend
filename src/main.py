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
from smds_core.logger import Logger

# ロガー初期化
logger = Logger("OptiServe", "config.yaml")
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
