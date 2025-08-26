#!/usr/bin/env python3
"""
mst_medical_facilityテーブルにCSVデータをインポートするスクリプト

CSVファイル: data/01_mst_medical_facility.csv
対象テーブル: mst_medical_facility
"""

import csv
import sqlite3
from datetime import datetime
from pathlib import Path

def import_csv_to_db():
    """CSVファイルをSQLiteデータベースにインポート"""
    
    # ファイルパス
    csv_file = Path("data/01_mst_medical_facility.csv")
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
        # 既存データを削除（動作検証のため）
        print("既存のmst_medical_facilityデータを削除中...")
        cursor.execute("DELETE FROM mst_medical_facility")
        
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
                INSERT INTO mst_medical_facility (
                    medical_id,
                    medical_name,
                    address_postal_code,
                    address_prefecture,
                    address_city,
                    address_line1,
                    address_line2,
                    phone_number,
                    reg_user_id,
                    regdate,
                    update_user_id,
                    lastupdate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                values = (
                    int(row['medical_id']),
                    row['medical_name'],
                    clean_value(row['address_postal_code']),
                    clean_value(row['address_prefecture']),
                    clean_value(row['address_city']),
                    clean_value(row['address_line1']),
                    clean_value(row['address_line2']),
                    clean_value(row['phone_number']),
                    int(row['reg_user_id']),
                    row['regdate'],
                    int(row['update_user_id']),
                    row['lastupdate']
                )
                
                cursor.execute(insert_sql, values)
                records_inserted += 1
                
                print(f"挿入完了: {row['medical_name']} (medical_id={row['medical_id']})")
        
        # コミット
        conn.commit()
        print(f"\nインポート完了: {records_inserted}件のレコードを挿入しました")
        
        # 確認クエリ
        cursor.execute("SELECT COUNT(*) FROM mst_medical_facility")
        total_count = cursor.fetchone()[0]
        print(f"mst_medical_facilityテーブルの総レコード数: {total_count}")
        
        # サンプルデータ表示
        print("\n挿入されたデータの確認:")
        cursor.execute("""
            SELECT medical_id, medical_name, address_prefecture, address_city, phone_number
            FROM mst_medical_facility 
            ORDER BY medical_id
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} ({row[2]}{row[3]}) Tel: {row[4]}")
        
        # user_entity_linkとの関係確認
        print("\nuser_entity_linkとの関係確認:")
        cursor.execute("""
            SELECT 
                mf.medical_id,
                mf.medical_name,
                uel.entity_name,
                uel.notification_email_list
            FROM mst_medical_facility mf
            LEFT JOIN user_entity_link uel ON mf.medical_id = uel.entity_relation_id
            WHERE uel.entity_type = 1
            ORDER BY mf.medical_id
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} -> {row[2]} (emails: {row[3]})")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("mst_medical_facility CSVインポート開始")
    import_csv_to_db()
    print("インポート処理完了")