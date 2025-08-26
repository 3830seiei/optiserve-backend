# 🏥 医療機関管理API仕様書 / Medical Facility Management API Specification

**対象API**: `/api/v1/facilities`

---

## 1. 概要 / Overview

### 1.1 API説明 / API Description

医療機関マスタ情報の管理機能を提供するAPIです。医療機関の一覧取得、個別取得、新規登録、更新の機能を含みます。権限に基づくアクセス制御により、システム管理者は全機能、医療機関ユーザーは自医療機関の情報のみアクセス可能です。

This API provides medical facility master information management functionality. It includes features for retrieving medical facility lists, individual retrieval, new registration, and updates. Role-based access control allows system administrators full access, while medical facility users can only access their own facility information.

### 1.2 エンドポイント一覧 / Endpoint List

| エンドポイント / Endpoint | メソッド / Method | 説明 / Description |
| -------------------- | --------------- | ------------------- |
| `/api/v1/facilities` | GET | 医療機関一覧取得 / Get medical facility list |
| `/api/v1/facilities/{facility_id}` | GET | 医療機関個別取得 / Get individual medical facility |
| `/api/v1/facilities` | POST | 医療機関新規登録 / Create new medical facility |
| `/api/v1/facilities/{facility_id}` | PUT | 医療機関情報更新 / Update medical facility information |

### 1.3 実装ファイル / Implementation Files

- **Router**: `src/routers/facilities.py`
- **Schema**: `src/schemas/mst_medical_facility.py`
- **Model**: `src/models/pg_optigate/mst_medical_facility.py`
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

- **システム管理者** (user_id: 900001-999999): 全医療機関情報へのアクセス可能
- **医療機関ユーザー** (entity_type=1): 自医療機関の情報のみアクセス可能
- **System Administrator** (user_id: 900001-999999): Access to all medical facility information
- **Medical Facility User** (entity_type=1): Access only to their own medical facility information

### 2.3 削除機能について / About Delete Functionality

医療機関の削除機能は意図的に提供されていません。データの整合性とトレーサビリティを保つため、論理削除や無効化も実装していません。

Delete functionality for medical facilities is intentionally not provided. To maintain data integrity and traceability, logical deletion or inactivation is also not implemented.

---

## 3. GET /api/v1/facilities - 医療機関一覧取得 / Get Medical Facility List

### 3.1 リクエスト仕様 / Request Specification

```
GET /api/v1/facilities?skip={offset}&limit={count}
```

#### 3.1.1 クエリパラメータ / Query Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| skip | int | ❌ | スキップ件数（デフォルト: 0）/ Skip count (default: 0) |
| limit | int | ❌ | 取得件数（デフォルト: 100、最大: 100）/ Limit count (default: 100, max: 100) |

#### 3.1.2 リクエスト例 / Request Examples

```
# 全件取得 / Get all facilities
GET /api/v1/facilities

# ページング取得 / Get with pagination
GET /api/v1/facilities?skip=0&limit=50
GET /api/v1/facilities?skip=50&limit=50
```

### 3.2 レスポンス仕様 / Response Specification

#### 3.2.1 成功時レスポンス / Success Response

```json
[
  {
    "medical_id": 22,
    "medical_name": "○○総合病院",
    "address_postal_code": "100-0001",
    "address_prefecture": "東京都",
    "address_city": "千代田区",
    "address_line1": "千代田1-1-1",
    "address_line2": "○○ビル3F",
    "phone_number": "03-1234-5678",
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

## 4. GET /api/v1/facilities/{facility_id} - 医療機関個別取得 / Get Individual Medical Facility

### 4.1 リクエスト仕様 / Request Specification

```
GET /api/v1/facilities/{facility_id}
```

#### 4.1.1 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| facility_id | int | ✅ | 医療機関ID / Medical facility ID |

### 4.2 レスポンス仕様 / Response Specification

#### 4.2.1 成功時レスポンス / Success Response

```json
{
  "medical_id": 22,
  "medical_name": "○○総合病院",
  "address_postal_code": "100-0001",
  "address_prefecture": "東京都",
  "address_city": "千代田区",
  "address_line1": "千代田1-1-1",
  "address_line2": "○○ビル3F",
  "phone_number": "03-1234-5678",
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
| 404 Not Found | 医療機関が見つからない / Medical facility not found |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 5. POST /api/v1/facilities - 医療機関新規登録 / Create New Medical Facility

### 5.1 リクエスト仕様 / Request Specification

#### 5.1.1 権限要件 / Permission Requirements

システム管理者権限が必要です。
System administrator privileges required.

#### 5.1.2 リクエストボディ / Request Body

```json
{
  "medical_name": "新規医療機関",
  "address_postal_code": "100-0002",
  "address_prefecture": "東京都",
  "address_city": "千代田区",
  "address_line1": "千代田2-2-2",
  "address_line2": "○○タワー10F",
  "phone_number": "03-9999-9999"
}
```

#### 5.1.3 リクエストフィールド / Request Fields

| フィールド / Field | 型 / Type | 必須 / Required | 説明 / Description |
| ---------------- | -------- | ------------- | ------------------- |
| medical_name | string | ✅ | 医療機関名 / Medical facility name |
| address_postal_code | string | ❌ | 郵便番号 / Postal code |
| address_prefecture | string | ❌ | 都道府県 / Prefecture |
| address_city | string | ❌ | 市区町村 / City |
| address_line1 | string | ❌ | 住所1（町名・番地等）/ Address line 1 |
| address_line2 | string | ❌ | 住所2（建物名等）/ Address line 2 |
| phone_number | string | ❌ | 電話番号 / Phone number |

### 5.2 レスポンス仕様 / Response Specification

#### 5.2.1 成功時レスポンス / Success Response

```json
{
  "medical_id": 23,
  "medical_name": "新規医療機関",
  "address_postal_code": "100-0002",
  "address_prefecture": "東京都",
  "address_city": "千代田区",
  "address_line1": "千代田2-2-2",
  "address_line2": "○○タワー10F",
  "phone_number": "03-9999-9999",
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
| 403 Forbidden | 管理者権限なし / No administrator permission |
| 422 Unprocessable Entity | バリデーションエラー / Validation error |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 6. PUT /api/v1/facilities/{facility_id} - 医療機関情報更新 / Update Medical Facility Information

### 6.1 リクエスト仕様 / Request Specification

#### 6.1.1 権限要件 / Permission Requirements

システム管理者権限が必要です。
System administrator privileges required.

#### 6.1.2 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| facility_id | int | ✅ | 医療機関ID / Medical facility ID |

#### 6.1.3 リクエストボディ / Request Body

```json
{
  "medical_name": "更新された医療機関名",
  "address_postal_code": "100-0003",
  "address_prefecture": "東京都",
  "address_city": "千代田区",
  "address_line1": "千代田3-3-3",
  "address_line2": "更新ビル5F",
  "phone_number": "03-8888-8888"
}
```

### 6.2 レスポンス仕様 / Response Specification

#### 6.2.1 成功時レスポンス / Success Response

```json
{
  "medical_id": 22,
  "medical_name": "更新された医療機関名",
  "address_postal_code": "100-0003",
  "address_prefecture": "東京都",
  "address_city": "千代田区",
  "address_line1": "千代田3-3-3",
  "address_line2": "更新ビル5F",
  "phone_number": "03-8888-8888",
  "reg_user_id": "900001",
  "regdate": "2025-08-19T10:00:00",
  "update_user_id": "900001",
  "lastupdate": "2025-08-19T12:00:00"
}
```

### 6.3 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常更新 / Successful update |
| 403 Forbidden | 管理者権限なし / No administrator permission |
| 404 Not Found | 医療機関が見つからない / Medical facility not found |
| 422 Unprocessable Entity | バリデーションエラー / Validation error |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 7. データモデル / Data Model

### 7.1 医療機関情報フィールド / Medical Facility Information Fields

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| medical_id | int | 医療機関ID（自動採番）/ Medical facility ID (auto-generated) |
| medical_name | string | 医療機関名 / Medical facility name |
| address_postal_code | string | 郵便番号 / Postal code |
| address_prefecture | string | 都道府県 / Prefecture |
| address_city | string | 市区町村 / City |
| address_line1 | string | 住所1（町名・番地等）/ Address line 1 |
| address_line2 | string | 住所2（建物名等）/ Address line 2 |
| phone_number | string | 電話番号 / Phone number |
| reg_user_id | str | 登録ユーザーID / Registration user ID |
| regdate | datetime | 登録日時 / Registration date |
| update_user_id | str | 更新ユーザーID / Update user ID |
| lastupdate | datetime | 最終更新日時 / Last update date |

---

## 8. 実装詳細 / Implementation Details

### 8.1 権限チェック / Permission Checking

#### 8.1.1 医療機関フィルタリング / Medical Facility Filtering

```python
# 権限に基づくデータフィルタリング
filtered_query = AuthManager.filter_by_medical_permission(
    query, current_user_id, db, MstMedicalFacility.medical_id
)
```

#### 8.1.2 管理者権限チェック / Administrator Permission Check

```python
# システム管理者権限チェック
AuthManager.require_admin_permission(current_user_id, db)
```

#### 8.1.3 医療機関アクセス権限チェック / Medical Facility Access Permission Check

```python
# 医療機関アクセス権限チェック
AuthManager.require_medical_permission(current_user_id, facility_id, db)
```

### 8.2 ログ出力 / Logging

新規登録および更新処理では詳細なログを出力：
Detailed logging for registration and update processes:

- 処理開始・完了ログ / Process start and completion logs
- リクエストデータログ / Request data logs  
- エラーログ / Error logs

### 8.3 トランザクション管理 / Transaction Management

- 自動コミット・ロールバック機能 / Automatic commit/rollback functionality
- エラー発生時の自動ロールバック / Automatic rollback on error occurrence

---

## 9. エラーハンドリング / Error Handling

### 9.1 バリデーションエラー / Validation Errors

Pydanticによる自動バリデーションで以下をチェック：
Automatic validation by Pydantic checks the following:

- 必須フィールドの存在 / Presence of required fields
- データ型の整合性 / Data type consistency
- 文字列長制限 / String length limitations

### 9.2 権限エラー / Permission Errors

- 403 Forbidden: アクセス権限不足 / Insufficient access permissions
- 管理者権限が必要な操作での権限チェック / Permission check for operations requiring administrator privileges

### 9.3 データエラー / Data Errors

- 404 Not Found: 指定された医療機関が存在しない / Specified medical facility does not exist
- 500 Internal Server Error: データベース操作エラー / Database operation error

### 9.4 エラーレスポンス例 / Error Response Examples

```json
# 権限エラー
{
  "detail": "管理者権限が必要です"
}

# 医療機関が見つからない
{
  "detail": "Medical facility not found"
}

# バリデーションエラー
{
  "detail": [
    {
      "loc": ["body", "medical_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 10. セキュリティ考慮事項 / Security Considerations

### 10.1 アクセス制御 / Access Control

- 医療機関ユーザーは自医療機関の情報のみアクセス可能
- システム管理者のみが新規登録・更新可能
- Medical facility users can only access their own facility information
- Only system administrators can perform registration and updates

### 10.2 データ保護 / Data Protection

- 医療機関情報は機密性が高いため、適切な権限管理が必要
- 削除機能は提供せず、データの永続性を保証
- Medical facility information is highly confidential and requires proper permission management
- No delete functionality provided to ensure data persistence

### 10.3 監査ログ / Audit Logs

- 全操作について登録・更新ユーザーIDと日時を記録
- セキュリティ監査用のアクセスログ出力
- Record registration/update user ID and timestamp for all operations
- Output access logs for security auditing

---

## 11. パフォーマンス考慮事項 / Performance Considerations

### 11.1 ページネーション / Pagination

- デフォルトページサイズ: 100件 / Default page size: 100 records
- 最大取得件数制限: 100件 / Maximum retrieval limit: 100 records
- skipとlimitパラメータによる効率的なページング / Efficient paging with skip and limit parameters

### 11.2 データベースアクセス最適化 / Database Access Optimization

- SQLAlchemy ORMによる効率的なクエリ生成 / Efficient query generation with SQLAlchemy ORM
- 必要最小限のデータフィールド取得 / Retrieve minimum necessary data fields

---

## 12. テスト項目 / Test Cases

### 12.1 正常系テスト / Normal Test Cases

- [ ] 医療機関一覧取得（管理者）
- [ ] 医療機関一覧取得（医療機関ユーザー）
- [ ] 医療機関個別取得
- [ ] 医療機関新規登録
- [ ] 医療機関情報更新
- [ ] ページネーション機能

### 12.2 異常系テスト / Error Test Cases

- [ ] 権限なしでの管理者機能アクセス
- [ ] 他医療機関の情報アクセス
- [ ] 存在しない医療機関ID指定
- [ ] 必須フィールド未入力
- [ ] 無効なデータ型指定

---

## 13. 今後の拡張予定 / Future Enhancements

### 13.1 機能拡張 / Feature Enhancement

- 医療機関検索機能（名前、住所での部分一致検索）/ Medical facility search functionality (partial match search by name, address)
- 医療機関カテゴリ分類機能 / Medical facility category classification functionality
- 医療機関連携情報管理 / Medical facility relationship information management
- 一括登録・更新機能 / Bulk registration and update functionality

### 13.2 データ拡張 / Data Enhancement

- 医療機関の特徴情報（診療科目、病床数等）/ Medical facility characteristics (medical departments, number of beds, etc.)
- 地理的情報（緯度経度）/ Geographic information (latitude/longitude)
- 営業時間情報 / Business hours information

### 13.3 セキュリティ強化 / Security Enhancement

- API レート制限 / API rate limiting
- 詳細な操作ログ記録 / Detailed operation log recording
- データ暗号化対応 / Data encryption support

---

## 14. 関連資料 / Related Documents

- **プログラム仕様書**: `design/backend/proc/proc_facilities.md`
- **スキーマ定義**: `src/schemas/mst_medical_facility.py`
- **テストケース**: `tests/test_user_api.py`
- **データベース設計**: `design/database/pg_optigate/mst_medical_facility.yaml`
- **認証管理**: `src/utils/auth.py`