-- Table: public.mst_user
--   OptiServe管理のユーザーマスタ
--
-- Note:
--    - テーブル定義書(YAML)を利用し、generate_dbdesign_artifacts.pyでの自動生成
--
-- ChangeLog:
--    v1.0.0 (2025-08-22)
--    - 新規作成
--
-- DROP TABLE IF EXISTS public.mst_user

CREATE TABLE IF NOT EXISTS public.mst_user (
    user_id text COLLATE pg_catalog."default" NOT NULL,
    user_name text COLLATE pg_catalog."default" NOT NULL,
    entity_type integer NOT NULL,
    entity_relation_id integer NOT NULL,
    password text COLLATE pg_catalog."default" NOT NULL,
    e_mail text COLLATE pg_catalog."default" NOT NULL,
    phone_number text COLLATE pg_catalog."default",
    mobile_number text COLLATE pg_catalog."default" NOT NULL,
    user_status integer NOT NULL,
    inactive_reason_code integer,
    inactive_reason_note text COLLATE pg_catalog."default",
    reg_user_id text COLLATE pg_catalog."default" NOT NULL,
    regdate timestamp NOT NULL,
    update_user_id text COLLATE pg_catalog."default" NOT NULL,
    lastupdate timestamp NOT NULL,
    PRIMARY KEY (user_id)
);


CREATE UNIQUE INDEX idx_user_email ON mst_user (e-mail);

CREATE INDEX idx_user_entity ON mst_user (entity_type, entity_relation_id);

--TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.mst_user
    OWNER to usr_optigate;

COMMENT ON TABLE public.mst_user
    IS 'OptiServe管理のユーザーマスタ';