-- Table: public.equipment_classification_report_selection
--   レポート出力用の機器分類の選択情報
--
-- Note:
--    - テーブル定義書(YAML)を利用し、generate_dbdesign_artifacts.pyでの自動生成
--
-- ChangeLog:
--    v1.0.0 (2025-08-22)
--    - 新規作成
--
-- DROP TABLE IF EXISTS public.equipment_classification_report_selection

CREATE TABLE IF NOT EXISTS public.equipment_classification_report_selection (
    medical_id integer NOT NULL,
    rank integer NOT NULL,
    classification_id integer,
    reg_user_id text COLLATE pg_catalog."default" NOT NULL,
    regdate timestamp NOT NULL,
    update_user_id text COLLATE pg_catalog."default" NOT NULL,
    lastupdate timestamp NOT NULL,
    PRIMARY KEY (medical_id, rank)
);

--TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.equipment_classification_report_selection
    OWNER to usr_optigate;

COMMENT ON TABLE public.equipment_classification_report_selection
    IS 'レポート出力用の機器分類の選択情報';