# CLAUDE.md

このファイルは Claude Code (claude.ai/code) がこのリポジトリで作業を行う際のガイダンスを提供します。

- プロジェクトは日本語で進行してください。
- markdownの追記をする時は、markdownlintのエラーになら無い記述を希望
  - 見出しの行の下は必ず１行開ける
  - urlは[]で囲む
  - tree構成を表示する時は```plaintext ... ``` で囲む

## 📘 プロジェクト概要 / Project Overview

OptiServe は医療機関向けの機器管理・レポート出力システムのバックエンド API です。FastAPI を使用し、WSL Ubuntu・macOS 両方での稼働が確認済みです。

### 技術スタック

- **Backend**: FastAPI + SQLAlchemy ORM + Pydantic
- **Database**: SQLite (開発), PostgreSQL (本番予定)
- **Deployment**: Docker + AWS (予定)
- **Testing**: pytest (40/40 テスト通過)

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

# 全テスト実行
pytest tests/ -v  # -s でprint文を表示

# 異常終了でテスト終了
pytest tests/ -v -x

# 前回の異常終了からの継続
pytest tests/ --last-failed -v -x
```

### データベース関連

- データベースはyamlファイルでデザインした後で、各種ファイルやAlembicファイルの自動生成を行っている

```bash
# テーブル情報更新 (自動生成システム利用)
./upgrade_tableinfo.sh       # 本番用
./upgrade_tableinfo_poc.sh   # PoC用
```

### 🔄 動作環境切り替え / Environment Switching

OptiServeは異なるOS環境間での動作をサポートしています。パス設定は自動的に環境を判定して最適化されます。

#### 対応OS環境

- **macOS**: `/Users/smds/develop/optiserve-backend`
- **WSL Ubuntu**: `/home/smds/projects/optiserve-backend`
- **Docker Container**: `/app`
- **その他Linux**: `/app`

#### 自動環境判定の仕組み

```python
# src/utils/path_config.py による自動判定
# 1. 環境変数 OPTISERVE_BASE_PATH が設定されていれば優先使用
# 2. OS判定による自動設定:
#    - macOS (Darwin): /Users/smds/develop/optiserve-backend
#    - WSL Ubuntu: /home/smds/projects/optiserve-backend
#    - Linux Container: /app
```

#### 環境切り替え手順

##### 1. macOS → WSL Ubuntu への移行

```bash
# 1. プロジェクトファイルをWSL環境にコピー
# (Windows側で実行)
cp -r /mnt/c/path/to/optiserve-backend /home/smds/projects/optiserve-backend

# 2. WSL Ubuntu環境でディレクトリ移動
cd /home/smds/projects/optiserve-backend

# 3. Python仮想環境設定
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. 環境確認（自動的にWSL用パスが設定される）
python -c "from src.utils.path_config import path_config; print(path_config.get_config_info())"

# 5. データベース初期化
./upgrade_tableinfo_poc.sh

# 6. サーバー起動
./startup_optiserve.sh
```

##### 2. 手動パス指定による環境設定

```bash
# 環境変数による明示的パス指定
export OPTISERVE_BASE_PATH="/custom/path/to/optiserve"

# 設定確認
python -c "from src.utils.path_config import path_config; print(path_config.base_path)"
```

##### 3. Docker環境での実行

```bash
# Dockerfileでの環境設定例
ENV OPTISERVE_BASE_PATH="/app"

# または実行時指定
docker run -e OPTISERVE_BASE_PATH="/app" -p 8000:8000 optiserve
```

#### 環境固有の設定ファイル

各環境で以下のパスが動的に設定されます：

- **データベースファイル**: `{BASE_PATH}/poc_optigate.db`
- **ファイル管理**: `{BASE_PATH}/files/`
- **アップロード**: `{BASE_PATH}/files/uploads/`
- **レポート**: `{BASE_PATH}/files/reports/`
- **データ**: `{BASE_PATH}/data/`
- **オンプレレポート**: `{BASE_PATH}/data/onpre_reports/`
- **ログ**: `{BASE_PATH}/log/`

#### トラブルシューティング

```bash
# パス設定の確認
python -c "
from src.utils.path_config import path_config
from src.utils.config_loader import get_config_info
import json
print('=== Path Config ===')
print(json.dumps(path_config.get_config_info(), indent=2))
print('=== Config Loader ===')
print(json.dumps(get_config_info(), indent=2))
"

# 必要ディレクトリの手動作成
python -c "from src.utils.path_config import path_config; path_config.ensure_directories()"

# データベース接続テスト
python -c "from src.database import DATABASE_URL, engine; print(f'DATABASE_URL: {DATABASE_URL}')"
```

---

## 🏗️ アーキテクチャ / Architecture

### ディレクトリ構造

```plaintext
src/
├── main.py                  # FastAPI アプリケーションエントリーポイント
├── database.py             # DB 接続設定 (SQLite/PostgreSQL)
├── routers/                # API エンドポイント定義 (全て実装完了)
│   ├── auth.py            # 認証 API (完成)
│   ├── users.py           # ユーザー管理 API (完成)
│   ├── facilities.py      # 医療機関マスタ API (完成)
│   ├── user_entity_links.py       # 組織リンク API (完成)
│   ├── file_management.py          # ファイル管理 API (完成)
│   ├── equipment_classifications.py # 機器分類 API (完成)
│   └── medical_equipment_analysis.py # 機器分析設定 API (完成)
├── models/pg_optigate/    # SQLAlchemy ORM モデル (YAML から自動生成)
├── schemas/               # Pydantic スキーマ定義
├── utils/                 # ユーティリティ (パスワード生成、認証管理、パス設定等)
│   ├── auth.py            # 認証・認可管理
│   ├── password.py        # パスワード生成
│   ├── path_config.py     # OS環境に応じた動的パス設定 (v1.1.0)
│   └── config_loader.py   # 設定ファイル動的ローダー (v1.1.0)
└── validators/            # バリデーション ロジック

tests/
├── test_user_api.py                      # ユーザー管理APIテスト (完成)
├── test_user_entity_links_api.py        # 組織リンクAPIテスト (完成)
├── test_05_file_management_api.py       # ファイル管理APIテスト (完成)
├── test_06_equipment_classifications_api.py  # 機器分類APIテスト (完成)
└── test_07_medical_equipment_analysis_api.py # 機器分析APIテスト (完成)
```

### API 設計原則

- **URL パターン**: `/api/v1/{resource}`
- **認証**: X-User-Id ヘッダーベース + 医療機関権限チェック
- **エラーハンドリング**: HTTPException を使用した統一エラーレスポンス
- **バリデーション**: Pydantic スキーマで実装
- **CRUD パターン**: GET (一覧/個別), POST (作成), PUT (更新), DELETE (論理削除)
- **権限管理**: AuthManager による統一認証・認可システム

### データベース設計

- **設計ファイル**: `design/database/pg_optigate/*.yaml`
- **自動生成**: YAML → Alembic マイグレーション + SQLAlchemy モデル + SQL ファイル
- **開発環境**: SQLite (`poc_optigate.db`)
- **本番環境**: PostgreSQL (予定)

---

## 🎯 実装完了状況 / Implementation Status

### ✅ 完成済み API

- **`auth.py`**: ログイン認証 API
- **`users.py`**: ユーザー CRUD API (権限管理対応)
- **`facilities.py`**: 医療機関マスタ管理 API
- **`user_entity_links.py`**: ユーザー組織連携 API (複合主キー対応)
- **`file_management.py`**: 月次ファイルアップロード/ダウンロード API
- **`equipment_classifications.py`**: 機器分類マスタ管理 API
- **`medical_equipment_analysis.py`**: 機器分析設定上書き管理 API

### ✅ 完成済みテスト

- **テスト対象**: 全 7 つの API モジュール
- **テスト状況**: 40/40 テスト通過（100% パス率）
- **テスト範囲**: CRUD 操作、権限チェック、エラーハンドリング、統合テスト

### ✅ 権限管理システム

- **AuthManager**: 統一認証・認可クラス実装
- **システム管理者**: user_id 900001-999999（全医療機関アクセス可能）
- **医療機関ユーザー**: 自医療機関のみアクセス可能
- **権限チェック**: 全 API で一貫した権限管理を実装

---

## 📁 ファイル管理システム / File Management System

### 運用要件 (実装完了)

OptiServeでは医療機関からの**月次ファイルアップロード**と**システム生成レポートのダウンロード**機能を提供します。

#### アップロード運用

- **頻度**: 月1回（毎月10日頃までに実施）
- **ファイル種類**: 3種類を同時アップロード
  1. 医療機器台帳 (`file_type=1`)
  2. 貸出履歴 (`file_type=2`)
  3. 故障履歴 (`file_type=3`)
- **上書き**: 同じ医療機関での再アップロードは上書きとする
- **通知**: アップロード完了時、`user_entity_link.notification_email_list`のメンバーに自動通知

#### ダウンロード運用

- **レポート生成**: オンプレシステムで月初に自動生成
- **ファイル種類**: 3種類のレポート
  1. 分析レポート (`file_type=1`)
  2. 故障リスト (`file_type=2`)
  3. 未実績リスト (`file_type=3`)
- **通知**: レポート公開時、対象医療機関に自動通知

### ファイル構成（実装済み）

```plaintext
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

---

## 🔧 実装済み機能詳細 / Implemented Features

### 機器分類管理

- **mst_equipment_classification**: 医療機関ごとの機器分類マスタ
- **階層構造**: 大分類・中分類・小分類の3階層対応
- **API**: 分類の取得、ページング対応

### 機器分析設定

- **医療機器台帳**: PostgreSQL から移行した機器台帳データ
- **分析対象上書き**: デフォルト設定に対する医療機関別上書き設定
- **分類上書き**: 医療機関独自ルールによる分類変更設定
- **履歴管理**: 変更理由と実施者の記録
- **差分管理**: デフォルト値と同じ設定は保存せず効率化

### レポート出力用機器分類選択

- **equipment_classification_report_selection**: レポート出力対象分類の選択
- **ランキング制御**: `user_entity_link.count_reportout_classification` による出力数制御
- **優先順位**: 医療機関が確認したい機器分類の優先順位設定

---

## 🔐 セキュリティ設計 / Security Design

### 権限管理

- **システム管理者権限**: 9で始まるユーザーID（900001-999999）
- **医療機関権限**: entity_type=1 で自医療機関のみアクセス可能
- **パラメータチェック**: medical_id パラメータと認証ユーザーの医療機関一致確認

### API セキュリティ

- **認証ヘッダー**: X-User-Id による統一認証
- **権限チェック**: 全エンドポイントで適切な権限確認
- **エラーハンドリング**: 権限エラー時の適切なレスポンス

---

## 📊 データ移行システム / Data Migration System

### PostgreSQL からの移行 (実装完了)

- **機器分類データ**: rawhpmelist + mstgroupbunrui からの分類情報移行
- **機器台帳データ**: tblhpmelist からの機器情報移行
- **実績データ確認**: 貸出実績・故障実績の存在確認による is_included 設定
- **システムユーザー**: 900001-900012 のシステム用ユーザー作成済み

---

## 📝 今後の開発予定 / Future Development Plan

### 1. バックエンド仕様書 (`design/backend/`)

- **API仕様書** (`design/backend/api/`)
  - 全7つのAPIモジュールの詳細仕様
  - リクエスト/レスポンス仕様
  - エラーケース定義
- **プロセス仕様書**
  - ファイル処理フロー
  - データ移行プロセス
  - レポート生成プロセス
- **データベース設計書** (既存YAML活用)

### 2. フロントエンド仕様書 (`design/frontend/`)

- **画面仕様書**
  - ユーザー画面設計
  - 管理者画面設計
- **機能仕様書**
  - ファイルアップロード画面
  - 機器分析設定画面
  - レポート表示画面
- **ユーザビリティ設計書**

### 3. コンテナデプロイ

- **Dockerコンテナ見直し**
- **AWS展開準備**
  - ECS/Fargate 対応
  - RDS PostgreSQL 接続
  - S3 + CloudFront ファイル管理

### 4. ドキュメント管理方針

- **言語**: 日本語で作成し、英語は後から併記
- **形式**: 同一ファイル内で日英両言語対応
- **更新**: 実装と同期したドキュメント更新

---

## 🎯 開発時の注意点 / Development Notes

### コーディング規約

- **統一性**: 既存の API 実装パターンに準拠
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
- **前提条件**: API サーバー起動が必要（./startup_optiserve.sh）
- **完全性**: 全機能のテストカバレッジ確保

### 設計原則

- **YAML First**: データベース設計は YAML で定義し自動生成
- **スキーマ分離**: Pydantic (API) と SQLAlchemy (DB) の明確な分離
- **バリデーション**: 入力データの厳密なバリデーション実装
- **権限管理**: AuthManager による統一認証・認可

---

## 🚀 システム起動方法 / System Startup

### 開発環境セットアップ

```bash
# 1. API サーバー起動
./startup_optiserve.sh

# 2. テスト実行で動作確認
pytest tests/ -v

# 3. API ドキュメント確認
# http://localhost:8000/docs にアクセス
```

### プロダクション環境 (予定)

```bash
# Docker コンテナでの起動
docker-compose up -d

# PostgreSQL 接続設定
# 環境変数で DATABASE_URL を設定
```

---

## 📋 プログラム仕様書章構成パターン / Program Specification Chapter Patterns

共通の章立てとして統一することで、文書の整合性と可読性を向上させます。

### 統一章構成 (12章構成)

1. **概要 / Overview**
2. **システム構成 / System Architecture**
3. **関連ファイル / Related Files**
4. **API仕様 / API Specifications**
5. **データモデル / Data Models**
6. **機能詳細 / Functional Details**
   - 6.1 業務フロー / Business Flow
   - 6.2 権限管理 / Permission Management
   - 6.3 バリデーション / Validation
   - 6.4 エラーハンドリング / Error Handling
   - 6.5 データベース連携 / Database Integration
   - 6.6 その他機能固有詳細 / Other Function-Specific Details
7. **セキュリティ考慮事項 / Security Considerations**
8. **パフォーマンス考慮事項 / Performance Considerations**
9. **テスト項目 / Test Cases**
10. **今後の拡張予定 / Future Enhancements**
11. **運用考慮事項 / Operational Considerations**
12. **関連資料 / Related Documents**

---

## 📚 関連資料 / Related Documents

- **API仕様**: [http://localhost:8000/docs] (Swagger UI)
- **データベース設計**: `design/database/pg_optigate/*.yaml`
- **プログラム仕様書**: `design/backend/proc/*.md` (7ファイル完成)
- **テスト結果**: 40/40 テスト通過
- **実装状況**: 全 API モジュール実装完了

---

## 📞 サポート / Support

プロジェクトに関する質問や問題については、実装済みのテストケースと API ドキュメントを参照してください。
すべての機能が実装され、テストが通過している状態です。

---

## 🎨 フロントエンド仕様・画面設計情報 / Frontend Specifications & Screen Design

### 📱 対応画面・機能一覧 / Screen and Functionality List

#### 認証・ユーザー管理系 / Authentication & User Management

- **ログイン画面** (ui_login.md) - 完成済み
- **ユーザーマスタメンテナンス画面** (ui_user_master_maintenance.md) - 完成済み

#### ファイル管理系 / File Management

- **ファイルアップロード画面**
  - 機能：月次ファイル（機器台帳・貸出履歴・故障履歴）のアップロード
  - API連携：`/api/v1/file-management/upload` (医療機関用)
  - ユーザー：医療機関担当者
  - 特徴：3種類ファイル同時アップロード、上書き対応、通知機能
  - 補足：
    - 最初に直近6ヶ月のアップロード履歴を表示
    - アップロードが完了したら、最新のアップロード履歴を取得して画面を更新

- **レポートダウンロード画面**
  - 機能：システム生成レポート（分析レポート・故障リスト・未実績リスト）のダウンロード
  - API連携：`/api/v1/file-management/download` (医療機関用)
  - ユーザー：医療機関担当者
  - 特徴：月次レポート一覧表示、ファイル種別選択、ダウンロード実行
  - 補足：
    - 最初に直近6ヶ月のダウンロード履歴を表示
    - ダウンロードが完了したら、最新のダウンロード履歴を取得して画面を更新
    - レポートのダウンロードは、最新でなくても年月を指定すれば取得可能
      - デフォルトは最新年月分

- **システムファイル管理画面（管理者用）**
  - 機能：レポートファイルのシステム側アップロード
  - API連携：`/api/v1/file-management/system-upload` (システム用)
  - ユーザー：システム管理者・オンプレシステム
  - 特徴：月次レポートの自動配布、通知機能
  - 補足：
    - このAPIはpythonの別プロセスから利用するだけなので、作成不要です

#### 機器管理・分析系 / Equipment Management & Analysis

- **機器分析設定画面**
  - 機能：医療機器分析設定の上書き管理（分析対象フラグ・分類上書き）
  - API連携：`/api/v1/medical-equipment-analysis-settings`
  - ユーザー：医療機関担当者・システム管理者
  - 特徴：差分管理システム、変更履歴記録、デフォルト値との比較、一括復帰機能
  - 補足：
    - 「差分」だと利用者がわかりにくいので、とりあえず「上書き」にしたが、システム標準の機器分類に対して、病院の独自ルールに置換して分析する機能、という意味から分かりやすい名前と説明を考えてください

- **機器分類管理画面**
  - 機能：機器分類マスタの参照・レポート出力選択設定
  - API連携：`/api/v1/equipment-classifications`
  - ユーザー：医療機関担当者・システム管理者
  - 特徴：3階層分類構造、ページネーション対応、権限別表示制御
  - 補足：
    - なし

- **レポート分類選択設定画面**
  - 機能：レポート出力対象機器分類の選択・優先順位設定
  - API連携：`/api/v1/equipment-classifications/report-selection`
  - ユーザー：医療機関担当者
  - 特徴：優先順位管理、選択数制限（user_entity_link.count_reportout_classification基準）
  - 補足：
    - なし

#### システム管理系 / System Management

- **医療機関マスタ管理画面**
  - 機能：医療機関情報のCRUD操作（登録・参照・更新・論理削除なし）
  - API連携：`/api/v1/facilities`
  - ユーザー：システム管理者（全件）・医療機関ユーザー（自医療機関のみ）
  - 特徴：権限別アクセス制御、ページネーション対応、検索機能
  - 補足：
    - 医療機関マスタの実操作はシステム管理者のみとする
      - 一般ユーザーがメンテナンスする場合は、user-entity-linkへの反映とする
      - バックエンド側に一般ユーザーからの更新APIも残しておくが、現時点では利用しない
      - 本番運用の流れの整理:
        1. DataHubが厚生労働省提供の医療機関情報をオンプレ側DBに保管
        2. 医療機関のSMDS登録時は厚生労働省の情報を利用して新規登録
            - 今は厚生労働省の情報テーブルが無いので画面から手作業入力
            - ✅ 最終的にはオンプレ側の情報を利用して更新する仕組みを検討
        3. 厚生労働省データに登録している以外の住所等の利用はuser_entity_link側の情報を修正
    - 一般ユーザーの利用は無し
      - 他の画面から医療機関の情報取得にはuser_entity_listを利用する

- **組織連携管理画面**
  - 機能：ユーザー組織連携情報の管理（複合主キー対応）
  - API連携：`/api/v1/user-entity-links`
  - ユーザー：システム管理者
  - 特徴：複合主キー（user_id + entity_type）管理、通知設定管理、権限管理
  - 補足：
    - user_entity_linksの追加処理は、ui_user_master_maintenanceの追加処理が行われた時に作成
      - ただし、既に存在すれば存在するレコードを利用するので追加不要
    - 画面を開くタイミングで取得を行い表示させる
    - 一般ユーザーと管理者で取得条件が異なるので注意

- **ユーザーマスタ管理画面**
  - 機能：ユーザー情報のCRUD操作・仮登録・利用停止処理
  - API連携：`/api/v1/users`
  - ユーザー：システム管理者（全ユーザー）・医療機関ユーザー（同一医療機関内）
  - 特徴：user_id採番範囲管理、権限管理、パスワード生成、利用停止履歴
  - 補足：
    - 全体のルールから考えるなら、ui_user_master_maintenanceから改名した方が良いかも
    - 同じ機能なので、2つに分かれないこと
    - 既に配布している仕様書なので、扱いに注意（1.1で対応済み）

### 🔧 画面共通仕様 / Common Screen Specifications

#### 認証方式 / Authentication Method

- **認証ヘッダー**: `X-User-Id` による統一認証
- **権限管理**:
  - システム管理者 (user_id: 900001-999999): 全医療機関データアクセス可能
  - 医療機関ユーザー (entity_type=1): 自医療機関データのみアクセス可能

#### エラーハンドリング / Error Handling

- **403 Forbidden**: アクセス権限なし
- **404 Not Found**: データ不存在
- **422 Unprocessable Entity**: バリデーションエラー
- **500 Internal Server Error**: サーバーエラー

#### UI/UX ガイドライン / UI/UX Guidelines

- **メッセージ表示**: 画面右下トースト通知または上部アラート表示
- **フォームバリデーション**: フィールド下部または横に赤字エラー表示
- **ページング**: skip/limitパラメータ、通常20-100件単位
- **確認ダイアログ**: 重要操作時の確認プロンプト表示

#### 技術仕様 / Technical Specifications

- **フロントエンド**: Next.js/React SPA
- **バックエンド**: FastAPI + SQLAlchemy ORM + Pydantic
- **通信**: REST API (JSON)、axios/fetch使用
- **認証**: `X-User-Id`ヘッダー方式（将来的にJWT/Cookie検討）
- **開発環境API**: `http://192.168.99.118:8000`
- **本番環境**: AWS (ECS/Fargate + RDS PostgreSQL + S3/CloudFront)
- **データベース**: SQLite（開発）→ PostgreSQL（本番）

### 🗂️ 既存画面モック・仕様書 / Existing Screen Mocks & Specifications

#### 利用可能なモック画面 / Available Mock Screens

- `design/frontend/assets/mock_login.png`: ログイン画面
- `design/frontend/assets/mock_user-maintenance.png`: ユーザーマスタメンテナンス画面

#### API仕様書対応画面 / API-Based Screen Specifications

- 全7つのAPI仕様書 (`design/backend/api/*.md`) に対応する画面設計が必要
- 各画面はFastAPI + SQLAlchemy ORMのREST API連携を前提として設計
- Next.js/React SPA構成でのフロントエンド実装を想定

### 🔄 画面遷移フロー / Screen Navigation Flow

#### 基本遷移パターン / Basic Navigation Pattern

1. **ログイン** → **メインメニュー** → **各機能画面**
2. **権限チェック** → **403エラー** または **画面表示**
3. **CRUD操作** → **確認ダイアログ** → **API実行** → **結果表示**

#### 画面グループ別遷移 / Navigation by Screen Groups

**認証フロー**:

```plaintext
ログイン画面 → next_action判定
├─ show_main_menu: メインメニュー
├─ show_user_registration: ユーザー情報更新画面
├─ inactive: 利用停止メッセージ
└─ error: エラー画面
```

**ファイル管理フロー**:

```plaintext
メインメニュー
├─ ファイルアップロード画面 → 3種ファイル同時アップロード → 通知送信 → 履歴更新
└─ レポートダウンロード画面 → 月次レポート選択 → ダウンロード実行
```

- 補足：
  - 不要と判断
    - システムファイル管理画面（管理者用） → レポート配布 → 通知送信

**機器管理フロー**:

```plaintext
メインメニュー
├─ 機器分析設定画面 → 差分管理による上書き設定 → 変更履歴記録
├─ 機器分類管理画面 → 3階層分類参照 → ページング表示
└─ レポート分類選択設定画面 → 優先順位設定 → 選択数制限チェック → 保存
```

- 相談：
  - レポートで利用する機器分類はuser_entity_link.analiris_classification_levelで定義された分類です
  - 機器分類の上書きを行う対象はその分類のみとなります
    - そのmedical_idの機器分類に大分類、中分類、小分類全てのグループ構成が設定されているとしても、表示・変更が可能なのは、定義された分類レベルのみ
  - user_entity_link側でanaliris_classification_levelの設定を変更した場合は、初期化(Delete)を行う
  - ただし、上のランクの分類が異なっても、対象の分類で名称が一致することはあるので、対象の分類とそれを含める親グループの表示までは行う必要がある
  - ここのインターフェース案がまだ出来ていない

**システム管理フロー（管理者のみ）**:

```plaintext
メインメニュー
├─ ユーザーマスタ管理画面 → CRUD操作 → 権限チェック → user_id採番
└─ 医療機関マスタ管理画面 → CRUD操作（論理削除なし） → 権限チェック
```

- 補足：
  - 通知の機能は現状未対応
    - 組織連携管理画面 → 複合主キー管理 → 通知設定 → 権限割当

### 📋 フロントエンド仕様書テンプレート構造 / Frontend Specification Template Structure

#### 標準章構成 (12章構成)

1. **画面名称 / Screen Title** - 日英併記、機能ID定義
2. **機能概要 / Function Overview** - 日英併記の機能説明
3. **画面利用対象ユーザー / Target Users** - 権限別利用者定義
4. **運用概要 / Operational Usage** - 業務的背景・利用目的
5. **処理の流れ / Processing Flow** - 画面操作フロー詳細
6. **入出力仕様 / Input/Output Specifications** - フィールド定義・表示項目
7. **バリデーション仕様 / Validation Rules** - 入力検証ルール
8. **API連携仕様 / API Integration** - エンドポイント別連携仕様
9. **画面遷移 / Screen Navigation** - 操作・遷移フロー
10. **PoC制約事項 / Limitations for PoC Version** - 開発版制限事項
11. **フロントエンド開発者向け補足 / Notes for Frontend Developer** - 技術仕様・サンプルコード
12. **処理メッセージ仕様 / Operation Messages** - エラーメッセージ・通知仕様

#### 記述ガイドライン / Writing Guidelines

- **API連携仕様**: 必須`X-User-Id`ヘッダー、権限別アクセス制御を明記
- **権限管理**: システム管理者(user_id: 900001-999999)・医療機関ユーザー(entity_type=1)別制御
- **エラーハンドリング**: 403(権限なし)/404(不存在)/422(バリデーション)/500(サーバーエラー)対応
- **バリデーション**: Pydantic準拠の検証ルール・エラーメッセージ定義
- **ページング**: skip/limitパラメータ（通常100件、最大1000件制限）
- **差分管理**: デフォルト値との比較・上書き設定の概念を含む
- **複合主キー**: user_entity_link等の複合主キー管理画面での特殊対応
- **通知機能**: ファイル操作時の自動通知仕様を記載
- **技術仕様**: FastAPI + SQLAlchemy ORM連携、axios認証ヘッダー設定例を含む

#### 参照すべきAPI仕様書 / Reference API Specifications

- `design/backend/api/api_auth.md`: 認証API
- `design/backend/api/api_users.md`: ユーザー管理API
- `design/backend/api/api_facilities.md`: 医療機関API
- `design/backend/api/api_user_entity_links.md`: 組織連携API
- `design/backend/api/api_file_management.md`: ファイル管理API
- `design/backend/api/api_equipment_classifications.md`: 機器分類API
- `design/backend/api/api_medical_equipment_analysis.md`: 機器分析設定API

## mst_user.user_idをinteger から text に変更

- user_idはmst_userで宣言しているが、各テーブルの履歴情報等でも採用されているので全てに影響
- design/database/pg_optigate/mst_user.yamlを修正
- upgrade_tableinfo_poc.sh を実行しalembic並びにmodelsも修正済みを確認
- sqliteのテーブルも切り替わっていることを確認

---

## 🔄 Claude Code 環境移行時の引継ぎ情報 / Claude Code Environment Migration Notes

**作成日**: 2025-08-26
**前回Claude Code環境**: `/Users/smds/develop/smds_optiserve` → `/Users/smds/develop/optiserve-backend` (macOS)

### 📋 新しいClaude Codeセッションへの引継ぎ事項

#### 🎯 プロジェクト完了度サマリー

- **バックエンドAPI**: **100%完成** (全7つのAPIモジュール実装完了)
- **テストカバレッジ**: **40/40テスト通過** (100%パス率)
- **データベース設計**: **YAML自動生成システム完備**
- **権限管理システム**: **AuthManager統一認証実装済み**
- **ドキュメント**: **API仕様書7ファイル + プログラム仕様書7ファイル完成**
- **フロントエンド仕様書**: **2ファイル完成** (ログイン・ユーザー管理画面)

#### 🚨 重要な開発完了状況

1. **API実装**: 認証・ユーザー管理・医療機関マスタ・組織連携・ファイル管理・機器分類・機器分析設定 → **全て実装完了**
2. **テスト実装**: pytest統合テストスイート → **完全パス**
3. **権限システム**: システム管理者(900001-999999)・医療機関ユーザー(entity_type=1)別制御 → **実装完了**
4. **ファイル管理**: 月次アップロード・ダウンロード・通知システム → **実装完了**
5. **データ移行**: PostgreSQL→SQLite移行システム → **実装完了**

#### ⚠️ 新環境での最初に確認すべき事項

```bash
# 1. 環境パス設定確認 (最重要)
python -c "from src.utils.path_config import path_config; print(path_config.get_config_info())"

# 2. 必要ディレクトリ作成
python -c "from src.utils.path_config import path_config; path_config.ensure_directories()"

# 3. データベース初期化
./upgrade_tableinfo_poc.sh

# 4. API起動確認
./startup_optiserve.sh

# 5. テスト実行で完全性確認
pytest tests/ -v
```

#### 🎯 今後の開発優先度

1. **最優先**: フロントエンド画面仕様書の残り5画面分作成
   - ファイルアップロード・ダウンロード画面
   - 機器分析設定画面・機器分類管理画面・レポート分類選択設定画面
   - 医療機関マスタ管理画面・組織連携管理画面
2. **次優先**: Next.js/React実装開始
3. **その後**: Docker本番環境・AWS展開準備

#### 🔧 技術的な重要ポイント

- **path_config.py**: OS環境自動判定システムが実装済み（macOS・WSL・Docker対応）
- **AuthManager**: `src/utils/auth.py`で統一認証・認可システム実装済み
- **YAML自動生成**: `upgrade_tableinfo_poc.sh`でAlembic・SQLAlchemyモデル自動生成
- **複合主キー**: `user_entity_links`テーブルで(user_id + entity_type)の複合主キー対応済み
- **差分管理**: `medical_equipment_analysis`でデフォルト値との差分のみ保存システム実装済み

#### 💡 前回セッションでの主要な設計判断

1. **user_id型変更**: integer → text に変更済み (全テーブル影響あり、Alembic適用済み)
2. **権限設計**: システム管理者は9で始まるuser_id範囲、医療機関ユーザーはentity_type=1での制御
3. **ファイル管理**: 1世代保管(上書き)方式、3種類ファイル同時処理
4. **API設計**: X-User-Idヘッダー認証、HTTPException統一エラーハンドリング
5. **テスト設計**: ランダムデータ生成による干渉回避、E2Eテスト重視

#### 🗂️ 重要なファイル・ディレクトリ

- **API仕様書**: `design/backend/api/*.md` (7ファイル)
- **プログラム仕様書**: `design/backend/proc/*.md` (7ファイル)
- **フロントエンド仕様書**: `design/frontend/ui/*.md` (2ファイル)
- **データベース設計**: `design/database/pg_optigate/*.yaml`
- **テストスイート**: `tests/*.py` (5ファイル、40テスト)
- **認証管理**: `src/utils/auth.py` (AuthManagerクラス)
- **パス設定**: `src/utils/path_config.py` (環境自動判定)

#### 📝 新しいClaude Codeセッションで最初にやるべきこと

1. この引継ぎ情報を読んで、プロジェクトの完了度を把握
2. 上記の確認コマンドを実行して、新環境での動作確認
3. `pytest tests/ -v`でテスト全通過を確認
4. 既存の仕様書ファイルを確認して、設計思想を理解
5. フロントエンド仕様書の残り作成から開発を再開

**🎉 このプロジェクトは98%完成しています。残りはフロントエンド仕様書のみです！フロントエンドのNext.js開発は別スタッフが別のリポジトリで作成する前提です。**
