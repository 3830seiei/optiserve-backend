#!/usr/bin/env bash
#
# upgrade_tableinfo_onlyoption.sh
#
# 目的:
#   generate_dbdesign_artifacts.py の `--only` オプションを使って
#   特定の YAML 定義ファイルだけを対象に Alembic マイグレーションを生成し、
#   既存のマイグレーション履歴の末尾に連結して適用する。
#   さらに、DB種別（PostgreSQL / SQLite）を自動判別し、適用後にテーブル定義確認を行う。
#
# 使い方（共通）:
#   1) このスクリプトをプロジェクトルート（Alembic の ini ファイルがある場所）に置く
#   2) 下の「変数設定」を環境に合わせて変更（CONFIG_KEY, YAML_BASENAME, ALEMBIC_INI など）
#   3) 実行権限を付与して実行:  ./upgrade_tableinfo_onlyoption.sh
#
# 使い方（PostgreSQL の場合）:
#   export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
#   ./upgrade_tableinfo_onlyoption.sh
#
# 使い方（SQLite の場合）:
#   どちらか一方を設定してください
#     A) export SQLITE_DB="path/to/app.db"
#     B) export DATABASE_URL="sqlite:///absolute/path/to/app.db"  または "sqlite:///./relative.db"
#   ./upgrade_tableinfo_onlyoption.sh
#
# 注意:
#   - Alembic の ini ファイル名が標準 (`alembic.ini`) でない場合は --ini オプションで指定
#   - 実行前に DB とマイグレーションの head を一致させる（内部で upgrade head を実行）
#   - マルチヘッド状態の場合は処理を中止する
#   - 生成後は自動で upgrade head を実行
#   - テーブル確認は DB種別を自動判別（PostgreSQL=psql / SQLite=sqlite3）
#
# 修正の履歴:
#   - 2025-08-12 新規作成
#
set -euo pipefail
IFS=$'\n\t'

# ---------- 変数設定（必要に応じて変更） -----------------------------------
CONFIG_KEY="${CONFIG_KEY:-smds_optiserve_pg_optigate}"      # generate_dbdesign_artifacts.py に渡す config_key
YAML_BASENAME="${YAML_BASENAME:-medical_equipment_ledger}"  # 対象YAML（拡張子なし）
TOOL_PATH="${TOOL_PATH:-/Users/smds/develop/devbase/tools/generate_dbdesign_artifacts.py}"  # ジェネレータスクリプトのパス
ALEMBIC_INI="${ALEMBIC_INI:-alembic_pg_optigate.ini}"       # Alembic ini ファイル
PYTHON_BIN="${PYTHON_BIN:-python}"                          # Python 実行コマンド

# DB 確認用（PostgreSQL か SQLite を自動判別する）
# - PostgreSQL: DATABASE_URL を設定（postgresql://...）
# - SQLite:     SQLITE_DB にファイルパス、または DATABASE_URL=sqlite:///path/to.db を設定
DATABASE_URL="${DATABASE_URL:-}"
SQLITE_DB="${SQLITE_DB:-./poc_optigate.db}"                  # 例: ./var/app.db
SCHEMA_NAME="${SCHEMA_NAME:-public}"        # PostgreSQL のスキーマ名
TABLE_NAME_FROM_YAML="${TABLE_NAME_FROM_YAML:-$YAML_BASENAME}"  # YAMLとテーブル名が異なる場合は明示指定

# ---------- CLI オプションでの上書き ----------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --yaml) YAML_BASENAME="$2"; shift 2;;
    --config) CONFIG_KEY="$2"; shift 2;;
    --ini) ALEMBIC_INI="$2"; shift 2;;
    --python) PYTHON_BIN="$2"; shift 2;;
    --tool) TOOL_PATH="$2"; shift 2;;
    --table) TABLE_NAME_FROM_YAML="$2"; shift 2;;
    --sqlite-db) SQLITE_DB="$2"; shift 2;;   # 明示的にSQLite DBファイルを指定
    -h|--help)
      cat <<USAGE
使用方法: $0 [--yaml NAME] [--config KEY] [--ini FILE] [--python BIN] [--tool PATH] [--table NAME] [--sqlite-db FILE]
  --yaml        対象のYAML（拡張子なし）
  --config      generate_dbdesign_artifacts.py に渡す config_key
  --ini         Alembic の ini ファイル（例: alembic_pg_optigate.ini）
  --python      Python 実行コマンド（例: .venv/bin/python）
  --tool        ジェネレータスクリプトのパス
  --table       テーブル名（YAMLと異なる場合に指定）
  --sqlite-db   SQLite DBファイルを直接指定（DATABASE_URL未設定時の補助）
環境変数:
  DATABASE_URL  postgresql://...  または  sqlite:///path/to.db
  SQLITE_DB     SQLite DBファイルパス（DATABASE_URLがsqlite指定なら不要）
USAGE
      exit 0
      ;;
    *) echo "不明なオプション: $1" >&2; exit 1;;
  esac
done

# ---------- ヘルパー関数 ---------------------------------------------------
die()  { echo "ERROR: $*" >&2; exit 1; }
info() { echo "[INFO] $*"; }
cmd()  { echo "+ $*"; "$@"; }

trim() { awk '{$1=$1;print}'; }

# DB種別とパスの自動判別（psql or sqlite3 のどちらで確認するか決める）
detect_db() {
  DB_KIND=""     # "postgres" or "sqlite" or ""
  DB_DSN=""      # 表示用
  SQLITE_PATH="" # 実ファイルパス（sqlite確認で使用）

  if [[ -n "$DATABASE_URL" ]]; then
    case "$DATABASE_URL" in
      postgresql://*|postgres://*)
        DB_KIND="postgres"
        DB_DSN="(DATABASE_URL)"
        ;;
      sqlite:///*)
        DB_KIND="sqlite"
        DB_DSN="(DATABASE_URL)"
        # sqlite:///absolute/or/relative/path
        SQLITE_PATH="${DATABASE_URL#sqlite:///}"
        ;;
    esac
  fi

  if [[ -z "$DB_KIND" && -n "$SQLITE_DB" ]]; then
    DB_KIND="sqlite"
    DB_DSN="(SQLITE_DB)"
    SQLITE_PATH="$SQLITE_DB"
  fi

  echo "$DB_KIND|$DB_DSN|$SQLITE_PATH"
}

# ---------- ファイル存在チェック -------------------------------------------
[[ -f "$ALEMBIC_INI" ]] || die "Alembic ini ファイルが見つかりません: $ALEMBIC_INI"
[[ -f "$TOOL_PATH"   ]] || die "ジェネレータスクリプトが見つかりません: $TOOL_PATH"
command -v alembic >/dev/null 2>&1 || die "alembic コマンドが見つかりません（仮想環境を有効化してください）"
command -v "$PYTHON_BIN" >/dev/null 2>&1 || die "python が見つかりません: $PYTHON_BIN"

# ---------- 実行コンテキスト表示 --------------------------------------------
info "CONFIG_KEY     = $CONFIG_KEY"
info "YAML_BASENAME  = $YAML_BASENAME"
info "TOOL_PATH      = $TOOL_PATH"
info "ALEMBIC_INI    = $ALEMBIC_INI"
info "PYTHON_BIN     = $PYTHON_BIN"

read -r DETECTED_KIND DETECTED_DSN DETECTED_SQLITE_PATH <<<"$(detect_db | tr '|' ' ')"
info "DB 判定        = ${DETECTED_KIND:-未設定} ${DETECTED_DSN:-}"
[[ -n "$DETECTED_SQLITE_PATH" ]] && info "SQLite パス     = $DETECTED_SQLITE_PATH"

# ---------- DB が head にあるか確認 -----------------------------------------
info "Alembic の head/current を確認..."
HEADS_COUNT=$(alembic -c "$ALEMBIC_INI" heads | wc -l | tr -d ' ')
if [[ "$HEADS_COUNT" -ne 1 ]]; then
  alembic -c "$ALEMBIC_INI" heads -v || true
  die "マルチヘッド状態です ($HEADS_COUNT)。merge heads を行ってから再実行してください。"
fi

info "DB を head にアップグレード（既にheadなら何もしない）..."
cmd alembic -c "$ALEMBIC_INI" upgrade head

# ---------- 対象 YAML のみマイグレーション生成 -----------------------------
info "対象 YAML のみマイグレーション生成: $YAML_BASENAME"
cmd "$PYTHON_BIN" "$TOOL_PATH" "$CONFIG_KEY" --only "$YAML_BASENAME"

# ---------- 新規生成ファイル確認 --------------------------------------------
info "新規生成ファイル（名前に '$YAML_BASENAME' を含む）:"
ls -1t alembic*/versions/*"$YAML_BASENAME"*.py 2>/dev/null | head -n 3 || true

# ---------- 新マイグレーションを適用 ----------------------------------------
info "新しいマイグレーションを適用: alembic upgrade head"
cmd alembic -c "$ALEMBIC_INI" upgrade head

# ---------- 履歴確認 -------------------------------------------------------
info "直近のマイグレーション履歴:"
alembic -c "$ALEMBIC_INI" history | tail -n 10 || true

# ---------- テーブル定義のスモーク確認（DB種別に応じて自動切替） ----------
case "$DETECTED_KIND" in
  postgres)
    if command -v psql >/dev/null 2>&1; then
      info "PostgreSQL: psql によるテーブル構造確認 → ${SCHEMA_NAME}.${TABLE_NAME_FROM_YAML}"
      # DATABASE_URL から psql 接続（環境により .pgpass を利用）
      PGPASSWORD="" psql "$DATABASE_URL" -c "\d+ ${SCHEMA_NAME}.${TABLE_NAME_FROM_YAML}" || true
    else
      info "psql コマンドが見つからないため確認をスキップ（PostgreSQL）"
    fi
    ;;
  sqlite)
    if command -v sqlite3 >/dev/null 2>&1; then
      # パスが相対の場合、カレントから解決
      DBFILE="$DETECTED_SQLITE_PATH"
      [[ -z "$DBFILE" ]] && die "SQLite のDBファイルパスを解決できませんでした（DATABASE_URL または SQLITE_DB を確認）"
      if [[ ! -f "$DBFILE" ]]; then
        info "注意: SQLite DB ファイルが見つかりません: $DBFILE （接続文字列と実体が異なる可能性）"
      fi
      info "SQLite: sqlite3 によるテーブル構造確認 → ${TABLE_NAME_FROM_YAML}"
      # .schema はテーブル名一致で出力。見つからない場合は一覧を表示。
      sqlite3 "$DBFILE" ".schema ${TABLE_NAME_FROM_YAML}" || true
      info "（見つからない場合は .tables 出力）"
      sqlite3 "$DBFILE" ".tables" | tr ' ' '\n' | grep -E "^${TABLE_NAME_FROM_YAML}$" || true
    else
      info "sqlite3 コマンドが見つからないため確認をスキップ（SQLite）"
    fi
    ;;
  *)
    info "DB接続情報が未設定のため、テーブル構造確認をスキップ（DATABASE_URL または SQLITE_DB を設定すると自動確認します）"
    ;;
esac

info "処理完了"
# ================================================
# 🎯 Alembic マルチヘッド確認・手動マージ チェックシート
# ================================================
echo -e "\033[1;33m"  # 明るい黄色で開始

echo "⚠️  Alembic マルチヘッド確認・手動マージ チェックシート"
echo
echo "1️⃣ 現在の head を確認（1本ならOK）"
echo "    alembic -c alembic_pg_optigate.ini heads -v"
echo
echo "2️⃣ 複数 head が出た場合（行数が2以上）➡ マージ実行"
echo "    ./merge_alembic_heads.sh --ini alembic_pg_optigate.ini \\"
echo "        --message \"merge heads after <変更内容>\""
echo
echo "3️⃣ マージ結果を確認（末尾に merge リビジョンがあること）"
echo "    alembic -c alembic_pg_optigate.ini history | tail -n 10"
echo
echo "4️⃣ 念のため再アップグレード（変更なし＝no-opになるはず）"
echo "    alembic -c alembic_pg_optigate.ini upgrade head"
echo
echo "💡 よくあるエラー"
echo "   - Multiple head revisions are present..."
echo "       → 上記 2️⃣ へ"
echo "   - No 'script_location' key found in configuration."
echo "       → -c alembic_pg_optigate.ini を付け忘れていないか確認"
echo "   - Can't locate revision identified by 'XXXX'"
echo "       → heads と history でリビジョン整合性を確認"
echo
echo "💡 alias 推奨（~/.zshrc に追加）"
echo "    alias ae=\"alembic -c alembic_pg_optigate.ini\""
echo "    alias merge_heads=\"./merge_alembic_heads.sh --ini alembic_pg_optigate.ini\""

echo -e "\033[0m"  # 色リセット
