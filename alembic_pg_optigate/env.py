"""
env.py - Alembic マイグレーション実行時の設定ファイル

このファイルは Alembic によるマイグレーション実行時に、接続先のデータベース情報や、
マイグレーション実行の方法（オンライン / オフライン）を制御するためのスクリプトです。

【修正ポイント】
- `.env` ファイルを利用して、機密性の高い接続情報（ユーザー名・パスワード・ホスト名など）を
  INI ファイルに直接記述せず、外部ファイルから安全に読み込むように変更。
- Alembic 実行時に `sqlalchemy.url` を `.env` に定義された環境変数から組み立てて設定。
- タイムゾーン（Asia/Tokyo）でのマイグレーション対応も実施済み。

【前提】
- `.env` ファイルがプロジェクトルートに存在し、以下のようなキーが定義されていること：
　　例）データベースに応じて定義
    PG_MASTER_USER
    PG_MASTER_PASSWORD
    PG_MASTER_HOST
    PG_MASTER_DBNAME
    PG_MASTER_PORT

Note:
    - Alembicの実行モードには２つの方法があります。
        - オンラインモード：DB接続を行い、マイグレーションを実行する。
        　開発・本番環境等に直接反映したいときに利用。現プロジェクトはこちらを頻繁に利用。
        　実行例）alembic upgrade head
        - オフラインモード：DB接続を行わず、SQL文を生成してファイルに出力する。
        　レビューなど、マイグレーションファイルを生成する際に利用。
        　実行例) alembic upgrade head --sql > migrate.sql
    - 他のDBからコピーしてきた場合は、下記を修正してください。
        - .envの内容に従い、下記部分（記載時は63行目）を修正してください。
        　DB_USER = os.getenv("PG_MASTER_USER")
        　DB_PASSWORD = os.getenv("PG_MASTER_PASSWORD")
        　DB_HOST = os.getenv("PG_MASTER_HOST")
        　DB_NAME = os.getenv("PG_MASTER_DBNAME")
        　DB_PORT = os.getenv("PG_MASTER_PORT", "5432")

ChangeLog:
    v1.0.0 (2025-04-02)
        - alembic init alembicコマンドで生成されたenv.pyをベースに修正
        - 日本のTimeZone（Asia/Tokyo）を考慮した日付の取得例を追加
    v1.1.0 (2024-04-11)
        - .envファイルからの接続情報取得を追加
"""
from logging.config import fileConfig
#from sqlalchemy import engine_from_config
from sqlalchemy import create_engine  # 1.1.0 変更
from sqlalchemy import pool
from alembic import context
from pytz import timezone  # 追加
import datetime  # 追加
import os  # 追加
from dotenv import load_dotenv  # 追加

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# .env ファイルの読み込み  v1.1.0 From --
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    raise FileNotFoundError(f".env ファイルが見つかりませんでした: {dotenv_path}\n"
                            "→ Alembic 実行前に .env をプロジェクトルートに配置してください。"
                            )

# 環境変数から DB 接続情報を取得して、Alembic に渡す接続 URL を組み立てる
# ※他DB用（例: PG_RAW）を追加する場合は、同様のキーで .env も定義してください
# 例：
# PG_RAW_USER=...
# PG_RAW_PASSWORD=...
DB_TYPE = os.getenv("DB_TYPE", "postgres")  # デフォルトは postgres(本番用)とする
if DB_TYPE == "postgres":
    DB_USER = os.getenv("PG_MASTER_USER")
    DB_PASSWORD = os.getenv("PG_MASTER_PASSWORD")
    DB_HOST = os.getenv("PG_MASTER_HOST")
    DB_NAME = os.getenv("PG_MASTER_DBNAME")
    DB_PORT = os.getenv("PG_MASTER_PORT", "5432")
    DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
elif DB_TYPE == "sqlite":
    DB_NAME = os.getenv("SQLITE_DB_NAME", "poc_optigate.db")
    # OS環境に応じた動的パス設定を適用
    if not os.path.isabs(DB_NAME):
        # 相対パスの場合は、OS判定によるベースパスを適用
        import sys
        import platform
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        
        try:
            from utils.path_config import path_config
            db_path = path_config.database_path / DB_NAME
            DB_URL = f"sqlite:///{db_path}"
        except ImportError:
            # フォールバック: 従来の相対パス
            DB_URL = f"sqlite:///{DB_NAME}"
    else:
        # 絶対パスの場合はそのまま使用
        DB_URL = f"sqlite:///{DB_NAME}"
else:
    raise ValueError(f"Unsupported DB_TYPE: {DB_TYPE}. Supported types are 'postgres' and 'sqlite'.")

print(f"DB_URL: {DB_URL}")

# Alembic の設定に URL をセット
config.set_main_option("sqlalchemy.url", DB_URL)  # v1.1.0 To --

# config_ini_sectionを設定
config.config_ini_section = 'sqlalchemy'

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Engine を使わずにデータベースの接続情報（URL）のみで context を設定し、
    SQL 文をスクリプトとして出力します。実際のDB接続が不要なため、
    DBAPIがインストールされていなくても実行可能です。

    Note:
        - 仕組み
            - DB 接続は行いません。
            - SQL スクリプトを 文字列として出力（標準出力やファイル） する構成。
            - alembic upgrade head --sql
            　↑ このように --sql オプション付きで実行すると、SQL文のみを生成して出力します。
        - 特徴
            - DB への変更は 一切行われない。
            - あくまで「マイグレーションSQLを生成するための手段」。
            - セキュリティ上の理由や、事前に SQL をレビューして適用する文化のチームに向いています。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    データベースへの実際の接続（Engine）を作成し、
    それを Alembic の context に紐付けてマイグレーションを実行します。
    `.env` ファイルで組み立てた DB_URL を直接使用する。

    Note:
        - 仕組み
            - engine_from_config() を使って データベースと接続。
            - context.configure() に接続情報を渡して、マイグレーションを実行（upgrade/downgrade）します。
        - 特徴
            - 即時で DB に反映される。
            - Alembic が SQL を自動生成 → そのまま SQL を実行。
            - 実際に alembic upgrade head を実行すると、基本こちらが呼ばれます。
    """
    print(f"✅ Using DB_URL: {DB_URL}")

    # Alembicの実行に使用するEngineを手動で作成
    connectable = create_engine(DB_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # タイムゾーンを日本時間に設定
            timezone=timezone('Asia/Tokyo')
        )

        with context.begin_transaction():
            context.run_migrations()

    # タイムゾーンを考慮した日付の取得例
    now = datetime.datetime.now(timezone('Asia/Tokyo'))
    print("Current time in Tokyo:", now)

# ここから実行モードの選択
try:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
except Exception as e:
    print(f"Error: {e}")
