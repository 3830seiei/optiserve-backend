#!/usr/bin/env python3
"""
create_sample_equipment_classification.py

テスト用の機器分類サンプルデータ作成ツール

PostgreSQLではなく、SQLiteに直接サンプルデータを作成します。
機器分類・レポート選択APIのテスト用データとして使用されます。

使用方法:
    python tests/create_sample_equipment_classification.py
"""

import sqlite3
from datetime import datetime
import sys
import os

# プロジェクトルートをsys.pathに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

SQLITE_DB_PATH = 'poc_optigate.db'

def connect_sqlite():
    """SQLite接続"""
    try:
        print("SQLiteに接続中...")
        conn = sqlite3.connect(SQLITE_DB_PATH)
        print("✅ SQLite接続成功")
        return conn
    except Exception as e:
        print(f"❌ SQLite接続エラー: {e}")
        sys.exit(1)

def get_next_classification_id(sqlite_conn) -> int:
    """次のclassification_idを取得"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT MAX(classification_id) FROM mst_equipment_classification")
    result = cursor.fetchone()[0]
    cursor.close()
    return (result or 0) + 1

def create_sample_data(sqlite_conn):
    """サンプル機器分類データを作成"""
    cursor = sqlite_conn.cursor()
    current_time = datetime.now()
    
    # テスト用医療機関ID
    medical_id = 5
    
    # 既存データをクリーンアップ
    print(f"既存の医療機関ID {medical_id} のデータをクリーンアップ中...")
    cursor.execute("DELETE FROM mst_equipment_classification WHERE medical_id = ?", (medical_id,))
    
    # classification_id管理
    next_id = get_next_classification_id(sqlite_conn)
    
    # サンプルデータ定義
    # (level, name, parent_name)の形式
    sample_data = [
        # 大分類
        (1, "治療機器", None),
        (1, "診断機器", None),
        (1, "生命維持管理装置", None),
        
        # 中分類（治療機器）
        (2, "電気メス", "治療機器"),
        (2, "レーザー治療器", "治療機器"),
        (2, "高周波治療器", "治療機器"),
        
        # 中分類（診断機器）
        (2, "超音波診断装置", "診断機器"),
        (2, "内視鏡", "診断機器"),
        (2, "X線撮影装置", "診断機器"),
        
        # 中分類（生命維持管理装置）
        (2, "人工呼吸器", "生命維持管理装置"),
        (2, "輸液ポンプ", "生命維持管理装置"),
        (2, "除細動器", "生命維持管理装置"),
        
        # 小分類（電気メス）
        (3, "単極電気メス", "電気メス"),
        (3, "双極電気メス", "電気メス"),
        
        # 小分類（超音波診断装置）
        (3, "汎用超音波診断装置", "超音波診断装置"),
        (3, "心臓用超音波診断装置", "超音波診断装置"),
        
        # 小分類（人工呼吸器）
        (3, "成人用人工呼吸器", "人工呼吸器"),
        (3, "新生児用人工呼吸器", "人工呼吸器"),
    ]
    
    # 親IDマップ作成
    parent_id_map = {}
    
    try:
        print(f"医療機関ID {medical_id} のサンプルデータを作成中...")
        
        # レベル順に処理（1 → 2 → 3）
        for target_level in [1, 2, 3]:
            for level, name, parent_name in sample_data:
                if level != target_level:
                    continue
                
                # 親IDの取得
                parent_id = None
                if parent_name:
                    parent_id = parent_id_map.get(parent_name)
                    if parent_id is None:
                        print(f"⚠️  親分類が見つかりません: {parent_name}")
                        continue
                
                # レコード挿入
                cursor.execute("""
                    INSERT INTO mst_equipment_classification 
                    (classification_id, medical_id, classification_level, classification_name, 
                     parent_classification_id, publication_classification_id, reg_user_id, regdate, update_user_id, lastupdate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (next_id, medical_id, level, name, parent_id, None, 900001, current_time, 900001, current_time))
                
                # 親IDマップに追加
                parent_id_map[name] = next_id
                next_id += 1
        
        # コミット
        sqlite_conn.commit()
        cursor.close()
        
        print(f"✅ サンプルデータ作成完了:")
        print(f"   - 作成レコード数: {len(sample_data)}件")
        print(f"   - 医療機関ID: {medical_id}")
        print(f"   - 作成日時: {current_time}")
        
    except Exception as e:
        sqlite_conn.rollback()
        cursor.close()
        print(f"❌ サンプルデータ作成エラー: {e}")
        sys.exit(1)

def verify_created_records(sqlite_conn):
    """作成されたレコードの確認"""
    print("\n作成されたレコードを確認中...")
    
    cursor = sqlite_conn.cursor()
    
    # 統計情報取得
    cursor.execute("""
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT medical_id) as hospital_count,
            COUNT(CASE WHEN classification_level = 1 THEN 1 END) as level1_count,
            COUNT(CASE WHEN classification_level = 2 THEN 1 END) as level2_count,
            COUNT(CASE WHEN classification_level = 3 THEN 1 END) as level3_count
        FROM mst_equipment_classification
        WHERE medical_id = 5
    """)
    
    stats = cursor.fetchone()
    print(f"📊 統計情報 (医療機関ID=5):")
    print(f"   - 総レコード数: {stats[0]}件")
    print(f"   - 大分類: {stats[2]}件")
    print(f"   - 中分類: {stats[3]}件")
    print(f"   - 小分類: {stats[4]}件")
    
    # サンプルレコード表示
    cursor.execute("""
        SELECT classification_id, classification_level, classification_name, parent_classification_id
        FROM mst_equipment_classification 
        WHERE medical_id = 5
        ORDER BY classification_level, classification_id
    """)
    
    records = cursor.fetchall()
    print(f"\n📋 作成された機器分類一覧:")
    for record in records:
        classification_id, level, name, parent_id = record
        level_name = {1: "大分類", 2: "中分類", 3: "小分類"}[level]
        print(f"   ID={classification_id}, {level_name}: '{name}' (parent_classification_id={parent_id})")
    
    cursor.close()

def main():
    """メイン処理"""
    print("=== 機器分類サンプルデータ作成ツール ===")
    print(f"開始時刻: {datetime.now()}")
    
    # SQLite接続とレコード作成
    sqlite_conn = connect_sqlite()
    try:
        create_sample_data(sqlite_conn)
        verify_created_records(sqlite_conn)
    finally:
        sqlite_conn.close()
        print("SQLite接続をクローズしました")
    
    print(f"\n✅ 処理完了: {datetime.now()}")

if __name__ == "__main__":
    main()