# テーブル定義書

## テーブル名: facility_upload_log

医療機関のデータアップロード履歴テーブル

|カラム名|型|制約|説明|補足事項|
|:--|:--|:--|:--|:--|
|uploadlog_id|Integer|PK NOT NULL |アップロードログID||
|medical_id|Integer|NOT NULL |医療機関ID||
|file_type|Integer|NOT NULL |アップロードされたファイルの種類|アップロードされたファイルの種類。1: 医療機器台帳, 2: 貸出履歴, 3: 故障履歴。|
|file_name|Text|NOT NULL |アップロードされたファイル名|アップロードされたファイルの名前。|
|upload_datetime|DateTime|NOT NULL |アップロード日時|アップロードが行われた日時|
|upload_user_id|Text|NOT NULL |アップロードを行ったユーザーID|アップロードを行ったユーザーのID。ユーザーマスタのuser_idと紐づく。|
|download_datetime|DateTime||システム側でのダウンロード日時|システム側でのダウンロードが行われた日時。ダウンロードが行われていない場合はNULL。|
|reg_user_id|Text|NOT NULL |登録ユーザーID|このレコードの登録を行ったユーザーのID。|
|regdate|DateTime|NOT NULL |データ作成日||
|update_user_id|Text|NOT NULL |更新ユーザーID|このレコードの更新を行ったユーザーのID。|
|lastupdate|DateTime|NOT NULL |最終更新日||


### インデックス

- **idx_facility_upload_log_medical_id_file_type**: medical_id

