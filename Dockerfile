# Python 3.12ベースの公式イメージを使用
FROM python:3.12.9-slim

# ロケールやタイムゾーン（日本向け）
ENV LANG=ja_JP.UTF-8
ENV TZ=Asia/Tokyo

# 作業ディレクトリ作成
WORKDIR /app

# ホスト側のrequirements.txtをコピーしてライブラリインストール
COPY requirements.txt .

# pip更新と依存パッケージのインストール
RUN apt-get update && apt-get install -y \
    build-essential locales && \
    locale-gen ja_JP.UTF-8 && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -e smds_core && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ソースコードをコンテナにコピー
COPY . .

# MkDocs用のポート（必要に応じて）も開ける
EXPOSE 8000 8001

# 開発用の起動コマンド
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

