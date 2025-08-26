-- Table: public.mst_medical_facility
--   医療機関マスタ（公開データ）
--
-- Note:
--    - テーブル定義書(YAML)を利用し、generate_dbdesign_artifacts.pyでの自動生成
--
-- ChangeLog:
--    v1.0.0 (2025-08-22)
--    - 新規作成
--
-- DROP TABLE IF EXISTS public.mst_medical_facility

DROP SEQUENCE IF EXISTS mst_medical_facility_medical_id_seq;
CREATE SEQUENCE mst_medical_facility_medical_id_seq;

CREATE TABLE IF NOT EXISTS public.mst_medical_facility (
    medical_id integer NOT NULL DEFAULT nextval('mst_medical_facility_medical_id_seq'::regclass),
    medical_name text COLLATE pg_catalog."default" NOT NULL,
    address_postal_code text COLLATE pg_catalog."default",
    address_prefecture text COLLATE pg_catalog."default",
    address_city text COLLATE pg_catalog."default",
    address_line1 text COLLATE pg_catalog."default",
    address_line2 text COLLATE pg_catalog."default",
    phone_number text COLLATE pg_catalog."default",
    reg_user_id text COLLATE pg_catalog."default" NOT NULL,
    regdate timestamp NOT NULL,
    update_user_id text COLLATE pg_catalog."default" NOT NULL,
    lastupdate timestamp NOT NULL,
    PRIMARY KEY (medical_id)
);


CREATE INDEX idx_medical_name ON mst_medical_facility (address_prefecture, medical_name);

CREATE INDEX idx_phone_number ON mst_medical_facility (phone_number);

CREATE INDEX idx_address_prefecture ON mst_medical_facility (address_prefecture);

--TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.mst_medical_facility
    OWNER to usr_optigate;

COMMENT ON TABLE public.mst_medical_facility
    IS '医療機関マスタ（公開データ）';