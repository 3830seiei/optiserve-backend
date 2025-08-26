#!/bin/bash

# ----------------------------------------
# FastAPI (uvicorn) サーバー起動用シェル
# 使い方:
#   chmod +x startup_optiserve.sh
#   ./startup_optiserve.sh
# ----------------------------------------

# プロジェクトのルートディレクトリに移動（必要なら）
cd "$(dirname "$0")"

# 仮想環境activate（既に有効なら何もしない）
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d ".venv" ]; then
        echo "仮想環境を有効化します"
        source .venv/bin/activate
    else
        echo "仮想環境が見つかりません"
    fi
else
    echo "仮想環境はすでに有効です"
fi

# 環境変数例（必要に応じて追加）
export UVICORN_HOST=0.0.0.0
export UVICORN_PORT=8000
export UVICORN_RELOAD=true

# 日本時間設定
export TZ=Asia/Tokyo

# 起動コマンド
uvicorn src.main:app \
    --host $UVICORN_HOST \
    --port $UVICORN_PORT \
    --reload

# --reload は開発用（本番は外してください）
