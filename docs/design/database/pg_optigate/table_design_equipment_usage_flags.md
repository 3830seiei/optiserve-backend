# テーブル定義書

## テーブル名: equipment_usage_flags

医療機器の分析使用フラグ管理テーブル

|カラム名|型|制約|説明|補足事項|
|:--|:--|:--|:--|:--|
|medical_id|Integer|PK NOT NULL |医療機関ID||
|equipment_id|Integer|PK NOT NULL |医療機器ID||
|is_active|Boolean|NOT NULL |使用中フラグ|医療機器を集計対象として有効化を示すフラグ。Trueの場合は使用中、Falseの場合は使用中ではない。|
|regdate|DateTime|NOT NULL |データ作成日||
|lastupdate|DateTime|NOT NULL |最終更新日||

