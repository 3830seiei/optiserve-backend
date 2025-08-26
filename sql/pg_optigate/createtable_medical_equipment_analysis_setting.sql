-- Table: public.medical_equipment_analysis_setting
--   機器ごとの分析設定（対象フラグ、分類上書きなど）
--
-- Note:
--    - テーブル定義書(YAML)を利用し、generate_dbdesign_artifacts.pyでの自動生成
--
-- ChangeLog:
--    v1.0.0 (2025-08-22)
--    - 新規作成
--
-- DROP TABLE IF EXISTS public.medical_equipment_analysis_setting

CREATE TABLE IF NOT EXISTS public.medical_equipment_analysis_setting (
    ledger_id integer NOT NULL,
    override_is_included boolean NOT NULL,
    override_classification_id integer,
    note json NOT NULL,
    reg_user_id text COLLATE pg_catalog."default" NOT NULL,
    regdate timestamp NOT NULL,
    update_user_id text COLLATE pg_catalog."default" NOT NULL,
    lastupdate timestamp NOT NULL,
    PRIMARY KEY (ledger_id)
);

--TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.medical_equipment_analysis_setting
    OWNER to usr_optigate;

COMMENT ON TABLE public.medical_equipment_analysis_setting
    IS '機器ごとの分析設定（対象フラグ、分類上書きなど）';