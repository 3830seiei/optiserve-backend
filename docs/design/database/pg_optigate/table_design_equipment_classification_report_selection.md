# テーブル定義書

## テーブル名: equipment_classification_report_selection

レポート出力用の機器分類の選択情報

|カラム名|型|制約|説明|補足事項|
|:--|:--|:--|:--|:--|
|medical_id|Integer|PK NOT NULL |医療機関ID||
|rank|Integer|PK NOT NULL |機器分類の表示順序|レポートの機器分類の表示順序を示す。小さいほど上位に表示される。|
|classification_id|Integer||機器分類ID|レポート出力対象の機器分類ID。NULLの場合は、システムルールに従って自動的に選択される。|
|reg_user_id|Text|NOT NULL |登録ユーザーID|このレコードの登録を行ったユーザーのID。|
|regdate|DateTime|NOT NULL |データ作成日||
|update_user_id|Text|NOT NULL |更新ユーザーID|このレコードの更新を行ったユーザーのID。|
|lastupdate|DateTime|NOT NULL |最終更新日||

