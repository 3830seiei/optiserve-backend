# テーブル定義書

## テーブル名: user_entity_link

ユーザーと組織（医療機関・ディーラー・メーカー）の紐付け

|カラム名|型|制約|説明|補足事項|
|:--|:--|:--|:--|:--|
|entity_type|Integer|PK NOT NULL |組織の種別|1: 医療機関, 2: ディーラー, 3: メーカー|
|entity_relation_id|Integer|PK NOT NULL |連携する組織ID|連携する組織のID。entity_typeに応じて医療機関ID、ディーラーID、メーカーIDが入る|
|entity_name|Text|NOT NULL |組織名|表示用に利用する組織名称|
|entity_address_postal_code|Text||組織の郵便番号|組織の郵便番号（オプション）|
|entity_address_prefecture|Text||組織の都道府県|組織の都道府県（オプション）|
|entity_address_city|Text||組織の市区町村|組織の市区町村（オプション）|
|entity_address_line1|Text||組織の住所1|組織の町名以降・番地（オプション）|
|entity_address_line2|Text||組織の住所2|組織の建物名等（オプション）|
|entity_phone_number|Text||組織の電話番号|組織の電話番号（オプション）|
|notification_email_list|JSON|NOT NULL |通知メールアドレス|ユーザーアカウントのメールアドレスは必須。それ以外にレポート配布の通知等の情報を受け取るメールアドレスをJSON形式で格納します。複数のメールアドレスを登録することができます。|
|count_reportout_classification|Integer|NOT NULL |レポート公開の分類数|医療機関向けレポートに、出力させる機器分類数。|
|analiris_classification_level|Integer|NOT NULL |分析レポートの分類レベル|分析レポートで使用する機器分類のレベル。1: 大分類、2: 中分類、3: 小分類。|
|reg_user_id|Text|NOT NULL |登録ユーザーID|このレコードの登録を行ったユーザーのID。|
|regdate|DateTime|NOT NULL |データ作成日||
|update_user_id|Text|NOT NULL |更新ユーザーID|このレコードの更新を行ったユーザーのID。|
|lastupdate|DateTime|NOT NULL |最終更新日||


### インデックス

- **idx_user_entity**: entity_type, entity_relation_id

