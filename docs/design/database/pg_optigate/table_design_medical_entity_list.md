# テーブル定義書

## テーブル名: medical_entity_list

医療機関別の医療機器台帳

|カラム名|型|制約|説明|補足事項|
|:--|:--|:--|:--|:--|
|equipment_id|Integer|PK NOT NULL |医療機器ID|医療機関に関係無く一意な医療機器のID。連番で管理される。|
|medical_id|Integer|NOT NULL |医療機関ID||
|facility_equipment_number|Text|NOT NULL |医療機関システムが管理する機器番号|基本的にmedical_id内では一意であることが期待される。|
|classification_id_level1|Integer|NOT NULL |医療機器分類ID（レベル1）|医療機器分類のレベル1（大分類）ID|
|classification_id_level2|Integer||医療機器分類ID（レベル2）|医療機器分類のレベル2（中分類）ID（オプション）|
|classification_id_level3|Integer||医療機器分類ID（レベル3）|医療機器分類のレベル3（小分類）ID（オプション）|
|jahid_product_id|Integer||医療機器のJAHID製品ID|医療機器のJAHID製品ID（オプション）|
|medie_product_id|Integer||医療機器のMedie製品ID|医療機器のMedie製品ID（オプション）|
|product_name|Text|NOT NULL |医療機器の製品名|医療機器の製品名（必須）|
|product_maker_name|Text||医療機器の製造業者名|医療機器の製造業者名（オプション）|
|date_purchase|Date||医療機器の購入日|医療機器の購入日（オプション）|
|date_disposal|Date||医療機器の廃棄日|医療機器の廃棄日（オプション）|
|regdate|DateTime|NOT NULL |データ作成日||
|lastupdate|DateTime|NOT NULL |最終更新日||


### インデックス

- **idx_medical_entity_list_medical_id_facility_equipment_number**: medical_id, facility_equipment_number

