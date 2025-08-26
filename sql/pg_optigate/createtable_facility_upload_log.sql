-- Table: public.facility_upload_log
--   医療機関のデータアップロード履歴テーブル
--
-- Note:
--    - テーブル定義書(YAML)を利用し、generate_dbdesign_artifacts.pyでの自動生成
--
-- ChangeLog:
--    v1.0.0 (2025-08-22)
--    - 新規作成
--
-- DROP TABLE IF EXISTS public.facility_upload_log

DROP SEQUENCE IF EXISTS facility_upload_log_uploadlog_id_seq;
CREATE SEQUENCE facility_upload_log_uploadlog_id_seq;

CREATE TABLE IF NOT EXISTS public.facility_upload_log (
    uploadlog_id integer NOT NULL DEFAULT nextval('facility_upload_log_uploadlog_id_seq'::regclass),
    medical_id integer NOT NULL,
    file_type integer NOT NULL,
    file_name text COLLATE pg_catalog."default" NOT NULL,
    upload_datetime timestamp NOT NULL,
    upload_user_id text COLLATE pg_catalog."default" NOT NULL,
    download_datetime timestamp,
    reg_user_id text COLLATE pg_catalog."default" NOT NULL,
    regdate timestamp NOT NULL,
    update_user_id text COLLATE pg_catalog."default" NOT NULL,
    lastupdate timestamp NOT NULL,
    PRIMARY KEY (uploadlog_id)
);

 -- 医療機関IDに対するインデックス。医療機関ごとのアップロード履歴を効率的に検索するためのインデックス。
CREATE INDEX idx_facility_upload_log_medical_id_file_type ON facility_upload_log (medical_id);

--TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.facility_upload_log
    OWNER to usr_optigate;

COMMENT ON TABLE public.facility_upload_log
    IS '医療機関のデータアップロード履歴テーブル';