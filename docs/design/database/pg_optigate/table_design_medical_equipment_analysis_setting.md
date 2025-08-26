# テーブル定義書

## テーブル名: medical_equipment_analysis_setting

機器ごとの分析設定（対象フラグ、分類上書きなど）

|カラム名|型|制約|説明|補足事項|
|:--|:--|:--|:--|:--|
|ledger_id|Integer|PK NOT NULL |機器台帳ID|pg_optigate.medical_equipment_ledgerの値を参照する|
|override_is_included|Boolean|NOT NULL |分析対象に含めるかの上書き情報|'true: 分析対象に含める, false: 分析対象外'
'マスタは実績有無で設定されるが、医療機関側での分析対象外を設定する場合に使用'
|
|override_classification_id|Integer||器機分類IDの上書き情報|医療機関独自の分類を適用する場合にセット|
|note|JSON|NOT NULL |備考（設定理由など）|user_id, timestamp, note の配列を格納するJSON形式|
|reg_user_id|Text|NOT NULL |登録ユーザーID|この設定を行ったユーザーのID。|
|regdate|DateTime|NOT NULL |データ作成日||
|update_user_id|Text|NOT NULL |更新ユーザーID|この設定を行ったユーザーのID。|
|lastupdate|DateTime|NOT NULL |最終更新日||

