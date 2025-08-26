-- Table: public.report_publication_log
--   医療機関向けレポートの公開履歴テーブル
--
-- Note:
--    - テーブル定義書(YAML)を利用し、generate_dbdesign_artifacts.pyでの自動生成
--
-- ChangeLog:
--    v1.0.0 (2025-08-22)
--    - 新規作成
--
-- DROP TABLE IF EXISTS public.report_publication_log

DROP SEQUENCE IF EXISTS report_publication_log_publication_id_seq;
CREATE SEQUENCE report_publication_log_publication_id_seq;

CREATE TABLE IF NOT EXISTS public.report_publication_log (
    publication_id integer NOT NULL DEFAULT nextval('report_publication_log_publication_id_seq'::regclass),
    medical_id integer NOT NULL,
    publication_ym text COLLATE pg_catalog."default" NOT NULL,
    file_type integer NOT NULL,
    file_name text COLLATE pg_catalog."default" NOT NULL,
    upload_datetime timestamp NOT NULL,
    download_user_id text COLLATE pg_catalog."default" NOT NULL,
    download_datetime timestamp,
    reg_user_id text COLLATE pg_catalog."default" NOT NULL,
    regdate timestamp NOT NULL,
    update_user_id text COLLATE pg_catalog."default" NOT NULL,
    lastupdate timestamp NOT NULL,
    PRIMARY KEY (publication_id)
);


CREATE INDEX idx_report_publication_log_medical_id ON report_publication_log (medical_id);

CREATE INDEX idx_publication_ym ON report_publication_log (publication_ym);

--TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.report_publication_log
    OWNER to usr_optigate;

COMMENT ON TABLE public.report_publication_log
    IS '医療機関向けレポートの公開履歴テーブル';