# テーブル定義書

## テーブル名: report_publication_log

医療機関向けレポートの公開履歴テーブル

|カラム名|型|制約|説明|補足事項|
|:--|:--|:--|:--|:--|
|publication_id|Integer|PK NOT NULL |レポート公開ID||
|medical_id|Integer|NOT NULL |医療機関ID||
|publication_ym|Text|NOT NULL |レポート公開年月|レポートが公開された年月。|
|file_type|Integer|NOT NULL |公開したファイルの種類|公開したファイルの種類。1: 分析レポート, 2: 故障リスト, 3: 未実績リスト。|
|file_name|Text|NOT NULL |公開したファイル名|公開したファイルの名前。|
|upload_datetime|DateTime|NOT NULL |サイトへの更新日時|サイトへの更新を行った日時|
|download_user_id|Text|NOT NULL |ダウンロードを行ったユーザーID|ダウンロードを行ったユーザーのID。ユーザーマスタのuser_idと紐づく。最初にダウンロードしたユーザーのみ登録される。|
|download_datetime|DateTime||ユーザーのダウンロード日時|ユーザーがファイルのダウンロードを行った日時。ダウンロードが行われていない場合はNULL。最初にダウンロードした日時のみ登録される。|
|reg_user_id|Text|NOT NULL |登録ユーザーID|このレコードの登録を行ったユーザーのID。|
|regdate|DateTime|NOT NULL |データ作成日||
|update_user_id|Text|NOT NULL |更新ユーザーID|このレコードの更新を行ったユーザーのID。|
|lastupdate|DateTime|NOT NULL |最終更新日||


### インデックス

- **idx_report_publication_log_medical_id**: medical_id

- **idx_publication_ym**: publication_ym

