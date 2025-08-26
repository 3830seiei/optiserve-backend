#!/bin/bash
# テーブル設計リフレッシュ用シェルスクリプト
# 注意：
#   - このスクリプトはSQLite専用です。
#   - パス情報はmacOS用に設定されています。

set -e  # エラーで止まる

# 0. .env の存在チェック
if [ ! -f .env ]; then
  echo "⚠️  .envファイルが見つかりません！プロジェクトルートに.envを配置してください。"
  exit 1
fi

# 1. DB_TYPE の確認
DB_TYPE=$(grep '^DB_TYPE=' .env | cut -d '=' -f2 | tr -d '\r' | tr -d '"')
if [ -z "$DB_TYPE" ]; then
  echo "⚠️  .envのDB_TYPEが未設定です。sqliteで実行する場合は DB_TYPE=sqlite を明記してください。"
  exit 1
fi

if [ "$DB_TYPE" != "sqlite" ]; then
  echo "⚠️  現在のDB_TYPEは [$DB_TYPE] です。poc_optigate.db（SQLite）用のリフレッシュではありません！"
  echo "このまま実行すると、本番やPostgres環境を書き換えてしまうリスクがあります。"
  echo "本当にこのまま進めますか？ [y/N]"
  read -r CONFIRM
  if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "中止しました。"
    exit 0
  fi
fi

echo "== .env確認 OK：DB_TYPE=$DB_TYPE =="

echo "1. poc_optigate.db の削除"
rm -f poc_optigate.db

echo "2. alembic_pg_optigate/versions フォルダのファイル削除"
rm -f alembic_pg_optigate/versions/*.py
rm -f alembic_pg_optigate/versions/*.pyc

echo "3. マイグレーションファイルを自動生成中..."
TOOLS_PATH="/Users/smds/develop/devbase/tools"
CONFIG_KEY="optiserve_backend_pg_optigate"
python3 "${TOOLS_PATH}/generate_dbdesign_artifacts.py" "${CONFIG_KEY}"

echo "4. alembic -c alembic_pg_optigate.ini upgrade head の実行"
alembic -c alembic_pg_optigate.ini upgrade head

echo "=== テーブル設計のリフレッシュ完了 ==="
