#!/usr/bin/env bash
#
# merge_alembic_heads.sh  (bash 3.2 互換版 / mapfile不使用)
#
# 目的:
#   Alembic の「複数 head（ブランチ）」状態を自動検出し、merge リビジョンを作成して
#   直列化したあとに `upgrade head` を実行して統一する。
#
# 使い方:
#   1) プロジェクトのルート（Alembic の ini がある場所）で実行
#   2) ini 名が標準でない場合は --ini で指定（例: --ini alembic_pg_optigate.ini）
#      ※ すでに alembic.ini へシンボリックリンク済みなら --ini は不要
#   3) 実行: ./merge_alembic_heads.sh
#
# 注意:
#   - 2本以上の head がある場合に merge を作成します（何本でも OK）
#   - すでに単一 head の場合は何もせず終了します
#   - マージメッセージは自動生成（--message で上書き可）
#     例)
#     ./merge_alembic_heads.sh --message "merge heads after medical_equipment_ledger"
#
# 修正の履歴:
#   - 2025-08-12 新規作成
#

set -euo pipefail
IFS=$'\n\t'

# ====== 設定（必要に応じて変更 or CLI で上書き） ======
ALEMBIC_INI="${ALEMBIC_INI:-alembic.ini}"       # 既定は alembic.ini（別名なら --ini で指定）
MERGE_MESSAGE="${MERGE_MESSAGE:-merge heads}"   # マージ用メッセージ

# ====== CLI オプション処理 ======
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ini) ALEMBIC_INI="$2"; shift 2;;
    --message) MERGE_MESSAGE="$2"; shift 2;;
    -h|--help)
      echo "使用例: $0 [--ini alembic_pg_optigate.ini] [--message 'merge after XXX']"
      exit 0
      ;;
    *) echo "不明なオプション: $1" >&2; exit 1;;
  esac
done

# ====== ヘルパー ======
die()  { echo "ERROR: $*" >&2; exit 1; }
info() { echo "[INFO] $*"; }
cmd()  { echo "+ $*"; "$@"; }

# ====== 前提チェック ======
[[ -f "$ALEMBIC_INI" ]] || die "Alembic ini が見つかりません: $ALEMBIC_INI"
command -v alembic >/dev/null 2>&1 || die "alembic コマンドが見つかりません（仮想環境を有効化してください）"

# ====== 現在の head を取得（mapfile不使用） ======
info "現在の head を取得します..."
# `alembic heads -v` の出力からリビジョンIDのみを抽出（行頭 'Rev:' の2番目トークン）
HEADS_RAW="$(alembic -c "$ALEMBIC_INI" heads -v 2>/dev/null | awk '/^Rev: /{print $2}')"

# 空なら終了（履歴が空か、環境が違う可能性）
if [[ -z "${HEADS_RAW// /}" ]]; then
  info "head が見つかりません（履歴が空？）。処理を終了します。"
  exit 0
fi

# 改行/空白区切りを配列相当として解釈（bash 3.2 互換）
# set -- に展開して "$@" で扱うと可搬性が高い
# shellcheck disable=SC2086
set -- $HEADS_RAW
HEAD_COUNT=$#

if [[ "$HEAD_COUNT" -eq 1 ]]; then
  info "単一 head（$1）のため、merge は不要です。処理を終了します。"
  exit 0
fi

info "複数 head を検出: $*"
info "merge リビジョンを作成します（メッセージ: '$MERGE_MESSAGE'）"

# ====== merge リビジョン作成（全 head を引数で渡す） ======
cmd alembic -c "$ALEMBIC_INI" merge -m "$MERGE_MESSAGE" "$@"

# ====== upgrade head を実行 ======
info "merge 後の upgrade を実行します..."
cmd alembic -c "$ALEMBIC_INI" upgrade head

# ====== 確認表示 ======
info "現在の head 一覧:"
alembic -c "$ALEMBIC_INI" heads -v || true

info "直近の履歴:"
alembic -c "$ALEMBIC_INI" history | tail -n 12 || true

info "完了しました。"
