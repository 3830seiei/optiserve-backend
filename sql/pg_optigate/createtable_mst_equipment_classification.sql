-- Table: public.mst_equipment_classification
--   医療機関別と公開用（共通）の医療機器分類を管理するマスタテーブル
--
-- Note:
--    - テーブル定義書(YAML)を利用し、generate_dbdesign_artifacts.pyでの自動生成
--
-- ChangeLog:
--    v1.0.0 (2025-08-22)
--    - 新規作成
--
-- DROP TABLE IF EXISTS public.mst_equipment_classification

DROP SEQUENCE IF EXISTS mst_equipment_classification_classification_id_seq;
CREATE SEQUENCE mst_equipment_classification_classification_id_seq;

CREATE TABLE IF NOT EXISTS public.mst_equipment_classification (
    classification_id integer NOT NULL DEFAULT nextval('mst_equipment_classification_classification_id_seq'::regclass),
    medical_id integer,
    classification_level integer NOT NULL,
    classification_name text COLLATE pg_catalog."default" NOT NULL,
    parent_classification_id integer,
    publication_classification_id integer,
    reg_user_id text COLLATE pg_catalog."default" NOT NULL,
    regdate timestamp NOT NULL,
    update_user_id text COLLATE pg_catalog."default" NOT NULL,
    lastupdate timestamp NOT NULL,
    PRIMARY KEY (classification_id)
);


CREATE INDEX idx_mst_equipment_classification_medical_id ON mst_equipment_classification (medical_id);

CREATE INDEX idx_mst_equipment_classification_classification_name ON mst_equipment_classification (classification_name);

--TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.mst_equipment_classification
    OWNER to usr_optigate;

COMMENT ON TABLE public.mst_equipment_classification
    IS '医療機関別と公開用（共通）の医療機器分類を管理するマスタテーブル';