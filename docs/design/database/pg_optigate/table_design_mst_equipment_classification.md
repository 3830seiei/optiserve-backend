# テーブル定義書

## テーブル名: mst_equipment_classification

医療機関別と公開用（共通）の医療機器分類を管理するマスタテーブル

|カラム名|型|制約|説明|補足事項|
|:--|:--|:--|:--|:--|
|classification_id|Integer|PK NOT NULL |機器分類ID||
|medical_id|Integer||医療機関ID|医療機関ID。医療機関別の分類の場合は設定される。NULLの場合は公開用の分類。|
|classification_level|Integer|NOT NULL |レベル（分類の階層）|分類の階層を示す。1 : 大分類、 2 : 中分類、3 : 小分類。|
|classification_name|Text|NOT NULL |機器分類名|機器分類の名前。|
|parent_classification_id|Integer||親となる機器分類ID|親となる機器分類のID。NULLの場合は最上位の分類。|
|publication_classification_id|Integer||公開用の機器分類ID|公開用の機器分類ID。医療機関別の分類の場合は基本的に設定されるが分類できないものはNULL。公開用の機器分類の場合はNULL。|
|reg_user_id|Text|NOT NULL |登録ユーザーID|このレコードの登録を行ったユーザーのID。|
|regdate|DateTime|NOT NULL |データ作成日||
|update_user_id|Text|NOT NULL |更新ユーザーID|このレコードの更新を行ったユーザーのID。|
|lastupdate|DateTime|NOT NULL |最終更新日||


### インデックス

- **idx_mst_equipment_classification_medical_id**: medical_id

- **idx_mst_equipment_classification_classification_name**: classification_name

