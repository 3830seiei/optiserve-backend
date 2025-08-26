-- Table: public.user_entity_link
--   ユーザーと組織（医療機関・ディーラー・メーカー）の紐付け
--
-- Note:
--    - テーブル定義書(YAML)を利用し、generate_dbdesign_artifacts.pyでの自動生成
--
-- ChangeLog:
--    v1.0.0 (2025-08-22)
--    - 新規作成
--
-- DROP TABLE IF EXISTS public.user_entity_link

CREATE TABLE IF NOT EXISTS public.user_entity_link (
    entity_type integer NOT NULL,
    entity_relation_id integer NOT NULL,
    entity_name text COLLATE pg_catalog."default" NOT NULL,
    entity_address_postal_code text COLLATE pg_catalog."default",
    entity_address_prefecture text COLLATE pg_catalog."default",
    entity_address_city text COLLATE pg_catalog."default",
    entity_address_line1 text COLLATE pg_catalog."default",
    entity_address_line2 text COLLATE pg_catalog."default",
    entity_phone_number text COLLATE pg_catalog."default",
    notification_email_list json NOT NULL,
    count_reportout_classification integer NOT NULL,
    analiris_classification_level integer NOT NULL,
    reg_user_id text COLLATE pg_catalog."default" NOT NULL,
    regdate timestamp NOT NULL,
    update_user_id text COLLATE pg_catalog."default" NOT NULL,
    lastupdate timestamp NOT NULL,
    PRIMARY KEY (entity_type, entity_relation_id)
);


CREATE INDEX idx_user_entity ON user_entity_link (entity_type, entity_relation_id);

--TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.user_entity_link
    OWNER to usr_optigate;

COMMENT ON TABLE public.user_entity_link
    IS 'ユーザーと組織（医療機関・ディーラー・メーカー）の紐付け';