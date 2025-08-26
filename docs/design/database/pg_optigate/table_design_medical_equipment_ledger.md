# テーブル定義書

## テーブル名: medical_equipment_ledger

医療機関別機器台帳（オンプレミス側PostgreSQLのtblhpmelistから集約されたデータ）

|カラム名|型|制約|説明|補足事項|
|:--|:--|:--|:--|:--|
|ledger_id|Integer|PK NOT NULL |機器台帳ID|自動採番される台帳レコードの一意識別子|
|medical_id|Integer|NOT NULL |医療機関ID|オンプレミス側PostgreSQL tblhpmelist.hpcodeから取得される医療機関識別子|
|model_number|Text|NOT NULL |メーカー型番|オンプレミス側PostgreSQL tblhpmelist.modelnumberから取得される機器の型番|
|product_name|Text||機器製品名|オンプレミス側PostgreSQL tblhpmelist.productnameのMAX値から取得される製品名|
|maker_name|Text||メーカー名|オンプレミス側PostgreSQL tblhpmelist.makernameのMAX値から取得されるメーカー名|
|classification_id|Integer||機器分類ID|user_entity_link.analiris_classification_levelの分類レベルに対して、オンプレミス側PostgreSQL tblhpmelist.equipmentclassificationのMAX値から取得される機器分類|
|stock_quantity|Integer|NOT NULL |台帳保有台数|オンプレミス側PostgreSQL tblhpmelistでCOUNT(*)により集計された保有台数|
|is_included|Boolean|NOT NULL |分析対象に含めるか|true: 分析対象に含める, false: 分析対象外|
|reg_user_id|Text|NOT NULL |登録ユーザーID|このレコードの登録を行ったユーザーのID。|
|regdate|DateTime|NOT NULL |データ作成日|レコードの作成日時|
|update_user_id|Text|NOT NULL |更新ユーザーID|このレコードの更新を行ったユーザーのID。|
|lastupdate|DateTime|NOT NULL |最終更新日|レコードの最終更新日時|


### インデックス

- **idx_medical_equipment_medical_id**: medical_id

- **idx_medical_equipment_model**: medical_id, model_number

- **idx_medical_equipment_maker**: maker_name

