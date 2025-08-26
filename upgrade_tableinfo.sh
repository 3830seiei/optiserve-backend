#!/bin/bash

#============================================
# upgrade_tableinfo.sh
#    テーブルのyaml情報修正後のマイグレーション一括対応スクリプト
#    ★★ホストOSで実行することが前提★★
#
# Note:
#    - ホストOSから Alembic を実行するメリット
#        - 柔軟性：複数コンテナ（PostgreSQLなど）にまたがる操作が可能。Alembic + psql のような組み合わせ処理もスムーズ。
#        - ビルド不要：Alembic実行のたびにコンテナビルドやマウント設定をしなくて済む。
#        - バージョン管理やデバッグがしやすい：ファイル構成・バージョン管理・ロギングなどを開発環境と統一しやすい。
#        - 開発支援ツールと連携しやすい：VSCodeから直接スクリプト実行、または make や CI/CD 組込みもしやすい。
#        - コードと環境の分離：コンテナ内にツールを入れずに済むので、イメージが軽量・安全に保たれる。
#    - エラー等で途中から実行する場合はDBを削除しておく
#        - 例）ホストOSで実行
#            $ psql -U postgres -h localhost
#            postgres=# \l  # データベース一覧表示
#            postgres=# drop database pg_master
#            postgres=# \du  # ユーザー一覧表示
#            postgres-# drop role usr_datahub
#
# 修正の履歴:
#    v1.0.0 (2025-04-02)
#        - 新規作成
#    v1.1.0 (2025-04-07)
#        - テーブルを引数に処理を行なうように修正
#    v1.2.0 (2025-04-11)
#        - init.sql実行処理を追加
#        - generate_dbdesign_artifacts.pyの実行パラメータを追加
#============================================
set -e  # エラー時に即終了

# ユーザー設定部 ============================
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="$(basename "$PROJECT_ROOT")"
TOOLS_PATH="/home/smds/project_base/devbase/tools"
DB_ID="$1"

if [ -z "$DB_ID" ]; then
  echo "❗️第一引数に 'pg_master' や 'pg_raw' を指定してください。"
  exit 1
fi

ALEMBIC_INI="${PROJECT_ROOT}/alembic_${DB_ID}.ini"
VERSIONS_DIR="${PROJECT_ROOT}/alembic_${DB_ID}/versions"
INIT_SQL_PATH="${PROJECT_ROOT}/sql/${DB_ID}/init.sql"

# 実行処理部 ===========================
echo "📦 Step 1: Alembic versions をクリーンアップ中..."
rm -f "${VERSIONS_DIR}"/*.py
rm -rf "${VERSIONS_DIR}/__pycache__"

echo "🛠 Step 2: マイグレーションファイルを自動生成中..."
CONFIG_KEY="${PROJECT_NAME}_${DB_ID}"
python3 "${TOOLS_PATH}/generate_dbdesign_artifacts.py" "${CONFIG_KEY}"

echo "📄 Step 3: データベース初期化SQL(init.sql)を実行中..."
if [ -f "${INIT_SQL_PATH}" ]; then
  psql -U postgres -h localhost -p 5432 -f "${INIT_SQL_PATH}"
else
  echo "⚠️ init.sql が見つかりません: ${INIT_SQL_PATH}"
  exit 1
fi

echo "🔍 Step 4: Alembic 現在の状態を確認中..."
cp "${PROJECT_ROOT}/.env.localhost" "${PROJECT_ROOT}/.env"
alembic -c "${ALEMBIC_INI}" current

echo "🚀 Step 5: Alembic マイグレーションを適用中..."
alembic -c "${ALEMBIC_INI}" upgrade head
cp "${PROJECT_ROOT}/.env.docker" "${PROJECT_ROOT}/.env"

echo "✅ 完了しました！（対象: ${DB_ID}）"

