# 🔗 ユーザー組織連携API仕様書 / User Entity Links API Specification

**対象API**: `/api/v1/user-entity-links`

---

## 1. 概要 / Overview

### 1.1 API説明 / API Description

ユーザーと組織（医療機関・ディーラー・メーカー）の連携情報を管理するAPIです。現在は医療機関（entity_type=1）のみをサポートしており、連携情報の取得、新規登録、更新の機能を提供します。複合主キー（entity_type + entity_relation_id）による一意性管理を行います。

This API manages the linkage information between users and organizations (medical facilities, dealers, manufacturers). Currently, it only supports medical facilities (entity_type=1) and provides functionality for retrieving, registering, and updating linkage information. Uniqueness is managed through composite primary keys (entity_type + entity_relation_id).

### 1.2 エンドポイント一覧 / Endpoint List

| エンドポイント / Endpoint | メソッド / Method | 説明 / Description |
| -------------------- | --------------- | ------------------- |
| `/api/v1/user-entity-links` | GET | 連携情報一覧取得 / Get link list |
| `/api/v1/user-entity-links/{entity_type}/{entity_relation_id}` | GET | 連携情報個別取得 / Get individual link |
| `/api/v1/user-entity-links` | POST | 連携情報新規登録 / Create new link |
| `/api/v1/user-entity-links/{entity_type}/{entity_relation_id}` | PUT | 連携情報更新 / Update link information |

### 1.3 実装ファイル / Implementation Files

- **Router**: `src/routers/user_entity_links.py`
- **Schema**: `src/schemas/user_entity_link.py`
- **Model**: `src/models/pg_optigate/user_entity_link.py`
- **Utils**: `src/utils/auth.py`

---

## 2. 共通仕様 / Common Specifications

### 2.1 認証ヘッダー / Authentication Header

全エンドポイントで以下のヘッダーが必須です：
All endpoints require the following header:

```
X-User-Id: {user_id}
```

### 2.2 権限管理 / Permission Management

- **システム管理者** (user_id: 900001-999999): 全連携情報へのアクセス可能
- **医療機関ユーザー** (entity_type=1): 自医療機関の連携情報のみアクセス可能
- **System Administrator** (user_id: 900001-999999): Access to all linkage information
- **Medical Facility User** (entity_type=1): Access only to their own medical facility linkage information

### 2.3 複合主キー / Composite Primary Key

連携情報は以下の複合主キーで一意性を管理します：
Linkage information uniqueness is managed by the following composite primary key:

- `entity_type`: 組織種別 / Organization type
- `entity_relation_id`: 組織ID / Organization ID

### 2.4 サポート対象組織 / Supported Organizations

現在は医療機関（entity_type=1）のみサポートしています。
Currently supports only medical facilities (entity_type=1).

---

## 3. GET /api/v1/user-entity-links - 連携情報一覧取得 / Get Link List

### 3.1 リクエスト仕様 / Request Specification

```
GET /api/v1/user-entity-links?skip={offset}&limit={count}
```

#### 3.1.1 クエリパラメータ / Query Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| skip | int | ❌ | スキップ件数（デフォルト: 0）/ Skip count (default: 0) |
| limit | int | ❌ | 取得件数（デフォルト: 100、最大: 100）/ Limit count (default: 100, max: 100) |

#### 3.1.2 リクエスト例 / Request Examples

```
# 全件取得 / Get all links
GET /api/v1/user-entity-links

# ページング取得 / Get with pagination
GET /api/v1/user-entity-links?skip=0&limit=50
GET /api/v1/user-entity-links?skip=50&limit=50
```

### 3.2 レスポンス仕様 / Response Specification

#### 3.2.1 成功時レスポンス / Success Response

```json
[
  {
    "entity_type": 1,
    "entity_relation_id": 22,
    "entity_name": "○○総合病院",
    "notification_email_list": ["admin@hospital.example.com", "manager@hospital.example.com"],
    "count_reportout_classification": 10,
    "analiris_classification_level": 2,
    "reg_user_id": "900001",
    "regdate": "2025-08-19T10:00:00",
    "update_user_id": "900001",
    "lastupdate": "2025-08-19T10:00:00"
  }
]
```

### 3.3 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常取得 / Successful retrieval |
| 403 Forbidden | アクセス権限なし / No access permission |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 4. GET /api/v1/user-entity-links/{entity_type}/{entity_relation_id} - 連携情報個別取得 / Get Individual Link

### 4.1 リクエスト仕様 / Request Specification

```
GET /api/v1/user-entity-links/{entity_type}/{entity_relation_id}
```

#### 4.1.1 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| entity_type | int | ✅ | 組織種別（1: 医療機関）/ Entity type (1: Medical facility) |
| entity_relation_id | int | ✅ | 組織ID / Entity relation ID |

#### 4.1.2 リクエスト例 / Request Examples

```
# 医療機関ID=22の連携情報取得
GET /api/v1/user-entity-links/1/22
```

### 4.2 レスポンス仕様 / Response Specification

#### 4.2.1 成功時レスポンス / Success Response

```json
{
  "entity_type": 1,
  "entity_relation_id": 22,
  "entity_name": "○○総合病院",
  "notification_email_list": ["admin@hospital.example.com", "manager@hospital.example.com"],
  "count_reportout_classification": 10,
  "analiris_classification_level": 2,
  "reg_user_id": "900001",
  "regdate": "2025-08-19T10:00:00",
  "update_user_id": "900001",
  "lastupdate": "2025-08-19T10:00:00"
}
```

### 4.3 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常取得 / Successful retrieval |
| 403 Forbidden | アクセス権限なし / No access permission |
| 404 Not Found | 連携情報が見つからない / Link information not found |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 5. POST /api/v1/user-entity-links - 連携情報新規登録 / Create New Link

### 5.1 リクエスト仕様 / Request Specification

#### 5.1.1 権限要件 / Permission Requirements

システム管理者権限が必要です。
System administrator privileges required.

#### 5.1.2 リクエストボディ / Request Body

```json
{
  "entity_type": 1,
  "entity_relation_id": 23,
  "entity_name": "新規医療機関",
  "notification_email_list": "admin@newhosp.example.com,manager@newhosp.example.com",
  "count_reportout_classification": 15,
  "analiris_classification_level": 3
}
```

#### 5.1.3 リクエストフィールド / Request Fields

| フィールド / Field | 型 / Type | 必須 / Required | 説明 / Description |
| ---------------- | -------- | ------------- | ------------------- |
| entity_type | int | ✅ | 組織種別（1のみサポート）/ Entity type (only 1 supported) |
| entity_relation_id | int | ✅ | 組織ID（医療機関マスタに存在必須）/ Entity relation ID (must exist in medical facility master) |
| entity_name | string | ✅ | 組織名 / Entity name |
| notification_email_list | string/array | ✅ | 通知メールリスト / Notification email list |
| count_reportout_classification | int | ✅ | レポート公開分類数 / Report output classification count |
| analiris_classification_level | int | ✅ | 分析レポート分類レベル（1-3）/ Analysis classification level (1-3) |

#### 5.1.4 バリデーション / Validation

- **entity_type**: 1のみ有効 / Only 1 is valid
- **entity_relation_id**: 医療機関マスタに存在する必要あり / Must exist in medical facility master
- **entity_name**: 空文字列不可 / Cannot be empty string
- **notification_email_list**: 空文字列不可 / Cannot be empty string
- **analiris_classification_level**: 1-3の値のみ有効 / Only values 1-3 are valid

### 5.2 レスポンス仕様 / Response Specification

#### 5.2.1 成功時レスポンス / Success Response

```json
{
  "entity_type": 1,
  "entity_relation_id": 23,
  "entity_name": "新規医療機関",
  "notification_email_list": ["admin@newhosp.example.com", "manager@newhosp.example.com"],
  "count_reportout_classification": 15,
  "analiris_classification_level": 3,
  "reg_user_id": "900001",
  "regdate": "2025-08-19T11:00:00",
  "update_user_id": "900001",
  "lastupdate": "2025-08-19T11:00:00"
}
```

### 5.3 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常登録 / Successful registration |
| 400 Bad Request | バリデーションエラー / Validation error |
| 403 Forbidden | 管理者権限なし / No administrator permission |
| 422 Unprocessable Entity | データ形式エラー / Data format error |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 6. PUT /api/v1/user-entity-links/{entity_type}/{entity_relation_id} - 連携情報更新 / Update Link Information

### 6.1 リクエスト仕様 / Request Specification

#### 6.1.1 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| entity_type | int | ✅ | 組織種別（1: 医療機関）/ Entity type (1: Medical facility) |
| entity_relation_id | int | ✅ | 組織ID / Entity relation ID |

#### 6.1.2 リクエストボディ / Request Body

```json
{
  "entity_type": 1,
  "entity_relation_id": 22,
  "entity_name": "更新された医療機関名",
  "notification_email_list": "updated@hospital.example.com,new-manager@hospital.example.com",
  "count_reportout_classification": 20,
  "analiris_classification_level": 1
}
```

### 6.2 レスポンス仕様 / Response Specification

#### 6.2.1 成功時レスポンス / Success Response

```json
{
  "entity_type": 1,
  "entity_relation_id": 22,
  "entity_name": "更新された医療機関名",
  "notification_email_list": ["updated@hospital.example.com", "new-manager@hospital.example.com"],
  "count_reportout_classification": 20,
  "analiris_classification_level": 1,
  "reg_user_id": "900001",
  "regdate": "2025-08-19T10:00:00",
  "update_user_id": "100001",
  "lastupdate": "2025-08-19T12:00:00"
}
```

### 6.3 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常更新 / Successful update |
| 400 Bad Request | バリデーションエラー / Validation error |
| 403 Forbidden | アクセス権限なし / No access permission |
| 404 Not Found | 連携情報が見つからない / Link information not found |
| 422 Unprocessable Entity | データ形式エラー / Data format error |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 7. データモデル / Data Model

### 7.1 連携情報フィールド / Link Information Fields

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| entity_type | int | 組織種別（1: 医療機関）/ Entity type (1: Medical facility) |
| entity_relation_id | int | 組織ID / Entity relation ID |
| entity_name | string | 組織名 / Entity name |
| notification_email_list | array | 通知メールリスト / Notification email list |
| count_reportout_classification | int | レポート公開分類数 / Report output classification count |
| analiris_classification_level | int | 分析レポート分類レベル / Analysis classification level |
| reg_user_id | str | 登録ユーザーID / Registration user ID |
| regdate | datetime | 登録日時 / Registration date |
| update_user_id | str | 更新ユーザーID / Update user ID |
| lastupdate | datetime | 最終更新日時 / Last update date |

### 7.2 組織種別 / Entity Type

| 値 / Value | 説明 / Description | サポート状況 / Support Status |
| --------- | ------------------- | ---------------------------- |
| 1 | 医療機関 / Medical facility | ✅ サポート済み / Supported |
| 2 | ディーラー / Dealer | ❌ 未サポート / Not supported |
| 3 | メーカー / Manufacturer | ❌ 未サポート / Not supported |

### 7.3 分析レポート分類レベル / Analysis Classification Level

| 値 / Value | 説明 / Description |
| --------- | ------------------- |
| 1 | 大分類のみ / Major classification only |
| 2 | 中分類まで / Up to medium classification |
| 3 | 小分類まで / Up to minor classification |

---

## 8. 実装詳細 / Implementation Details

### 8.1 データ変換機能 / Data Conversion Functions

#### 8.1.1 メールリスト変換 / Email List Conversion

```python
def convert_email_list_for_db(email_list_str: str) -> list:
    """notification_email_listを文字列からDB用リスト形式に変換"""
```

- 文字列形式とJSON形式の両方をサポート / Supports both string and JSON formats
- カンマ区切り文字列を配列に変換 / Converts comma-separated strings to arrays
- JSON文字列のバリデーション / JSON string validation

### 8.2 権限チェック / Permission Checking

#### 8.2.1 管理者権限チェック / Administrator Permission Check

```python
# 新規登録時のシステム管理者権限チェック
AuthManager.require_admin_permission(current_user_id, db)
```

#### 8.2.2 医療機関アクセス権限チェック / Medical Facility Access Permission Check

```python
# 個別取得・更新時の医療機関アクセス権限チェック
AuthManager.require_medical_permission(current_user_id, entity_relation_id, db)
```

#### 8.2.3 医療機関フィルタリング / Medical Facility Filtering

```python
# 一覧取得時の権限に基づくフィルタリング
filtered_query = AuthManager.filter_by_medical_permission(
    query, current_user_id, db, UserEntityLink.entity_relation_id
)
```

### 8.3 バリデーション / Validation

#### 8.3.1 必須フィールドチェック / Required Field Check

- entity_name の空文字列チェック / Empty string check for entity_name
- notification_email_list の空文字列チェック / Empty string check for notification_email_list
- 数値フィールドのNullチェック / Null check for numeric fields

#### 8.3.2 関連データ存在チェック / Related Data Existence Check

```python
# 医療機関マスタ存在チェック
medical_facility = db.query(MstMedicalFacility).filter(
    MstMedicalFacility.medical_id == link.entity_relation_id
).first()
```

---

## 9. エラーハンドリング / Error Handling

### 9.1 バリデーションエラー / Validation Errors

#### 9.1.1 組織種別エラー / Entity Type Error

```json
{
  "detail": "組織種別（entity_type）は1のみサポートしています（医療機関タイプ）"
}
```

#### 9.1.2 必須フィールドエラー / Required Field Error

```json
{
  "detail": "組織名（entity_name）は必須です"
}
```

#### 9.1.3 分析レベルエラー / Analysis Level Error

```json
{
  "detail": "分析レポート分類レベル（analiris_classification_level）は1-3の値のみ有効です"
}
```

### 9.2 関連データエラー / Related Data Error

```json
{
  "detail": "医療機関ID（entity_relation_id） 999 は存在しません"
}
```

### 9.3 権限エラー / Permission Error

```json
{
  "detail": "管理者権限が必要です"
}
```

### 9.4 データ不存在エラー / Data Not Found Error

```json
{
  "detail": "User entity link not found: entity_type=1, entity_relation_id=999"
}
```

---

## 10. セキュリティ考慮事項 / Security Considerations

### 10.1 アクセス制御 / Access Control

- 医療機関ユーザーは自医療機関の連携情報のみアクセス可能
- システム管理者のみが新規登録可能
- Medical facility users can only access their own facility linkage information
- Only system administrators can perform new registrations

### 10.2 データ整合性 / Data Integrity

- 複合主キーによる一意性保証 / Uniqueness guaranteed by composite primary key
- 関連する医療機関マスタの存在チェック / Existence check for related medical facility master
- 必須フィールドの厳密なバリデーション / Strict validation for required fields

### 10.3 監査ログ / Audit Logs

- 全操作について登録・更新ユーザーIDと日時を記録
- 詳細なログ出力によるトレーサビリティ確保
- Record registration/update user ID and timestamp for all operations
- Ensure traceability through detailed log output

---

## 11. パフォーマンス考慮事項 / Performance Considerations

### 11.1 ページネーション / Pagination

- デフォルトページサイズ: 100件 / Default page size: 100 records
- 最大取得件数制限: 100件 / Maximum retrieval limit: 100 records

### 11.2 データベースアクセス最適化 / Database Access Optimization

- 複合主キーによる効率的な検索 / Efficient search using composite primary key
- 必要に応じた関連データの結合 / Join related data as needed

---

## 12. テスト項目 / Test Cases

### 12.1 正常系テスト / Normal Test Cases

- [ ] 連携情報一覧取得（管理者）
- [ ] 連携情報一覧取得（医療機関ユーザー）
- [ ] 連携情報個別取得
- [ ] 連携情報新規登録
- [ ] 連携情報更新
- [ ] ページネーション機能
- [ ] メールリスト変換機能

### 12.2 異常系テスト / Error Test Cases

- [ ] 権限なしでの管理者機能アクセス
- [ ] 他医療機関の連携情報アクセス
- [ ] 存在しない組織IDでの操作
- [ ] 無効な組織種別指定
- [ ] 必須フィールド未入力
- [ ] 無効な分析レベル指定
- [ ] 存在しない医療機関IDでの登録

---

## 13. 今後の拡張予定 / Future Enhancements

### 13.1 組織種別拡張 / Entity Type Expansion

- ディーラー（entity_type=2）対応 / Support for dealers (entity_type=2)
- メーカー（entity_type=3）対応 / Support for manufacturers (entity_type=3)

### 13.2 機能拡張 / Feature Enhancement

- 連携情報の一括更新機能 / Bulk update functionality for linkage information
- 通知設定の詳細制御 / Detailed control of notification settings
- 履歴管理機能 / History management functionality

### 13.3 セキュリティ強化 / Security Enhancement

- メールアドレスの形式チェック強化 / Enhanced email format validation
- API レート制限 / API rate limiting
- 詳細な操作ログ記録 / Detailed operation log recording

---

## 14. 関連資料 / Related Documents

- **プログラム仕様書**: `design/backend/proc/proc_user_entity_links.md`
- **スキーマ定義**: `src/schemas/user_entity_link.py`
- **テストケース**: `tests/test_user_entity_links_api.py`
- **データベース設計**: `design/database/pg_optigate/user_entity_link.yaml`
- **認証管理**: `src/utils/auth.py`
- **医療機関マスタ**: `src/models/pg_optigate/mst_medical_facility.py`