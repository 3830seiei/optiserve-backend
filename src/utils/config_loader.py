"""config_loader.py

設定ファイルの動的ロードとパス置換機能

OS環境に応じてconfig.yamlの設定値を動的に置換し、
適切なパス設定を提供します。

ChangeLog:
    v1.0.0 (2025-08-26)
        - 新規作成
        - OS環境に応じた動的設定置換機能実装
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from .path_config import path_config

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """設定ファイルを読み込み、OS環境に応じてパスを置換"""
    
    # 設定ファイル読み込み
    config_file_path = path_config.base_path / config_path
    if not config_file_path.exists():
        # フォールバック: カレントディレクトリから探す
        config_file_path = Path(config_path)
        if not config_file_path.exists():
            raise FileNotFoundError(f"設定ファイルが見つかりません: {config_path}")
    
    with open(config_file_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # OS環境に応じたパス置換
    if 'logging' in config:
        # ログパスを環境に応じて設定
        if 'LOGPATH' in config['logging']:
            log_path = path_config.base_path / "log"
            log_path.mkdir(exist_ok=True)
            config['logging']['LOGPATH'] = str(log_path)
    
    if 'database' in config:
        # データベースURIを環境に応じて設定
        if 'uri' in config['database']:
            config['database']['uri'] = path_config.get_database_url()
    
    return config

def get_config_info() -> Dict[str, Any]:
    """現在の設定情報を取得（デバッグ用）"""
    try:
        config = load_config()
        return {
            "config_loaded": True,
            "logging_path": config.get('logging', {}).get('LOGPATH', 'Not configured'),
            "database_uri": config.get('database', {}).get('uri', 'Not configured'),
            "path_config": path_config.get_config_info()
        }
    except Exception as e:
        return {
            "config_loaded": False,
            "error": str(e),
            "path_config": path_config.get_config_info()
        }