# テーブル定義書

## テーブル名: mst_user

OptiServe管理のユーザーマスタ

|カラム名|型|制約|説明|補足事項|
|:--|:--|:--|:--|:--|
|user_id|Text|PK NOT NULL |ユーザーID|entity_typeに応じてユニークな値をシステムにて定義。
システム : 900001 - 999999
医療機関 : 100001 - 199999
ディーラー : 200001 - 299999
メーカー : 300001 - 399999
|
|user_name|Text|NOT NULL |ユーザー名|ユーザーの表示名|
|entity_type|Integer|NOT NULL |組織の種別|1: 医療機関, 2: ディーラー, 3: メーカー, 9:管理者権限|
|entity_relation_id|Integer|NOT NULL |連携する組織ID|連携する組織のID。entity_typeに応じて医療機関ID、ディーラーID、メーカーIDが入る。管理者時は0がセットされる。|
|password|Text|NOT NULL |ユーザーパスワード|ユーザーのパスワード（ハッシュ化して保存）|
|e_mail|Text|NOT NULL |メールアドレス|ユーザーのメールアドレス(ログインIDとしても使用)|
|phone_number|Text||電話番号|ユーザーの電話番号（オプション）|
|mobile_number|Text|NOT NULL |携帯電話番号|ユーザーの携帯電話番号（SMSによる二段階認証で利用）|
|user_status|Integer|NOT NULL |ユーザーステータス|0: temporary, 1: active, 9: inactive|
|inactive_reason_code|Integer||無効化理由コード|ユーザーが無効化された理由コード（1:組織退会, 2:組織の担当者変更, 3:処理ミス, 99:その他）|
|inactive_reason_note|Text||無効化理由メモ|ユーザー無効化の理由メモ（任意）|
|reg_user_id|Text|NOT NULL |登録ユーザーID|このレコードの登録を行ったユーザーのID。|
|regdate|DateTime|NOT NULL |データ作成日||
|update_user_id|Text|NOT NULL |更新ユーザーID|このレコードの更新を行ったユーザーのID。|
|lastupdate|DateTime|NOT NULL |最終更新日||


### インデックス

- **idx_user_email**: e-mail

- **idx_user_entity**: entity_type, entity_relation_id

