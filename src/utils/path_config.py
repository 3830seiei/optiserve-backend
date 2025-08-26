"""path_config.py

OS環境に応じた動的パス設定管理

このモジュールは異なるOS環境（macOS、WSL Ubuntu、コンテナ）間での
パス切り替えを自動化し、プロジェクト全体で統一されたパス管理を提供します。

ChangeLog:
    v1.0.0 (2025-08-26)
        - 新規作成
        - OS判定による動的パス切り替え機能実装
        - データベース、ファイル管理、オンプレレポートのパス管理
"""
import os
import platform
from pathlib import Path
from typing import Dict, Any

class PathConfig:
    """OS環境に応じたパス設定管理クラス"""
    
    def __init__(self):
        self._system = platform.system().lower()
        self._base_paths = self._get_base_paths()
        
    def _get_base_paths(self) -> Dict[str, Path]:
        """OS環境に応じたベースパスを取得"""
        
        # 環境変数による明示的な指定があれば優先
        if os.environ.get("OPTISERVE_BASE_PATH"):
            base_path = Path(os.environ["OPTISERVE_BASE_PATH"])
            return {
                "base": base_path,
                "data": base_path / "data",
                "files": base_path / "files", 
                "database": base_path
            }
        
        # OS自動判定
        if self._system == "darwin":  # macOS
            base_path = Path("/Users/smds/develop/optiserve-backend")
        elif self._system == "linux":
            # WSL Ubuntuかコンテナかを判定
            if os.path.exists("/proc/version"):
                with open("/proc/version", "r") as f:
                    version_info = f.read().lower()
                    if "microsoft" in version_info or "wsl" in version_info:
                        # WSL Ubuntu
                        base_path = Path("/home/smds/projects/optiserve-backend")
                    else:
                        # 通常のLinux（コンテナ含む）
                        base_path = Path("/app")  # コンテナ内標準パス
            else:
                base_path = Path("/app")
        else:
            # その他のOS（Windows等）
            base_path = Path.cwd()  # カレントディレクトリをベース
            
        return {
            "base": base_path,
            "data": base_path / "data",
            "files": base_path / "files",
            "database": base_path
        }
    
    @property
    def base_path(self) -> Path:
        """プロジェクトのベースパス"""
        return self._base_paths["base"]
    
    @property
    def database_path(self) -> Path:
        """データベースファイルのパス"""
        return self._base_paths["database"]
    
    @property
    def files_base_path(self) -> Path:
        """ファイル管理のベースパス"""
        return self._base_paths["files"]
    
    @property
    def uploads_path(self) -> Path:
        """アップロードファイル保存パス"""
        return self.files_base_path / "uploads"
    
    @property
    def reports_path(self) -> Path:
        """レポートファイル保存パス"""
        return self.files_base_path / "reports"
    
    @property
    def data_path(self) -> Path:
        """データディレクトリのパス"""
        return self._base_paths["data"]
    
    @property
    def onpre_reports_path(self) -> Path:
        """オンプレミスレポート保存パス"""
        return self.data_path / "onpre_reports"
    
    def get_database_url(self, db_filename: str = "poc_optigate.db") -> str:
        """データベースURL文字列を取得"""
        db_path = self.database_path / db_filename
        return f"sqlite:///{db_path}"
    
    def ensure_directories(self) -> None:
        """必要なディレクトリを作成"""
        directories = [
            self.files_base_path,
            self.uploads_path,
            self.reports_path,
            self.data_path,
            self.onpre_reports_path
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_config_info(self) -> Dict[str, Any]:
        """現在の設定情報を取得（デバッグ用）"""
        return {
            "system": self._system,
            "base_path": str(self.base_path),
            "database_path": str(self.database_path),
            "files_base_path": str(self.files_base_path),
            "uploads_path": str(self.uploads_path), 
            "reports_path": str(self.reports_path),
            "data_path": str(self.data_path),
            "onpre_reports_path": str(self.onpre_reports_path),
            "database_url": self.get_database_url()
        }

# シングルトンインスタンス
path_config = PathConfig()