-- Database: pg_optigate
--
-- ⚠️ 機密情報（パスワード等）の埋め込みに注意！
-- このテンプレートは Jinja2 により自動生成される SQL スクリプトです。
--     - パスワードは外部の `.env` や `-D password=xxx` で渡すことを前提にしています。
--     - 生成されたファイル（init.sql）は Git 管理しないようにしてください（.gitignore 対象）。
--     - 開発・本番の環境に応じてパスワードを切り替えられるように運用を設計してください。
--
-- Note:
--    - テーブル定義書(YAML)を利用し、generate_dbdesign_artifacts.pyでの自動生成
--    - 地域情報や言語は全て日本で対応
--
-- ChangeLog:
--    v1.0.0 (2025-08-22)
--    - 新規作成
--

-- ▼ ユーザー作成（存在しない場合のみ）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_catalog.pg_roles WHERE rolname = 'usr_optigate'
    ) THEN
        CREATE ROLE usr_optigate WITH
            LOGIN
            PASSWORD 'a~B6upMe!={3J=ue'
            NOSUPERUSER
            INHERIT
            CREATEDB
            NOCREATEROLE
            NOREPLICATION
            CONNECTION LIMIT -1;
    END IF;
END
$$;

-- ▼ データベースを作成（存在チェックとDROPは任意で）
-- DROP DATABASE IF EXISTS pg_optigate
CREATE DATABASE pg_optigate
    WITH
    OWNER = usr_optigate
    ENCODING = 'UTF8'
    LC_COLLATE = 'ja_JP.UTF-8'
    LC_CTYPE = 'ja_JP.UTF-8'
    ICU_LOCALE = 'ja-JP'
    LOCALE_PROVIDER = 'icu'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False
    TEMPLATE = template0;

-- ▼ 必要に応じてユーザーにスキーマ作成や接続権限も付与
-- GRANT ALL PRIVILEGES ON DATABASE pg_optigate TO usr_optigate;