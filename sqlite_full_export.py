import sqlite3
import pandas as pd
import os

DB_PATH = "poc_optigate.db"
EXPORT_DIR = "./sqlite_export"

os.makedirs(EXPORT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for (table_name,) in tables:
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    if not df.empty:
        csv_path = os.path.join(EXPORT_DIR, f"{table_name}.csv")
        df.to_csv(csv_path, index=False)
        print(f"✅ Exported: {csv_path} ({len(df)} rows)")

conn.close()
