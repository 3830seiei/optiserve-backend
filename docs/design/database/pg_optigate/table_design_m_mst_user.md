# テーブル定義書

## テーブル名: m_mst_user

OptiServe管理のユーザーマスタ

|カラム名|型|制約|説明|補足事項|
|:--|:--|:--|:--|:--|
|user_id|Integer|PK NOT NULL |ユーザーID||
|user_name|Text|NOT NULL |ユーザー名|ユーザーの表示名|
|entity_type|Integer|NOT NULL |組織の種別|1: 医療機関, 2: ディーラー, 3: メーカー|
|entity_relation_id|Integer|NOT NULL |連携する組織ID|連携する組織のID。entity_typeに応じて医療機関ID、ディーラーID、メーカーIDが入る|
|password|Text|NOT NULL |ユーザーパスワード|ユーザーのパスワード（ハッシュ化して保存）|
|e-mail|Text|NOT NULL |メールアドレス|ユーザーのメールアドレス(ログインIDとしても使用)|
|phone_number|Text||電話番号|ユーザーの電話番号（オプション）|
|mobile_number|Text|NOT NULL |携帯電話番号|ユーザーの携帯電話番号（SMSによる二段階認証で利用）|
|proc_type|Integer|NOT NULL |処理種別|0: 仮登録, 1: 登録済み, 9: 退会（使用不可）|
|regdate|DateTime|NOT NULL |データ作成日||
|lastupdate|DateTime|NOT NULL |最終更新日||


### インデックス

- **idx_user_email**: e-mail

- **idx_user_entity**: entity_type, entity_relation_id

