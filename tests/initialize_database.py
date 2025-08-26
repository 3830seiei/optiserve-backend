#!/usr/bin/env python3
"""
initialize_database.py

OptiServe初期データベース構築スクリプト

このスクリプトは、OptiServeの初期データを正しい順序で投入するためのマスタースクリプトです。
各データ投入スクリプトを順次実行し、エラーが発生した場合は処理を中断します。

実行順序:
1. initial/import_mst_medical_facility.py   - 医療機関マスタ
2. initial/import_user_entity_link.py       - ユーザー組織連携
3. initial/import_mst_user.py               - ユーザーマスタ
4. initial/create_equipment_classification.py - 機器分類作成
5. initial/create_sample_equipment_classification.py - サンプル機器分類
6. initial/create_medical_equipment_ledger.py - 機器台帳作成

使用方法:
    python tests/initialize_database.py
    
    # ログファイル出力付き
    python tests/initialize_database.py > logs/db_init.log 2>&1

注意事項:
- 既存データは各スクリプトの仕様に従って処理されます
- エラーが発生した場合、その時点で処理を中断します
- 実行前にデータベースファイルのバックアップを推奨します
"""

import sys
import os
import subprocess
import importlib.util
from datetime import datetime
from pathlib import Path


class DatabaseInitializer:
    """データベース初期化管理クラス"""
    
    def __init__(self):
        self.current_dir = Path(__file__).parent
        self.root_dir = self.current_dir.parent
        self.start_time = datetime.now()
        
        # 実行順序とスクリプト情報
        self.scripts = [
            {
                "name": "initial/import_mst_medical_facility.py",
                "description": "医療機関マスタデータ投入",
                "required": True
            },
            {
                "name": "initial/import_user_entity_link.py", 
                "description": "ユーザー組織連携データ投入",
                "required": True
            },
            {
                "name": "initial/import_mst_user.py",
                "description": "ユーザーマスタデータ投入", 
                "required": True
            },
            {
                "name": "initial/create_equipment_classification.py",
                "description": "機器分類データ作成",
                "required": True
            },
            {
                "name": "initial/create_sample_equipment_classification.py",
                "description": "サンプル機器分類データ作成",
                "required": False  # オプション
            },
            {
                "name": "initial/create_medical_equipment_ledger.py",
                "description": "機器台帳データ作成",
                "required": True
            }
        ]
        
        self.execution_log = []
    
    def print_header(self):
        """ヘッダー情報の表示"""
        print("=" * 80)
        print("OptiServe データベース初期化スクリプト")
        print("=" * 80)
        print(f"開始時刻: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"実行ディレクトリ: {self.current_dir}")
        print(f"プロジェクトルート: {self.root_dir}")
        print()
        
        print("実行予定スクリプト:")
        for i, script in enumerate(self.scripts, 1):
            required = "[必須]" if script["required"] else "[任意]"
            print(f"  {i}. {script['name']} {required}")
            print(f"     {script['description']}")
        print()
    
    def check_script_exists(self, script_name: str) -> bool:
        """スクリプトファイルの存在確認"""
        script_path = self.current_dir / script_name
        return script_path.exists()
    
    def execute_script(self, script_name: str, description: str, required: bool) -> bool:
        """個別スクリプトの実行"""
        script_path = self.current_dir / script_name
        
        print(f"🔄 実行中: {script_name}")
        print(f"   説明: {description}")
        print(f"   パス: {script_path}")
        
        execution_start = datetime.now()
        
        # スクリプト存在確認
        if not script_path.exists():
            print(f"❌ エラー: スクリプトが見つかりません: {script_path}")
            return False
        
        try:
            # スクリプトをサブプロセスで実行
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.root_dir),
                capture_output=True,
                text=True,
                timeout=600  # 10分でタイムアウト
            )
            
            execution_end = datetime.now()
            execution_time = (execution_end - execution_start).total_seconds()
            
            # 実行結果の記録
            log_entry = {
                "script": script_name,
                "description": description,
                "start_time": execution_start,
                "end_time": execution_end,
                "execution_time": execution_time,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            self.execution_log.append(log_entry)
            
            if result.returncode == 0:
                print(f"✅ 成功: {script_name} (実行時間: {execution_time:.2f}秒)")
                # 標準出力の重要部分を表示
                if result.stdout:
                    # 最後の数行を表示（成功メッセージなど）
                    stdout_lines = result.stdout.strip().split('\n')
                    for line in stdout_lines[-5:]:
                        if line.strip() and ('✅' in line or '完了' in line or 'success' in line.lower()):
                            print(f"   {line}")
                print()
                return True
            else:
                print(f"❌ 失敗: {script_name} (終了コード: {result.returncode})")
                print(f"   実行時間: {execution_time:.2f}秒")
                
                # エラー詳細の表示
                if result.stderr:
                    print("   エラー出力:")
                    for line in result.stderr.strip().split('\n')[-10:]:  # 最後の10行
                        print(f"     {line}")
                
                if result.stdout:
                    print("   標準出力:")
                    for line in result.stdout.strip().split('\n')[-10:]:  # 最後の10行
                        print(f"     {line}")
                
                print()
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ タイムアウト: {script_name} (10分で中断)")
            return False
        except Exception as e:
            print(f"❌ 実行エラー: {script_name}")
            print(f"   例外: {str(e)}")
            return False
    
    def print_summary(self):
        """実行結果サマリーの表示"""
        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds()
        
        print("=" * 80)
        print("実行結果サマリー")
        print("=" * 80)
        print(f"開始時刻: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"終了時刻: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"総実行時間: {total_time:.2f}秒")
        print()
        
        success_count = 0
        failed_count = 0
        
        for log_entry in self.execution_log:
            status = "✅ 成功" if log_entry["success"] else "❌ 失敗"
            print(f"{status} {log_entry['script']} ({log_entry['execution_time']:.2f}秒)")
            if log_entry["success"]:
                success_count += 1
            else:
                failed_count += 1
        
        print()
        print(f"成功: {success_count}件, 失敗: {failed_count}件")
        
        if failed_count == 0:
            print("🎉 すべてのスクリプトが正常に完了しました！")
        else:
            print("⚠️  一部のスクリプトでエラーが発生しました。")
        
        print("=" * 80)
    
    def run(self):
        """メイン実行処理"""
        self.print_header()
        
        # 各スクリプトを順次実行
        for i, script_info in enumerate(self.scripts, 1):
            script_name = script_info["name"]
            description = script_info["description"]
            required = script_info["required"]
            
            print(f"[{i}/{len(self.scripts)}] {datetime.now().strftime('%H:%M:%S')} - {script_name}")
            
            success = self.execute_script(script_name, description, required)
            
            if not success:
                if required:
                    print(f"💀 必須スクリプト '{script_name}' でエラーが発生したため、処理を中断します。")
                    break
                else:
                    print(f"⚠️  任意スクリプト '{script_name}' でエラーが発生しましたが、処理を継続します。")
        
        self.print_summary()
        
        # 失敗したスクリプトがある場合は終了コード1
        failed_scripts = [log for log in self.execution_log if not log["success"]]
        required_failed = any(
            script_info["required"] for script_info in self.scripts 
            if script_info["name"] in [log["script"] for log in failed_scripts]
        )
        
        if required_failed:
            sys.exit(1)


def main():
    """メイン関数"""
    # カレントディレクトリをプロジェクトルートに変更
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    # 初期化実行
    initializer = DatabaseInitializer()
    initializer.run()


if __name__ == "__main__":
    main()