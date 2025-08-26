#!/usr/bin/env python3
"""
create_equipment_classification.py

mst_equipment_classification テーブルのレコード作成ツール

PostgreSQL の rawhpmelist テーブルから機器分類情報を取得し、
SQLite の mst_equipment_classification テーブルにレコードを作成します。

使用方法:
    python tests/create_equipment_classification.py

仕様:
- PostgreSQL接続先: 192.168.1.200:5433/smdsdb (postgres/postgres)
- SQLite接続先: poc_optigate.db
- データ元: rawhpmelist テーブル
- 処理対象: hpcode, bunrui_1, bunrui_2, bunrui_3
"""

import sqlite3
from datetime import datetime
from typing import Set, Tuple, Dict, Optional
import sys

# psycopg2のインポートを条件付きにし、利用できない場合はスキップ
try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("⚠️  psycopg2が利用できません。PostgreSQLデータ移行はスキップします。")
    print("   開発環境ではこのスクリプトは実行不要です。")

# 接続設定
POSTGRES_CONFIG = {
    'host': '192.168.1.200',
    'port': 5433,
    'database': 'smdsdb',
    'user': 'postgres',
    'password': 'postgres'
}

SQLITE_DB_PATH = 'poc_optigate.db'

def connect_postgres():
    """PostgreSQL接続"""
    try:
        print("PostgreSQLに接続中...")
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        print("✅ PostgreSQL接続成功")
        return conn
    except Exception as e:
        print(f"❌ PostgreSQL接続エラー: {e}")
        sys.exit(1)

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

def fetch_classification_data(pg_conn) -> Set[Tuple[int, Optional[str], Optional[str], Optional[str]]]:
    """PostgreSQLから機器分類データを取得"""
    try:
        print("機器分類データを取得中...")
        cursor = pg_conn.cursor()
        
        # 1. まず元データを取得
        raw_query = """
        SELECT DISTINCT hpcode as medical_id,
                bunrui_1 as 大分類の機器分類名,
                bunrui_2 as 中分類の機器分類名,
                bunrui_3 as 小分類の機器分類名
        FROM rawhpmelist
        ORDER BY hpcode, bunrui_1, bunrui_2, bunrui_3
        """
        cursor.execute(raw_query)
        raw_data = cursor.fetchall()
        print(f"元データ取得: {len(raw_data)}件")
        
        # 2. 変換マッピングを取得
        mapping_query = """
        SELECT DISTINCT bunruiname as 変換前分類名, grpbunruiname as 変換後分類名 
        FROM mstgroupbunrui
        """
        cursor.execute(mapping_query)
        mapping_data = cursor.fetchall()
        cursor.close()
        
        # 変換マッピング辞書を構築
        conversion_map = {}
        for original, converted in mapping_data:
            if original and converted:
                conversion_map[original.strip()] = converted.strip()
        
        print(f"変換マッピング取得: {len(conversion_map)}件")
        
        # 3. データのクリーニングと変換
        cleaned_data = set()
        conversion_applied = 0
        
        for medical_id, bunrui_1, bunrui_2, bunrui_3 in raw_data:
            # 空白文字や空文字列をNoneに統一
            def clean_and_convert(s):
                if s is None or str(s).strip() == '' or str(s).strip() == '　':
                    return None
                cleaned = str(s).strip()
                # 変換マッピングを適用
                if cleaned in conversion_map:
                    nonlocal conversion_applied
                    conversion_applied += 1
                    return conversion_map[cleaned]
                return cleaned
            
            converted_bunrui_1 = clean_and_convert(bunrui_1)
            converted_bunrui_2 = clean_and_convert(bunrui_2)
            converted_bunrui_3 = clean_and_convert(bunrui_3)
            
            # 大分類が存在しない場合はスキップ
            if converted_bunrui_1 is None:
                continue
                
            cleaned_data.add((medical_id, converted_bunrui_1, converted_bunrui_2, converted_bunrui_3))
        
        print(f"✅ 機器分類データ取得完了: {len(cleaned_data)}件")
        print(f"✅ 変換適用件数: {conversion_applied}件")
        return cleaned_data
        
    except Exception as e:
        print(f"❌ データ取得エラー: {e}")
        sys.exit(1)

def get_next_classification_id(sqlite_conn) -> int:
    """次のclassification_idを取得"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT MAX(classification_id) FROM mst_equipment_classification")
    result = cursor.fetchone()[0]
    cursor.close()
    return (result or 0) + 1

def create_classification_records(sqlite_conn, classification_data: Set[Tuple[int, Optional[str], Optional[str], Optional[str]]]):
    """機器分類レコードを作成"""
    
    cursor = sqlite_conn.cursor()
    current_time = datetime.now()
    
    # 処理統計
    total_records = 0
    hospitals_processed = set()
    
    # classification_id管理
    next_id = get_next_classification_id(sqlite_conn)
    
    # 親子関係管理用辞書
    # key: (medical_id, classification_name, level), value: classification_id
    classification_map: Dict[Tuple[int, str, int], int] = {}
    
    try:
        print("機器分類レコードを作成中...")
        
        # 医療機関ごとにデータを整理
        hospital_data: Dict[int, Set[Tuple[Optional[str], Optional[str], Optional[str]]]] = {}
        for hpcode, bunrui_1, bunrui_2, bunrui_3 in classification_data:
            if hpcode not in hospital_data:
                hospital_data[hpcode] = set()
            hospital_data[hpcode].add((bunrui_1, bunrui_2, bunrui_3))
        
        # 病院ごとにレコード作成
        for medical_id in sorted(hospital_data.keys()):
            print(f"  医療機関ID {medical_id} を処理中...")
            hospitals_processed.add(medical_id)
            
            classifications = hospital_data[medical_id]
            
            # 階層ごとに処理（大→中→小の順）
            for level in [1, 2, 3]:
                for bunrui_1, bunrui_2, bunrui_3 in classifications:
                    
                    if level == 1 and bunrui_1:
                        # 大分類の処理
                        key = (medical_id, bunrui_1, 1)
                        if key not in classification_map:
                            cursor.execute("""
                                INSERT INTO mst_equipment_classification 
                                (classification_id, medical_id, classification_level, classification_name, 
                                 parent_classification_id, publication_classification_id, reg_user_id, regdate, update_user_id, lastupdate)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (next_id, medical_id, 1, bunrui_1, None, None, "900001", current_time, "900001", current_time))
                            
                            classification_map[key] = next_id
                            next_id += 1
                            total_records += 1
                    
                    elif level == 2:
                        # 中分類の処理
                        if bunrui_2:
                            # bunrui_2が存在する場合は中分類として登録
                            classification_name = bunrui_2
                            parent_key = (medical_id, bunrui_1, 1)
                        elif bunrui_3 and not bunrui_2:
                            # bunrui_2が存在しないがbunrui_3がある場合、bunrui_3を中分類として登録
                            classification_name = bunrui_3
                            parent_key = (medical_id, bunrui_1, 1)
                        else:
                            continue
                        
                        key = (medical_id, classification_name, 2)
                        if key not in classification_map:
                            parent_id = classification_map.get(parent_key)
                            if parent_id is None:
                                print(f"⚠️  親分類が見つかりません: {parent_key}")
                                continue
                                
                            cursor.execute("""
                                INSERT INTO mst_equipment_classification 
                                (classification_id, medical_id, classification_level, classification_name, 
                                 parent_classification_id, publication_classification_id, reg_user_id, regdate, update_user_id, lastupdate)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (next_id, medical_id, 2, classification_name, parent_id, None, "900001", current_time, "900001", current_time))
                            
                            classification_map[key] = next_id
                            next_id += 1
                            total_records += 1
                    
                    elif level == 3 and bunrui_2 and bunrui_3:
                        # 小分類の処理（bunrui_2とbunrui_3両方が存在する場合のみ）
                        key = (medical_id, bunrui_3, 3)
                        if key not in classification_map:
                            parent_key = (medical_id, bunrui_2, 2)
                            parent_id = classification_map.get(parent_key)
                            if parent_id is None:
                                print(f"⚠️  親分類が見つかりません: {parent_key}")
                                continue
                                
                            cursor.execute("""
                                INSERT INTO mst_equipment_classification 
                                (classification_id, medical_id, classification_level, classification_name, 
                                 parent_classification_id, publication_classification_id, reg_user_id, regdate, update_user_id, lastupdate)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (next_id, medical_id, 3, bunrui_3, parent_id, None, "900001", current_time, "900001", current_time))
                            
                            classification_map[key] = next_id
                            next_id += 1
                            total_records += 1
        
        # コミット
        sqlite_conn.commit()
        cursor.close()
        
        print(f"✅ レコード作成完了:")
        print(f"   - 作成レコード数: {total_records}件")
        print(f"   - 処理病院数: {len(hospitals_processed)}件")
        print(f"   - 作成日時: {current_time}")
        
    except Exception as e:
        sqlite_conn.rollback()
        cursor.close()
        print(f"❌ レコード作成エラー: {e}")
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
    """)
    
    stats = cursor.fetchone()
    print(f"📊 統計情報:")
    print(f"   - 総レコード数: {stats[0]}件")
    print(f"   - 医療機関数: {stats[1]}件") 
    print(f"   - 大分類: {stats[2]}件")
    print(f"   - 中分類: {stats[3]}件")
    print(f"   - 小分類: {stats[4]}件")
    
    # サンプルレコード表示
    cursor.execute("""
        SELECT medical_id, classification_level, classification_name, parent_classification_id
        FROM mst_equipment_classification 
        ORDER BY medical_id, classification_level, classification_id
        LIMIT 10
    """)
    
    sample_records = cursor.fetchall()
    print(f"\n📋 サンプルレコード (最初の10件):")
    for record in sample_records:
        medical_id, level, name, parent_id = record
        print(f"   medical_id={medical_id}, level={level}, name='{name}', parent_classification_id={parent_id}")
    
    cursor.close()

def main():
    """メイン処理"""
    print("=== mst_equipment_classification レコード作成ツール ===")
    print(f"開始時刻: {datetime.now()}")
    
    # psycopg2が利用できない場合は終了
    if not PSYCOPG2_AVAILABLE:
        print("✅ PostgreSQLが利用できない環境では、このスクリプトの実行は不要です。")
        print("   機器分類データは設計ファイルから自動生成されています。")
        sys.exit(0)
    
    # PostgreSQL接続とデータ取得
    pg_conn = connect_postgres()
    try:
        classification_data = fetch_classification_data(pg_conn)
    finally:
        pg_conn.close()
        print("PostgreSQL接続をクローズしました")
    
    # SQLite接続とレコード作成
    sqlite_conn = connect_sqlite()
    try:
        create_classification_records(sqlite_conn, classification_data)
        verify_created_records(sqlite_conn)
    finally:
        sqlite_conn.close()
        print("SQLite接続をクローズしました")
    
    print(f"\n✅ 処理完了: {datetime.now()}")

if __name__ == "__main__":
    main()