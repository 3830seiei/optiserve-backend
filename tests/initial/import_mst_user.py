#!/usr/bin/env python3
"""
mst_userテーブルにCSVデータをインポートするスクリプト

CSVファイル: data/03_mst_user.csv
対象テーブル: mst_user
"""

import csv
import sqlite3
from datetime import datetime
from pathlib import Path

def import_csv_to_db():
    """CSVファイルをSQLiteデータベースにインポート"""
    
    # ファイルパス
    csv_file = Path("data/03_mst_user.csv")
    db_file = Path("poc_optigate.db")
    
    if not csv_file.exists():
        print(f"CSVファイルが見つかりません: {csv_file}")
        return
    
    if not db_file.exists():
        print(f"データベースファイルが見つかりません: {db_file}")
        return
    
    # データベース接続
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        # 既存データを削除（必要に応じて）
        print("既存のmst_userデータを削除中...")
        cursor.execute("DELETE FROM mst_user")
        
        # CSVファイルを読み込み
        print(f"CSVファイルを読み込み中: {csv_file}")
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            records_inserted = 0
            for row in csv_reader:
                # NULLまたは空文字列の処理
                def clean_value(value):
                    if value == '' or value is None:
                        return None
                    return value
                
                # SQLに挿入
                insert_sql = """
                INSERT INTO mst_user (
                    user_id,
                    user_name,
                    entity_type,
                    entity_relation_id,
                    password,
                    e_mail,
                    phone_number,
                    mobile_number,
                    user_status,
                    inactive_reason_code,
                    inactive_reason_note,
                    reg_user_id,
                    regdate,
                    update_user_id,
                    lastupdate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                values = (
                    int(row['user_id']),
                    row['user_name'],
                    int(row['entity_type']),
                    int(row['entity_relation_id']),
                    row['password'],
                    row['e_mail'],
                    clean_value(row['phone_number']),
                    clean_value(row['mobile_number']),
                    int(row['user_status']),
                    clean_value(row['inactive_reason_code']),
                    clean_value(row['inactive_reason_note']),
                    int(row['reg_user_id']),
                    row['regdate'],
                    int(row['update_user_id']),
                    row['lastupdate']
                )
                
                cursor.execute(insert_sql, values)
                records_inserted += 1
                
                print(f"挿入完了: {row['user_name']} (user_id={row['user_id']}, entity_type={row['entity_type']})")
        
        # コミット
        conn.commit()
        print(f"\nインポート完了: {records_inserted}件のレコードを挿入しました")
        
        # 確認クエリ
        cursor.execute("SELECT COUNT(*) FROM mst_user")
        total_count = cursor.fetchone()[0]
        print(f"mst_userテーブルの総レコード数: {total_count}")
        
        # サンプルデータ表示
        print("\n挿入されたデータの確認:")
        cursor.execute("""
            SELECT user_id, user_name, entity_type, entity_relation_id, user_status
            FROM mst_user 
            ORDER BY user_id
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} (entity_type={row[2]}, entity_relation_id={row[3]}, status={row[4]})")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("mst_user CSVインポート開始")
    import_csv_to_db()
    print("インポート処理完了")