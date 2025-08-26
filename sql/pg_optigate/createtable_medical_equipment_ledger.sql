-- Table: public.medical_equipment_ledger
--   医療機関別機器台帳（オンプレミス側PostgreSQLのtblhpmelistから集約されたデータ）
--
-- Note:
--    - テーブル定義書(YAML)を利用し、generate_dbdesign_artifacts.pyでの自動生成
--
-- ChangeLog:
--    v1.0.0 (2025-08-22)
--    - 新規作成
--
-- DROP TABLE IF EXISTS public.medical_equipment_ledger

DROP SEQUENCE IF EXISTS medical_equipment_ledger_ledger_id_seq;
CREATE SEQUENCE medical_equipment_ledger_ledger_id_seq;

CREATE TABLE IF NOT EXISTS public.medical_equipment_ledger (
    ledger_id integer NOT NULL DEFAULT nextval('medical_equipment_ledger_ledger_id_seq'::regclass),
    medical_id integer NOT NULL,
    model_number text COLLATE pg_catalog."default" NOT NULL,
    product_name text COLLATE pg_catalog."default",
    maker_name text COLLATE pg_catalog."default",
    classification_id integer,
    stock_quantity integer NOT NULL,
    is_included boolean NOT NULL,
    reg_user_id text COLLATE pg_catalog."default" NOT NULL,
    regdate timestamp NOT NULL,
    update_user_id text COLLATE pg_catalog."default" NOT NULL,
    lastupdate timestamp NOT NULL,
    PRIMARY KEY (ledger_id)
);


CREATE INDEX idx_medical_equipment_medical_id ON medical_equipment_ledger (medical_id);

CREATE INDEX idx_medical_equipment_model ON medical_equipment_ledger (medical_id, model_number);

CREATE INDEX idx_medical_equipment_maker ON medical_equipment_ledger (maker_name);

--TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.medical_equipment_ledger
    OWNER to usr_optigate;

COMMENT ON TABLE public.medical_equipment_ledger
    IS '医療機関別機器台帳（オンプレミス側PostgreSQLのtblhpmelistから集約されたデータ）';