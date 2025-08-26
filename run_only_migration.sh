#!/usr/bin/env bash
#
# upgrade_tableinfo_onlyoption.sh
#
# 目的:
#   generate_dbdesign_artifacts.py の `--only` オプションを使って
#   特定の YAML 定義ファイルだけを対象に Alembic マイグレーションを生成し、
#   既存のマイグレーション履歴の末尾に連結して適用する。
#
# 使い方:
#   1) このスクリプトをプロジェクトルート（Alembic の ini ファイルがある場所）に置く
#   2) 下の「変数設定」欄を環境に合わせて変更（CONFIG_KEY, YAML_BASENAME, ALEMBIC_INIなど）
#   3) 実行権限を付与して実行:  ./upgrade_tableinfo_onlyoption.sh
#
# 注意:
#   - Alembic の ini ファイル名が標準 (`alembic.ini`) でない場合は --ini オプションで指定
#   - 実行前に DB とマイグレーションの head を一致させる（内部で upgrade head を実行）
#   - マルチヘッド状態の場合は処理を中止する
#   - 生成後は自動で upgrade head を実行
#
set -euo pipefail
IFS=$'\n\t'

# ---------- 変数設定（必要に応じて変更） -----------------------------------
CONFIG_KEY="${CONFIG_KEY:-optiserve_backend_pg_optigate}"   # generate_dbdesign_artifacts.py に渡す config_key
YAML_BASENAME="${YAML_BASENAME:-medical_equipment_ledger}"  # 対象YAML（拡張子なし）
TOOL_PATH="${TOOL_PATH:-tools/generate_dbdesign_artifacts.py}"  # ジェネレータスクリプトのパス
ALEMBIC_INI="${ALEMBIC_INI:-alembic_pg_optigate.ini}"    # Alembic ini ファイル
PYTHON_BIN="${PYTHON_BIN:-python}"                       # Python 実行コマンド（仮想環境なら venv 内の python）

# オプション: psql で生成テーブルの構造確認を行う場合は DATABASE_URL を設定
# 例: export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
DATABASE_URL="${DATABASE_URL:-}"
SCHEMA_NAME="${SCHEMA_NAME:-public}"
TABLE_NAME_FROM_YAML="${TABLE_NAME_FROM_YAML:-$YAML_BASENAME}"  # YAMLとテーブル名が異なる場合は設定

# ---------- CLI オプションでの上書き ----------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --yaml) YAML_BASENAME="$2"; shift 2;;
    --config) CONFIG_KEY="$2"; shift 2;;
    --ini) ALEMBIC_INI="$2"; shift 2;;
    --python) PYTHON_BIN="$2"; shift 2;;
    --tool) TOOL_PATH="$2"; shift 2;;
    --table) TABLE_NAME_FROM_YAML="$2"; shift 2;;
    -h|--help)
      echo "使用方法: $0 [--yaml NAME] [--config KEY] [--ini FILE] [--python BIN] [--tool PATH] [--table NAME]"
      exit 0
      ;;
    *) echo "不明なオプション: $1" >&2; exit 1;;
  esac
done

# ---------- ヘルパー関数 ---------------------------------------------------
die() { echo "ERROR: $*" >&2; exit 1; }
info(){ echo "[INFO] $*"; }
cmd() { echo "+ $*"; "$@"; }

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
info "DATABASE_URL   = ${DATABASE_URL:+(設定済)}${DATABASE_URL:+" (非表示)"}"

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

# ---------- psql でテーブル構造確認（任意） -------------------------------
if [[ -n "$DATABASE_URL" ]]; then
  if command -v psql >/dev/null 2>&1; then
    info "psql によるテーブル構造確認: ${SCHEMA_NAME}.${TABLE_NAME_FROM_YAML}"
    PGPASSWORD="" psql "$DATABASE_URL" -c "\d+ ${SCHEMA_NAME}.${TABLE_NAME_FROM_YAML}" || true
  else
    info "psql コマンドが見つからないため確認をスキップ"
  fi
else
  info "DATABASE_URL 未設定のため構造確認をスキップ"
fi

info "処理完了"
