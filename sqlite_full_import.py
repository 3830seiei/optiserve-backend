import sqlite3
import pandas as pd
import os

DB_PATH = "poc_optigate.db"
IMPORT_DIR = "./sqlite_export"

conn = sqlite3.connect(DB_PATH)

for file in os.listdir(IMPORT_DIR):
    if file.endswith(".csv"):
        table_name = file[:-4]
        df = pd.read_csv(os.path.join(IMPORT_DIR, file))
        df.to_sql(table_name, conn, if_exists="append", index=False)
        print(f"✅ Imported: {table_name} ({len(df)} rows)")

conn.close()
