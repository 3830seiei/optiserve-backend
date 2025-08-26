# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

- プロジェクトは日本語で進行してください。

## 📘 プロジェクト概要 / Project Overview

OptiServe は医療機関向けの機器管理・レポート出力システムのバックエンド API です。FastAPI を使用し、WSL Ubuntu・macOS 両方での稼働が確認済みです。

### 技術スタック
- **Backend**: FastAPI + SQLAlchemy ORM + Pydantic
- **Database**: SQLite (開発), PostgreSQL (本番予定)
- **Deployment**: Docker + AWS (予定)
- **Testing**: pytest

---

## 🚀 開発コマンド / Development Commands

### ローカル開発サーバー起動
```bash
# 直接起動
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# または startup script 使用
./startup_optiserve.sh
```

### Docker での起動
```bash
# イメージビルド
docker build -t optiserve .

# コンテナ起動
docker run -d --name optiserve_dev -p 8000:8000 optiserve
# または
./start_docker.sh
```

### テスト実行
```bash
# 前提: API サーバーが起動していること (./startup_optiserve.sh)
pytest tests/test_user_api.py -v
```

### データベース関連
```bash
# テーブル情報更新 (自動生成システム利用)
./upgrade_tableinfo.sh       # 本番用
./upgrade_tableinfo_poc.sh   # PoC用
```

---

## 🏗️ アーキテクチャ / Architecture

### ディレクトリ構造
```
src/
├── main.py                  # FastAPI アプリケーションエントリーポイント
├── database.py             # DB 接続設定 (SQLite/PostgreSQL)
├── routers/                # API エンドポイント定義
│   ├── auth.py            # 認証 API (完成)
│   ├── users.py           # ユーザー管理 API (完成)
│   ├── facilities.py      # 医療機関マスタ API (要見直し)
│   └── user_entity_links.py # 組織リンク API (要見直し)
├── models/pg_optigate/    # SQLAlchemy ORM モデル (YAML から自動生成)
├── schemas/               # Pydantic スキーマ定義
├── utils/                 # ユーティリティ (パスワード生成等)
└── validators/            # バリデーション ロジック
```

### API 設計原則
- **URL パターン**: `/api/v1/{resource}`
- **認証**: JWT トークンベース (予定)
- **エラーハンドリング**: 共通ミドルウェアで統一
- **バリデーション**: Pydantic スキーマで実装
- **CRUD パターン**: GET (一覧/個別), POST (作成), PUT (更新), DELETE (論理削除)

### データベース設計
- **設計ファイル**: `design/database/pg_optigate/*.yaml`
- **自動生成**: YAML → Alembic マイグレーション + SQLAlchemy モデル + SQL ファイル
- **開発環境**: SQLite (`poc_optigate.db`)
- **本番環境**: PostgreSQL (予定)

---

## 🎯 現在の開発状況 / Current Development Status

### 完成済み
- `auth.py`: ログイン認証 API
- `users.py`: ユーザー CRUD API
- `user_entity_links.py`: ユーザー組織連携 API (複合主キー対応、バリデーション実装済み)
- テスト: `test_user_api.py`, `test_user_entity_links_api.py` で一連フローのテスト完了

### 検討中・未実装
- `facilities.py`: 医療機関マスタ管理 API (要見直し)
- **ファイルアップロード/ダウンロード機能**: 月次運用に対応したファイル管理システム (後述)

---

## 🔧 開発時の注意点 / Development Notes

### コーディング規約
- **統一性**: 既存の `auth.py`, `users.py` の構成に準拠
- **エラーメッセージ**: 日本語でユーザーフレンドリー
- **API ドキュメント**: 日英両言語でのドキュメント記述
- **命名規則**: スネークケース (Python), ケバブケース (URL)

### データベース操作
- **ORM 優先**: 直接 SQL は避け、SQLAlchemy ORM を使用
- **トランザション**: 適切な commit/rollback 処理
- **論理削除**: 物理削除ではなく status フラグでの無効化

### テスト方針
- **統合テスト**: API エンドポイントの E2E テスト
- **テストデータ**: ランダム生成で他テストとの干渉回避
- **前提条件**: API サーバー起動が必要

### 設計原則
- **YAML First**: データベース設計は YAML で定義し自動生成
- **スキーマ分離**: Pydantic (API) と SQLAlchemy (DB) の明確な分離
- **バリデーション**: 入力データの厳密なバリデーション実装

---

## 📁 ファイル管理システム / File Management System

### 運用要件
OptiServeでは医療機関からの**月次ファイルアップロード**と**システム生成レポートのダウンロード**機能が必要です。

#### アップロード運用
- **頻度**: 月1回（毎月10日頃までに実施）
- **ファイル種類**: 3種類を同時アップロード
  1. 医療機器台帳 (`file_type=1`)
  2. 貸出履歴 (`file_type=2`)
  3. 故障履歴 (`file_type=3`)
- **上書き**: 同じ医療機関での再アップロードは上書きとする
  - 【運用】別プロセスがアップロードを確認したらダウンロドして世代別の保管を実施
- **通知**: アップロード完了時、`user_entity_link.notification_email_list`のメンバーに自動通知

#### ダウンロード運用
- **レポート生成**: オンプレシステムで月初に自動生成
- **ファイル種類**: 3種類のレポート
  1. 分析レポート (`file_type=1`)
  2. 故障リスト (`file_type=2`)
  3. 未実績リスト (`file_type=3`)
- **通知**: レポート公開時、対象医療機関に自動通知

### データベース設計
既存テーブルを活用:
- **`facility_upload_log`**: アップロードファイルの履歴管理
  - API経由でアップロードされたものは全てログに登録し、ファイル名の変更を行う必要はなし
- **`report_publication_log`**: ダウンロード可能レポートの履歴管理

### ファイル構成（実装済み）
```
files/
├── uploads/                    # 医療機関からのアップロード（1世代保管）
│   └── {medical_id}/
│       ├── equipment.csv       # 医療機器台帳（上書き保存）
│       ├── rental.csv          # 貸出履歴（上書き保存）
│       └── failure.csv         # 故障履歴（上書き保存）
└── reports/                    # システム生成レポート
    └── {medical_id}/
        └── {YYYY-MM}/
            ├── analysis_report.pdf    # 分析レポート
            ├── failure_list.xlsx      # 故障リスト
            └── unachieved_list.xlsx   # 未実績リスト
```

### 実装済み機能
- **FastAPI統合**: 既存APIシステムと統合したファイル管理機能
- **一括アップロード**: 3ファイル同時アップロード対応（上書き保存）
- **履歴管理**: 全てのアップロード実行履歴をDBに記録
- **バリデーション**: ファイル形式・医療機関存在チェック
- **通知機能**: メール通知機能（設計済み・実装予定）

### 実装予定
- **レポート配信**: システム生成レポートの自動公開・配信
- **AWS対応**: 将来的にS3 + CloudFrontでの配信に対応可能な設計

## mst_equipment_classification テーブルのレコードを作成する

design/database/pg_optigate/mst_equipment_classification.yaml参照

### 情報元となるPostgresql

-h 192.168.1.200
-p 5433
-d smdsdb
-U postgres
-W postgres

### 情報元となる情報

select distinct hpcode, bunrui_1, bunrui_2, bunrui_3 from rawhpmelist;

hpcode = 病院コード
bunrui_1 = 大分類
bunrui_2 = 中分類
bunrui_3 = 小分類

病院によって、大分類のみ、大分類＋小分類など組み合わせは様々ですが、中分類を親として大分類が存在するような逆転現象はありません
存在しない場合はNoneの予定ですが、空白、全角空白等があってもNoneと同じ扱いで問題ありません。

### 処理の流れ

- 病院コード毎に大分類、中分類、小分類の順でループ
- sqlite(poc_optigate.db) > mst_equipment_classificationにレコード追加
  - classification_idは連番をセット
  - hpcodeに存在するものはmst_medical_facilityに存在する前提としてチャックを行う必要なし
  - 中分類、小分類はparent_idに関連する大分類のclassification_idをセット
  - publication_classification_idは全てnull
  - regdate, lastupdateは処理の最初にシステム日時を取得したら、全てのレコードで同一
    - 同じタイミングで作成したことが分かるようにしておく

## レポート出力用の機器分類の選択を行うAPIの作成

### 目的

医療機関向けのレポートを作成する際に、デフォルトはシステム側が設定した機器台数多い順ランキングに準じて機器分類が決定するが、equipment_classification_report_selectionテーブルに登録しておくことで、医療機関が確認したい機器分類をレポート出力させることができる。
表示可能なランキング数は、user_entity_link.count_reportout_classificationに準ずる。デフォルトは5でレコート作成されているが、この数字分だけレポートは機器分類の情報を出力する。

その医療機関が優先して閲覧したい機器分類の登録を行う為のAPI。

### 処理の流れ

- レポート出力用の機器分類の選択情報
  - 取得 : 全件取得のみ
    - args : medical_id
    - medical_idの条件を満たすclassification_idをrank順にセット
    - ただし、user_entity_link.count_reportout_classificationまでの数が最大値
    - 最大数もレスポンスに含める
  - 登録 : 全件まとめて登録
    - 送られて来たclassification_idをrank=1から順番に登録
    - 最大数は取得時と同じ
  - 削除 : 全件まとめて削除
    - テーブルから実際にレコードを削除する
- 機器分類情報の提供
  - 取得 : 全件取得のみ
    - args : medical_id
    - mst_equipment_classificationのmedical_idが同じ情報を提供
    - 件数指定あり
      - 001～100件 : /users?skip=0&limit=100
      - 101～200件 : /users?skip=100&limit=100
      - さらに次のリクエストは、skipとlimitを調整して行います。
      - 例えば、次の100件を取得する場合は、**skip=200&limit=100** のようにします。

## システム用のユーザーIDを作成

900001 : システム管理者
900002 : opsman
900003 : SourceWatcher
900004 : DataHub
900005 : DataCuration
900006 : MasterFeed
900007 : PeportMixier
900008 : MedReporter
900009 : TrendMixer
900010 : MarketViewer
900011 : OptiServe Backend
900012 : OptiServe Frontend

## postgresの機器台帳からOptiServe用の機器台帳を準備

- postgresql側は下記条件で取得

```SQL
select hpcode as medical_id,  -- mst_medical_facility.medical_id
  modelnumber as model_number,  -- メーカー型番
  max(productname) as product_name,  -- 機器製品名
  max(makername) as maker_name,   -- メーカー名
  max(bunrui) as bunrui_name,  -- 分類名
  count(*) as stock_quantity  -- 台帳保有台数
from tblhpmelist
where modelnumber <> '不明'
group by hpcode, modelnumber
order by hpcode, count(*) desc;
```

- postgresql側にclassification_idは存在しないので、medical_id, bunrui_nameを利用してsqlite側でclassification_idを取得
- 取得した結果をmedical_equipment_ledgerテーブルに追加
- design/database/pg_optigate/medical_equipment_ledger.yaml が定義ファイルとなる
- reg_user_id, update_user_idは900001を利用

### 2025-08-14 追加

- 機器台帳にis_included項目を追加
- さらに貸出実績と故障実績の存在を確認して、is_included をセット

  ```sql
  select count(*) from tblrentallog where hpcode = 5 and modelnumber = '303';  -- 貸出実績（回数が取得）
  select count(*) from tblrepairlog where hpcode = 5 and modelnumber = '303';  -- 故障実績（回数が取得）
  ```

- 情報のSQLで件数が1以上であれば実績有りなので、is_included = True, 実績が無ければFalseをセット


testsフォルダにpythonスクリプトを作成し実行

## create_equipment_classification.py の見直し

- 現在のSQL だけだと、最終的にtblhpmelist.bunruiにならない

SELECT DISTINCT hpcode, bunrui_1, bunrui_2, bunrui_3
FROM rawhpmelist
ORDER BY hpcode, bunrui_1, bunrui_2, bunrui_3;

- postgresql.mstgroupbunrui というテーブルで、rawhpmelistに存在する機器分類を洗いだして、カナは全角、アルファベットや数字は半角に変換した情報を登録しておき、その値を利用してtblhpmelist.bunruiはセットされている。
- その為、先ほど作成した、medical_equipment_ledgerのbunruitとの紐付けが失敗する

- 対策案1. SQLを見直す

SELECT DISTINCT rhm.hpcode,
	mgb1.grpbunruiname as bunrui_1,
	mgb2.grpbunruiname as bunrui_2,
	mgb3.grpbunruiname as bunrui_3
FROM rawhpmelist rhm
left join mstgroupbunrui mgb1
  on mgb1.grpbunrui = 1 and rhm.bunrui_1 = mgb1.bunruiname
left join mstgroupbunrui mgb2
  on mgb2.grpbunrui = 2 and rhm.bunrui_2 = mgb2.bunruiname
left join mstgroupbunrui mgb3
  on mgb3.grpbunrui = 3 and rhm.bunrui_3 = mgb3.bunruiname

- 対策案2. 現在のSQLはそのままでbunruiをカナは全角、英数字は半角にする

### 2025-08-14 見直し

- 対策SQLは正確で無いと判断
- 従来のSQLで情報を取得

```SQL
SELECT DISTINCT hpcode as medical_id,
        bunrui_1 as 大分類の機器分類名,
        bunrui_2 as 中分類の機器分類名,
        bunrui_3 as 小分類の機器分類名
FROM rawhpmelist
ORDER BY hpcode, bunrui_1, bunrui_2, bunrui_3;
```

- さらに変換情報を取得

```SQL
select distinct bunruiname as 変換前分類名, grpbunruiname as 変換後分類名 from mstgroupbunrui;
```

- 変換情報を、機器分類（大・中・小）と比較してマッチするものは変換
- mst_equipment_classificationに登録

## medical_equipment_analysis_setting 用APIの作成

下記２点を行う為のAPI

1. is_include の更新処理
2. override_classification_id の更新処理

フロントエンドが利用する為には

- 取得対象:
  - mst_equipment_classification で medical_idがユーザーと紐付くレコードを取得
  - classification_id をキーに medical_equipment_analysis_setting を取得
    - is_include : 分析対象
    - override_classification_id : 見直し後機器分類

- 取得条件:
  - 条件が無ければ、同一の医療機関分は全件取得
  - classification_id がパラメータに存在する場合は、classification_idもしくはoverride_classification_idがパラメータと同一ののもを取得
  - 件数指定あり
    - 001～100件 : /users?skip=0&limit=100
    - 101～200件 : /users?skip=100&limit=100
    - さらに次のリクエストは、skipとlimitを調整して行います。
    - 例えば、次の100件を取得する場合は、**skip=200&limit=100** のようにします。

## routers のセキュリティ見直し

- それぞれのroutersのセキュリティを次のように見直し
  - routersの見直し
  - docstringの見直し
  - test_XXX.pyの見直し

- 全体共通:
  - パラメータにmedical_idが含まれている場合、headerのuser_idのmedical_idと等しく無ければ権限エラー
  - 管理者(9)の場合は、全件取得にて全てのレコードが取得出来るが、医療期間の場合は、headerのuser_idのmedical_idと等しく無ければ権限エラーとなる。（ディーラーやメーカーも同一だが、現在存在しないので未対応とする。）
  - 更新時もログインユーザーの医療機関と同一以外を指定されたら権限エラー
  - 管理者のみ可能なものはuser_entity_link.postのように管理者権限を付けてください

- facilities:
  - 追加、更新は9で始まるシステム管理者のみ利用可能
  - 一般ユーザーは閲覧のみ

- users:
  - 追加は9で始まるシステム管理者のみ利用可能
  - 更新は、システム管理者は全てのレコードが可能だが、一般ユーザーは自分の医療機関のみ可能
  - inactive対応もシステム管理者のみ利用可能

- user_entity_link:
  - システム管理者の更新は全項目可能
  - name: analiris_classification_level
  - 一般ユーザーの更新は自分の医療機関のみとし、さらにcount_reportout_classification, analiris_classification_levelについては修正不可能
  　→ 必要ならAPIを分けてください
