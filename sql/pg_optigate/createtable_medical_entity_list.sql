-- Table: public.medical_entity_list
--   医療機関別の医療機器台帳
--
-- Note:
--    - テーブル定義書(YAML)を利用し、generate_dbdesign_artifacts.pyでの自動生成
--
-- ChangeLog:
--    v1.0.0 (2025-07-16)
--    - 新規作成
--
-- DROP TABLE IF EXISTS public.medical_entity_list

DROP SEQUENCE IF EXISTS medical_entity_list_equipment_id_seq;
CREATE SEQUENCE medical_entity_list_equipment_id_seq;

CREATE TABLE IF NOT EXISTS public.medical_entity_list (
    equipment_id integer NOT NULL DEFAULT nextval('medical_entity_list_equipment_id_seq'::regclass),
    medical_id integer NOT NULL,
    facility_equipment_number text COLLATE pg_catalog."default" NOT NULL,
    classification_id_level1 integer NOT NULL,
    classification_id_level2 integer,
    classification_id_level3 integer,
    jahid_product_id integer,
    medie_product_id integer,
    product_name text COLLATE pg_catalog."default" NOT NULL,
    product_maker_name text COLLATE pg_catalog."default",
    date_purchase date,
    date_disposal date,
    regdate timestamp NOT NULL,
    lastupdate timestamp NOT NULL,
    PRIMARY KEY (equipment_id)
);


CREATE UNIQUE INDEX idx_medical_entity_list_medical_id_facility_equipment_number ON medical_entity_list (medical_id, facility_equipment_number);

--TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.medical_entity_list
    OWNER to usr_optigate;

COMMENT ON TABLE public.medical_entity_list
    IS '医療機関別の医療機器台帳';