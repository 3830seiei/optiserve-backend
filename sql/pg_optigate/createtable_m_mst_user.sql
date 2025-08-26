-- Table: public.m_mst_user
--   OptiServe管理のユーザーマスタ
--
-- Note:
--    - テーブル定義書(YAML)を利用し、generate_dbdesign_artifacts.pyでの自動生成
--
-- ChangeLog:
--    v1.0.0 (2025-07-10)
--    - 新規作成
--
-- DROP TABLE IF EXISTS public.m_mst_user

DROP SEQUENCE IF EXISTS m_mst_user_user_id_seq;
CREATE SEQUENCE m_mst_user_user_id_seq;

CREATE TABLE IF NOT EXISTS public.m_mst_user (
    user_id integer NOT NULL DEFAULT nextval('m_mst_user_user_id_seq'::regclass),
    user_name text COLLATE pg_catalog."default" NOT NULL,
    entity_type integer NOT NULL,
    entity_relation_id integer NOT NULL,
    password text COLLATE pg_catalog."default" NOT NULL,
    e-mail text COLLATE pg_catalog."default" NOT NULL,
    phone_number text COLLATE pg_catalog."default",
    mobile_number text COLLATE pg_catalog."default" NOT NULL,
    proc_type integer NOT NULL,
    regdate timestamp NOT NULL,
    lastupdate timestamp NOT NULL,
    PRIMARY KEY (user_id)
);


CREATE UNIQUE INDEX idx_user_email ON m_mst_user (e-mail);

CREATE INDEX idx_user_entity ON m_mst_user (entity_type, entity_relation_id);

--TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.m_mst_user
    OWNER to usr_optigate;

COMMENT ON TABLE public.m_mst_user
    IS 'OptiServe管理のユーザーマスタ';