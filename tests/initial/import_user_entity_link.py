#!/usr/bin/env python3
"""
user_entity_linkテーブルにCSVデータをインポートするスクリプト

CSVファイル: data/02_user_entity_link.csv
対象テーブル: user_entity_link
"""

import csv
import json
import sqlite3
from datetime import datetime
from pathlib import Path

def parse_email_list(email_str):
    """
    CSVのnotification_email_list文字列をJSONリストに変換
    
    Args:
        email_str (str): CSVからの文字列 (例: "['email1@example.com','email2@example.com']")
    
    Returns:
        str: JSON文字列
    """
    try:
        # 既にJSONリスト形式か確認
        if email_str.startswith('[') and email_str.endswith(']'):
            # Pythonリスト形式の文字列をパース
            # シングルクォートをダブルクォートに変換してJSONとしてパース
            json_str = email_str.replace("'", '"')
            email_list = json.loads(json_str)
            return json.dumps(email_list, ensure_ascii=False)
        else:
            # 単一のメールアドレスの場合はリスト化
            return json.dumps([email_str], ensure_ascii=False)
    except Exception as e:
        print(f"Email list parse error: {email_str} -> {e}")
        # パースに失敗した場合は単一要素のリストとして扱う
        return json.dumps([email_str], ensure_ascii=False)

def import_csv_to_db():
    """CSVファイルをSQLiteデータベースにインポート"""
    
    # ファイルパス
    csv_file = Path("data/02_user_entity_link.csv")
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
        print("既存のuser_entity_linkデータを削除中...")
        cursor.execute("DELETE FROM user_entity_link")
        
        # CSVファイルを読み込み
        print(f"CSVファイルを読み込み中: {csv_file}")
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            records_inserted = 0
            for row in csv_reader:
                # notification_email_listをJSON形式に変換
                notification_email_list = parse_email_list(row['notification_email_list'])
                
                # SQLに挿入
                insert_sql = """
                INSERT INTO user_entity_link (
                    entity_type,
                    entity_relation_id,
                    entity_name,
                    entity_address_postal_code,
                    entity_address_prefecture,
                    entity_address_city,
                    entity_address_line1,
                    entity_address_line2,
                    entity_phone_number,
                    notification_email_list,
                    count_reportout_classification,
                    analiris_classification_level,
                    reg_user_id,
                    regdate,
                    update_user_id,
                    lastupdate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                values = (
                    int(row['entity_type']),
                    int(row['entity_relation_id']),
                    row['entity_name'],
                    row['entity_address_postal_code'],
                    row['entity_address_prefecture'],
                    row['entity_address_city'],
                    row['entity_address_line1'] if row['entity_address_line1'] else None,
                    row['entity_address_line2'] if row['entity_address_line2'] else None,
                    row['entity_phone_number'],
                    notification_email_list,
                    int(row['count_reportout_classification']),
                    int(row['analiris_classification_level']),
                    int(row['reg_user_id']),
                    row['regdate'],
                    int(row['update_user_id']),
                    row['lastupdate']
                )
                
                cursor.execute(insert_sql, values)
                records_inserted += 1
                
                print(f"挿入完了: {row['entity_name']} (entity_type={row['entity_type']}, entity_relation_id={row['entity_relation_id']})")
        
        # コミット
        conn.commit()
        print(f"\nインポート完了: {records_inserted}件のレコードを挿入しました")
        
        # 確認クエリ
        cursor.execute("SELECT COUNT(*) FROM user_entity_link")
        total_count = cursor.fetchone()[0]
        print(f"user_entity_linkテーブルの総レコード数: {total_count}")
        
        # サンプルデータ表示
        print("\n挿入されたデータの確認:")
        cursor.execute("""
            SELECT entity_type, entity_relation_id, entity_name, notification_email_list
            FROM user_entity_link 
            ORDER BY entity_type, entity_relation_id
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]}-{row[1]}: {row[2]} -> {row[3]}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("user_entity_link CSVインポート開始")
    import_csv_to_db()
    print("インポート処理完了")