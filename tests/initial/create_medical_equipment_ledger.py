#!/usr/bin/env python3
"""
create_medical_equipment_ledger.py

medical_equipment_ledger テーブルのレコード作成ツール

PostgreSQL の tblhpmelist テーブルから機器台帳情報を取得し、
SQLite の medical_equipment_ledger テーブルにレコードを作成します。

使用方法:
    python tests/create_medical_equipment_ledger.py

仕様:
- PostgreSQL接続先: 192.168.1.200:5433/smdsdb (postgres/postgres)
- SQLite接続先: poc_optigate.db
- データ元: tblhpmelist テーブル
- 処理対象: hpcode, modelnumber, productname, makername, bunrui, count(*)
- classification_id取得: medical_id + bunrui_name で検索（小>中>大の優先順位）
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional
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
REG_USER_ID = "900001"  # システム管理者
UPDATE_USER_ID = "900001"

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

def fetch_equipment_data(pg_conn) -> List[Tuple]:
    """PostgreSQLから機器台帳データを取得"""
    try:
        print("機器台帳データを取得中...")
        cursor = pg_conn.cursor()
        
        query = """
        select hpcode as medical_id,  -- mst_medical_facility.medical_id
          modelnumber as model_number,  -- メーカー型番
          max(productname) as product_name,  -- 機器製品名
          max(makername) as maker_name,   -- メーカー名
          max(bunrui) as bunrui_name,  -- 分類名
          count(*) as stock_quantity  -- 台帳保有台数
        from tblhpmelist
        where modelnumber <> '不明'
        group by hpcode, modelnumber
        order by hpcode, count(*) desc
        """
        
        cursor.execute(query)
        raw_data = cursor.fetchall()
        cursor.close()
        
        print(f"✅ 機器台帳データ取得完了: {len(raw_data)}件")
        return raw_data
        
    except Exception as e:
        print(f"❌ データ取得エラー: {e}")
        sys.exit(1)

def check_is_included(pg_conn, medical_id: int, model_number: str) -> bool:
    """
    貸出履歴と故障履歴の存在確認でis_includedを判定
    
    Args:
        pg_conn: PostgreSQL接続
        medical_id: 医療機関ID
        model_number: 型番
        
    Returns:
        bool: 貸出実績または故障実績があればTrue、なければFalse
    """
    try:
        cursor = pg_conn.cursor()
        
        # 貸出実績チェック
        cursor.execute(
            "SELECT COUNT(*) FROM tblrentallog WHERE hpcode = %s AND modelnumber = %s",
            (medical_id, model_number)
        )
        rental_count = cursor.fetchone()[0]
        
        # 故障実績チェック
        cursor.execute(
            "SELECT COUNT(*) FROM tblrepairlog WHERE hpcode = %s AND modelnumber = %s", 
            (medical_id, model_number)
        )
        repair_count = cursor.fetchone()[0]
        
        cursor.close()
        
        # どちらかに実績があればTrue
        return (rental_count > 0) or (repair_count > 0)
        
    except Exception as e:
        print(f"⚠️  is_included判定エラー (medical_id={medical_id}, model={model_number}): {e}")
        return False

def build_classification_map(sqlite_conn) -> Dict[Tuple[int, str], List[Tuple[int, int]]]:
    """
    medical_id と bunrui_name から classification_id への変換マップを構築
    
    Returns:
        Dict[Tuple[medical_id, bunrui_name], List[Tuple[classification_id, level]]]
        レベル順でソート済み（小分類=3, 中分類=2, 大分類=1）
    """
    try:
        print("機器分類マッピングを構築中...")
        cursor = sqlite_conn.cursor()
        
        cursor.execute("""
            SELECT medical_id, classification_name, classification_id, classification_level
            FROM mst_equipment_classification
            ORDER BY medical_id, classification_name, classification_level DESC
        """)
        
        classification_data = cursor.fetchall()
        cursor.close()
        
        # マッピング構築
        classification_map = {}
        for medical_id, class_name, class_id, level in classification_data:
            key = (medical_id, class_name)
            if key not in classification_map:
                classification_map[key] = []
            classification_map[key].append((class_id, level))
        
        # 各キーの値をレベル順（降順）でソート（小分類3 > 中分類2 > 大分類1）
        for key in classification_map:
            classification_map[key].sort(key=lambda x: x[1], reverse=True)
        
        print(f"✅ 機器分類マッピング構築完了: {len(classification_map)}件")
        return classification_map
        
    except Exception as e:
        print(f"❌ 機器分類マッピング構築エラー: {e}")
        sys.exit(1)

def get_classification_id(medical_id: int, bunrui_name: str, classification_map: Dict) -> Optional[int]:
    """
    medical_id と bunrui_name から classification_id を取得
    優先順位: 小分類 > 中分類 > 大分類
    """
    if not bunrui_name or bunrui_name.strip() == '':
        return None
    
    key = (medical_id, bunrui_name.strip())
    if key in classification_map:
        # 最初の要素（最高レベル）を返す
        return classification_map[key][0][0]
    
    return None

def get_next_ledger_id(sqlite_conn) -> int:
    """次のledger_idを取得"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT MAX(ledger_id) FROM medical_equipment_ledger")
    result = cursor.fetchone()[0]
    cursor.close()
    return (result or 0) + 1

def create_equipment_ledger_records(sqlite_conn, equipment_data: List[Tuple], classification_map: Dict, pg_conn):
    """機器台帳レコードを作成"""
    
    cursor = sqlite_conn.cursor()
    current_time = datetime.now()
    
    # 処理統計
    total_records = 0
    classification_found = 0
    classification_not_found = 0
    is_included_true_count = 0
    is_included_false_count = 0
    
    # ledger_id管理
    next_id = get_next_ledger_id(sqlite_conn)
    
    try:
        print("機器台帳レコードを作成中...")
        
        # 既存データをクリーンアップ
        print("既存のmedical_equipment_ledgerデータをクリーンアップ中...")
        cursor.execute("DELETE FROM medical_equipment_ledger")
        
        for medical_id, model_number, product_name, maker_name, bunrui_name, stock_quantity in equipment_data:
            # classification_idを取得
            classification_id = get_classification_id(medical_id, bunrui_name, classification_map)
            
            if classification_id:
                classification_found += 1
            else:
                classification_not_found += 1
                if bunrui_name:
                    print(f"⚠️  分類が見つかりません: medical_id={medical_id}, bunrui='{bunrui_name}'")
            
            # is_includedを判定（貸出履歴・故障履歴の存在確認）
            is_included = check_is_included(pg_conn, medical_id, model_number)
            if is_included:
                is_included_true_count += 1
            else:
                is_included_false_count += 1
            
            # NULLや空文字列の処理
            def clean_value(value):
                if value == '' or value is None:
                    return None
                return value
            
            # レコード挿入
            cursor.execute("""
                INSERT INTO medical_equipment_ledger 
                (ledger_id, medical_id, model_number, product_name, maker_name, 
                 classification_id, stock_quantity, is_included, reg_user_id, regdate, update_user_id, lastupdate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                next_id,
                medical_id,
                model_number,
                clean_value(product_name),
                clean_value(maker_name),
                classification_id,
                stock_quantity,
                is_included,
                REG_USER_ID,
                current_time,
                UPDATE_USER_ID,
                current_time
            ))
            
            next_id += 1
            total_records += 1
            
            # 進捗表示（100件ごと）
            if total_records % 100 == 0:
                print(f"  処理済み: {total_records}件")
        
        # コミット
        sqlite_conn.commit()
        cursor.close()
        
        print(f"✅ レコード作成完了:")
        print(f"   - 作成レコード数: {total_records}件")
        print(f"   - 分類ID取得成功: {classification_found}件")
        print(f"   - 分類ID取得失敗: {classification_not_found}件")
        print(f"   - is_included=True: {is_included_true_count}件")
        print(f"   - is_included=False: {is_included_false_count}件")
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
            COUNT(CASE WHEN classification_id IS NOT NULL THEN 1 END) as with_classification,
            COUNT(CASE WHEN classification_id IS NULL THEN 1 END) as without_classification,
            COUNT(CASE WHEN is_included = 1 THEN 1 END) as is_included_true,
            COUNT(CASE WHEN is_included = 0 THEN 1 END) as is_included_false
        FROM medical_equipment_ledger
    """)
    
    stats = cursor.fetchone()
    print(f"📊 統計情報:")
    print(f"   - 総レコード数: {stats[0]}件")
    print(f"   - 医療機関数: {stats[1]}件") 
    print(f"   - 分類ID有り: {stats[2]}件")
    print(f"   - 分類ID無し: {stats[3]}件")
    print(f"   - is_included=True: {stats[4]}件")
    print(f"   - is_included=False: {stats[5]}件")
    
    # 医療機関別統計
    cursor.execute("""
        SELECT 
            medical_id,
            COUNT(*) as equipment_count,
            SUM(stock_quantity) as total_stock
        FROM medical_equipment_ledger
        GROUP BY medical_id
        ORDER BY medical_id
    """)
    
    medical_stats = cursor.fetchall()
    print(f"\n📋 医療機関別統計:")
    for medical_id, equipment_count, total_stock in medical_stats:
        print(f"   medical_id={medical_id}: 機器種類数={equipment_count}, 総保有台数={total_stock}")
    
    # サンプルレコード表示
    cursor.execute("""
        SELECT ledger_id, medical_id, model_number, product_name, maker_name, stock_quantity, classification_id, is_included
        FROM medical_equipment_ledger 
        ORDER BY medical_id, stock_quantity DESC
        LIMIT 10
    """)
    
    sample_records = cursor.fetchall()
    print(f"\n📋 サンプルレコード (上位10件):")
    for record in sample_records:
        ledger_id, medical_id, model_number, product_name, maker_name, stock_quantity, classification_id, is_included = record
        print(f"   ID={ledger_id}, medical_id={medical_id}, model='{model_number}', product='{product_name}', stock={stock_quantity}, class_id={classification_id}, is_included={is_included}")
    
    cursor.close()

def main():
    """メイン処理"""
    print("=== medical_equipment_ledger レコード作成ツール ===")
    print(f"開始時刻: {datetime.now()}")
    
    # psycopg2が利用できない場合は終了
    if not PSYCOPG2_AVAILABLE:
        print("✅ PostgreSQLが利用できない環境では、このスクリプトの実行は不要です。")
        print("   機器台帳データは設計ファイルから自動生成されています。")
        sys.exit(0)
    
    # PostgreSQL接続とデータ取得
    pg_conn = connect_postgres()
    try:
        equipment_data = fetch_equipment_data(pg_conn)
        
        # SQLite接続とレコード作成
        sqlite_conn = connect_sqlite()
        try:
            classification_map = build_classification_map(sqlite_conn)
            create_equipment_ledger_records(sqlite_conn, equipment_data, classification_map, pg_conn)
            verify_created_records(sqlite_conn)
        finally:
            sqlite_conn.close()
            print("SQLite接続をクローズしました")
    finally:
        pg_conn.close()
        print("PostgreSQL接続をクローズしました")
    
    print(f"\n✅ 処理完了: {datetime.now()}")

if __name__ == "__main__":
    main()