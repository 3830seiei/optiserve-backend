# データベース定義書

## 更新履歴

|Version|Date|Author|Comment|
|:--|:--|:--|:--|

| 1.0.0 | 2025-06-27 | H.Miyazawa | OptiServe用のデータベース設計 |


## データベース情報

### データベース名

**pg_optigate**

### 作成時オプション

PostgreSQLでのデータベース作成時のオプションの各設定値です。

1. OWNER = usr_optigate
    **データベース所有者**:
    - このデータベースを所有するユーザー（ロール）を指定します。

2. ENCODING = 'UTF8'
    **文字エンコーディング**:
    - データベースで使用する文字エンコーディング（例: UTF-8）。

3. LC_COLLATE = ''
    **照合順序（並び替え規則）**
    - データベースで文字列の比較や並び替えに使用するロケール設定。

4. LC_CTYPE = ''
    **文字クラス（文字列の分類）**:
    - データベースで使用する文字列の分類（大文字/小文字の扱い、文字型チェックなど）に関連するロケール設定。

5. ICU_LOCALE = ''
    **ICUロケール**:
    - ICU（International Components for Unicode）を使用したロケールの設定。

6. LOCALE_PROVIDER = ''
    **ロケールプロバイダ**:
    - ロケール情報の提供元を指定（libcまたはicu）。

7. TABLESPACE = pg_default
    **デフォルトテーブルスペース**:
    - このデータベースで使用するデフォルトのテーブルスペースを指定します。

8. CONNECTION LIMIT = -1
    **接続制限**:
    - このデータベースに接続できるクライアント数の制限。-1は無制限。

9. IS_TEMPLATE = False
    **テンプレートデータベースフラグ**:
    - このデータベースを新しいデータベース作成時のテンプレートとして使用可能にするかを指定します。Falseは使用不可。


## テーブル情報

- データベースを構成するテーブル情報です
- 対象のテーブルにどういう目的の情報が登録されるかグループ分けしてあります


### [OptiServe管理] グループ



|テーブル名|説明|
|:--|:--|

| mst_user | OptiServe管理のユーザーマスタ |


| user_entity_link | ユーザーとエンティティの紐付け |


| equipment_usage_flags | 医療器機の集計使用対象にするかのフラグ管理 |


| facility_upload_log | 医療機関のファイルアップロード履歴 |


| report_publication_log | 医療機関向けレポートの公開履歴 |


| equipment_classification_report_selection | レポート出力対象の機器分類選択情報 |



### [外部提供テーブル] グループ



|テーブル名|説明|
|:--|:--|

| mst_medical_facility | 医療機関マスタ（公開データ） |


| medical_equipment_list | 医療機関の機器台帳 |


| mst_equipment_classification | 機器分類マスタ |



