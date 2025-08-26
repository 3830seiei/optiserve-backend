-- Table: public.equipment_usage_flags
--   医療機器の分析使用フラグ管理テーブル
--
-- Note:
--    - テーブル定義書(YAML)を利用し、generate_dbdesign_artifacts.pyでの自動生成
--
-- ChangeLog:
--    v1.0.0 (2025-07-16)
--    - 新規作成
--
-- DROP TABLE IF EXISTS public.equipment_usage_flags

CREATE TABLE IF NOT EXISTS public.equipment_usage_flags (
    medical_id integer NOT NULL,
    equipment_id integer NOT NULL,
    is_active boolean NOT NULL,
    regdate timestamp NOT NULL,
    lastupdate timestamp NOT NULL,
    PRIMARY KEY (medical_id, equipment_id)
);

--TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.equipment_usage_flags
    OWNER to usr_optigate;

COMMENT ON TABLE public.equipment_usage_flags
    IS '医療機器の分析使用フラグ管理テーブル';