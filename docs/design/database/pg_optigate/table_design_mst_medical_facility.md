# テーブル定義書

## テーブル名: mst_medical_facility

医療機関マスタ（公開データ）

|カラム名|型|制約|説明|補足事項|
|:--|:--|:--|:--|:--|
|medical_id|Integer|PK NOT NULL |医療機関ID||
|medical_name|Text|NOT NULL |医療機関名|医療機関の名称。|
|address_postal_code|Text||医療機関の郵便番号|医療機関の郵便番号（オプション）|
|address_prefecture|Text||医療機関の都道府県|医療機関の都道府県（オプション）|
|address_city|Text||医療機関の市区町村|医療機関の市区町村（オプション）|
|address_line1|Text||医療機関の住所1|医療機関の町名以降・番地（オプション）|
|address_line2|Text||医療機関の住所2|医療機関の建物名等（オプション）|
|phone_number|Text||医療機関の電話番号|医療機関の電話番号（オプション）|
|reg_user_id|Text|NOT NULL |登録ユーザーID|このレコードの登録を行ったユーザーのID。|
|regdate|DateTime|NOT NULL |データ作成日||
|update_user_id|Text|NOT NULL |更新ユーザーID|このレコードの更新を行ったユーザーのID。|
|lastupdate|DateTime|NOT NULL |最終更新日||


### インデックス

- **idx_medical_name**: address_prefecture, medical_name

- **idx_phone_number**: phone_number

- **idx_address_prefecture**: address_prefecture

