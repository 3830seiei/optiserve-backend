# 👥 ユーザー管理API仕様書 / User Management API Specification

**対象API**: `/api/v1/users`

---

## 1. 概要 / Overview

### 1.1 API説明 / API Description

ユーザー情報の管理機能を提供するAPIです。ユーザーの一覧取得、個別取得、新規登録、更新、無効化の機能を含みます。权限に基づくアクセス制御により、システム管理者と医療機関ユーザーそれぞれに適切な権限を提供します。

This API provides user information management functionality. It includes features for retrieving user lists, individual retrieval, new registration, updates, and inactivation. Role-based access control provides appropriate permissions for system administrators and medical facility users.

### 1.2 エンドポイント一覧 / Endpoint List

| エンドポイント / Endpoint | メソッド / Method | 説明 / Description |
| -------------------- | --------------- | ------------------- |
| `/api/v1/users` | GET | ユーザー一覧取得 / Get user list |
| `/api/v1/users/{user_id}` | GET | ユーザー個別取得 / Get individual user |
| `/api/v1/users` | POST | ユーザー新規登録 / Create new user |
| `/api/v1/users/{user_id}` | PUT | ユーザー情報更新 / Update user information |
| `/api/v1/users/{user_id}/inactive` | PUT | ユーザー無効化 / Inactivate user |

### 1.3 実装ファイル / Implementation Files

- **Router**: `src/routers/users.py`
- **Schema**: `src/schemas/mst_user.py`
- **Model**: `src/models/pg_optigate/mst_user.py`
- **Utils**: `src/utils/password.py`, `src/utils/auth.py`

---

## 2. 共通仕様 / Common Specifications

### 2.1 認証ヘッダー / Authentication Header

全エンドポイントで以下のヘッダーが必須です：
All endpoints require the following header:

```
X-User-Id: {user_id}
```

### 2.2 権限管理 / Permission Management

- **システム管理者** (user_id: 900001-999999): 全機能アクセス可能
- **医療機関ユーザー** (entity_type=1): 自医療機関のユーザーのみアクセス可能
- **System Administrator** (user_id: 900001-999999): Full access to all functions
- **Medical Facility User** (entity_type=1): Access only to users within their medical facility

### 2.3 ユーザーID採番ルール / User ID Assignment Rules

| 組織種別 / Entity Type | 範囲 / Range | 説明 / Description |
| -------------------- | ----------- | ------------------- |
| 医療機関 (1) | 100001-199999 | Medical facilities |
| ディーラー (2) | 200001-299999 | Dealers |
| メーカー (3) | 300001-399999 | Manufacturers |
| システム (9) | 900001-999999 | System |

---

## 3. GET /api/v1/users - ユーザー一覧取得 / Get User List

### 3.1 リクエスト仕様 / Request Specification

```
GET /api/v1/users?user_name={name}&entity_type={type}&skip={offset}&limit={count}
```

#### 3.1.1 クエリパラメータ / Query Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| user_name | string | ❌ | ユーザー名でフィルタリング / Filter by user name |
| entity_type | int | ❌ | 組織種別でフィルタリング / Filter by entity type |
| entity_relation_id | int | ❌ | 組織IDでフィルタリング / Filter by entity ID |
| e_mail | string | ❌ | メールアドレスでフィルタリング / Filter by email |
| phone_number | string | ❌ | 電話番号でフィルタリング / Filter by phone number |
| mobile_number | string | ❌ | 携帯番号でフィルタリング / Filter by mobile number |
| user_status | int | ❌ | ユーザーステータスでフィルタリング / Filter by user status |
| skip | int | ❌ | スキップ件数（デフォルト: 0）/ Skip count (default: 0) |
| limit | int | ❌ | 取得件数（デフォルト: 100、最大: 100）/ Limit count (default: 100, max: 100) |

#### 3.1.2 リクエスト例 / Request Examples

```
# 全件取得 / Get all users
GET /api/v1/users

# 名前でフィルタリング / Filter by name
GET /api/v1/users?user_name=セイエイ太郎

# 医療機関のユーザーをページング取得 / Get medical facility users with pagination
GET /api/v1/users?entity_type=1&skip=0&limit=50
```

### 3.2 レスポンス仕様 / Response Specification

#### 3.2.1 成功時レスポンス / Success Response

```json
[
  {
    "user_id": "100001",
    "user_name": "医療機関太郎",
    "entity_type": 1,
    "entity_relation_id": 22,
    "e_mail": "user@medical.example.com",
    "phone_number": "03-1234-5678",
    "mobile_number": "090-1234-5678",
    "user_status": 1,
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

## 4. GET /api/v1/users/{user_id} - ユーザー個別取得 / Get Individual User

### 4.1 リクエスト仕様 / Request Specification

```
GET /api/v1/users/{user_id}
```

#### 4.1.1 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| user_id | str | ✅ | ユーザーID / User ID |

### 4.2 レスポンス仕様 / Response Specification

#### 4.2.1 成功時レスポンス / Success Response

```json
{
  "user_id": "100001",
  "user_name": "医療機関太郎",
  "entity_type": 1,
  "entity_relation_id": 22,
  "e_mail": "user@medical.example.com",
  "phone_number": "03-1234-5678",
  "mobile_number": "090-1234-5678",
  "user_status": 1,
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
| 404 Not Found | ユーザーが見つからない / User not found |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 5. POST /api/v1/users - ユーザー新規登録 / Create New User

### 5.1 リクエスト仕様 / Request Specification

#### 5.1.1 権限要件 / Permission Requirements

システム管理者権限が必要です。
System administrator privileges required.

#### 5.1.2 リクエストボディ / Request Body

```json
{
  "user_name": "新規ユーザー",
  "entity_type": 1,
  "entity_relation_id": 22,
  "e_mail": "newuser@medical.example.com",
  "phone_number": "03-1234-5678",
  "mobile_number": "090-1234-5678"
}
```

#### 5.1.3 リクエストフィールド / Request Fields

| フィールド / Field | 型 / Type | 必須 / Required | 説明 / Description |
| ---------------- | -------- | ------------- | ------------------- |
| user_name | string | ✅ | ユーザー名 / User name |
| entity_type | int | ✅ | 組織種別 / Entity type |
| entity_relation_id | int | ✅ | 組織ID / Entity relation ID |
| e_mail | string | ✅ | メールアドレス / Email address |
| phone_number | string | ❌ | 電話番号 / Phone number |
| mobile_number | string | ❌ | 携帯番号 / Mobile number |

### 5.2 レスポンス仕様 / Response Specification

#### 5.2.1 成功時レスポンス / Success Response

```json
{
  "user_id": "100002",
  "user_name": "新規ユーザー",
  "entity_type": 1,
  "entity_relation_id": 22,
  "e_mail": "newuser@medical.example.com",
  "phone_number": "03-1234-5678",
  "mobile_number": "090-1234-5678",
  "user_status": 0,
  "reg_user_id": "900001",
  "regdate": "2025-08-19T10:30:00",
  "update_user_id": "900001",
  "lastupdate": "2025-08-19T10:30:00"
}
```

### 5.3 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常登録 / Successful registration |
| 400 Bad Request | 採番範囲上限到達 / User ID range limit reached |
| 403 Forbidden | 管理者権限なし / No administrator permission |
| 422 Unprocessable Entity | バリデーションエラー / Validation error |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 6. PUT /api/v1/users/{user_id} - ユーザー情報更新 / Update User Information

### 6.1 リクエスト仕様 / Request Specification

#### 6.1.1 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| user_id | str | ✅ | ユーザーID / User ID |

#### 6.1.2 リクエストボディ / Request Body

```json
{
  "user_name": "更新されたユーザー名",
  "phone_number": "03-9999-9999",
  "mobile_number": "090-9999-9999"
}
```

### 6.2 レスポンス仕様 / Response Specification

#### 6.2.1 成功時レスポンス / Success Response

```json
{
  "user_id": "100001",
  "user_name": "更新されたユーザー名",
  "entity_type": 1,
  "entity_relation_id": 22,
  "e_mail": "user@medical.example.com",
  "phone_number": "03-9999-9999",
  "mobile_number": "090-9999-9999",
  "user_status": 1,
  "reg_user_id": "900001",
  "regdate": "2025-08-19T10:00:00",
  "update_user_id": "100001",
  "lastupdate": "2025-08-19T11:00:00"
}
```

### 6.3 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常更新 / Successful update |
| 404 Not Found | ユーザーが見つからない / User not found |
| 422 Unprocessable Entity | バリデーションエラー / Validation error |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 7. PUT /api/v1/users/{user_id}/inactive - ユーザー無効化 / Inactivate User

### 7.1 リクエスト仕様 / Request Specification

#### 7.1.1 権限要件 / Permission Requirements

システム管理者権限が必要です。
System administrator privileges required.

#### 7.1.2 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| user_id | str | ✅ | ユーザーID / User ID |

#### 7.1.3 リクエストボディ / Request Body

```json
{
  "reason_code": 1,
  "note": "退職による無効化"
}
```

#### 7.1.4 リクエストフィールド / Request Fields

| フィールド / Field | 型 / Type | 必須 / Required | 説明 / Description |
| ---------------- | -------- | ------------- | ------------------- |
| reason_code | int | ✅ | 無効化理由コード / Inactivation reason code |
| note | string | ✅ | 無効化理由詳細 / Detailed inactivation reason |

### 7.2 レスポンス仕様 / Response Specification

#### 7.2.1 成功時レスポンス / Success Response

```json
{
  "user_id": "100001",
  "user_name": "無効化されたユーザー",
  "entity_type": 1,
  "entity_relation_id": 22,
  "e_mail": "user@medical.example.com",
  "user_status": 9,
  "inactive_reason_code": 1,
  "inactive_reason_note": "退職による無効化",
  "reg_user_id": "900001",
  "regdate": "2025-08-19T10:00:00",
  "update_user_id": "900001",
  "lastupdate": "2025-08-19T12:00:00"
}
```

### 7.3 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常無効化 / Successful inactivation |
| 403 Forbidden | 管理者権限なし / No administrator permission |
| 404 Not Found | ユーザーが見つからない / User not found |
| 422 Unprocessable Entity | バリデーションエラー / Validation error |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 8. データモデル / Data Model

### 8.1 ユーザーステータス / User Status

| 値 / Value | 説明 / Description |
| --------- | ------------------- |
| 0 | 仮登録 / Provisional registration |
| 1 | 稼働中 / Active |
| 9 | 利用停止 / Suspended |

### 8.2 組織種別 / Entity Type

| 値 / Value | 説明 / Description |
| --------- | ------------------- |
| 1 | 医療機関 / Medical facility |
| 2 | ディーラー / Dealer |
| 3 | メーカー / Manufacturer |
| 9 | システム / System |

---

## 9. 実装詳細 / Implementation Details

### 9.1 パスワード管理 / Password Management

- 新規登録時は`generate_temp_password()`で仮パスワードを生成
- ユーザーは初回ログイン後にパスワード変更が必要
- Temporary passwords are generated using `generate_temp_password()` during new registration
- Users must change their password after initial login

### 9.2 権限チェック / Permission Checking

- `AuthManager.require_admin_permission()`でシステム管理者権限チェック
- `AuthManager.get_user_info()`でユーザー情報とアクセス権限確認
- System administrator permission checked using `AuthManager.require_admin_permission()`
- User information and access permissions verified using `AuthManager.get_user_info()`

### 9.3 データベース操作 / Database Operations

- SQLAlchemy ORMを使用した型安全なデータベース操作
- トランザクション管理によるデータ整合性保証
- Type-safe database operations using SQLAlchemy ORM
- Data consistency guaranteed through transaction management

---

## 10. エラーハンドリング / Error Handling

### 10.1 バリデーションエラー / Validation Errors

Pydanticによる自動バリデーションで以下をチェック：
Automatic validation by Pydantic checks the following:

- メールアドレス形式 / Email format
- 必須フィールドの存在 / Presence of required fields
- データ型の整合性 / Data type consistency

### 10.2 権限エラー / Permission Errors

- 403 Forbidden: アクセス権限不足
- 403 Forbidden: Insufficient access permissions

### 10.3 データエラー / Data Errors

- 404 Not Found: 指定されたユーザーが存在しない
- 400 Bad Request: ユーザーID採番範囲の上限到達
- 404 Not Found: Specified user does not exist
- 400 Bad Request: User ID assignment range limit reached

---

## 11. テスト項目 / Test Cases

### 11.1 正常系テスト / Normal Test Cases

- [ ] ユーザー一覧取得（管理者）
- [ ] ユーザー一覧取得（医療機関ユーザー）
- [ ] ユーザー個別取得
- [ ] ユーザー新規登録
- [ ] ユーザー情報更新
- [ ] ユーザー無効化

### 11.2 異常系テスト / Error Test Cases

- [ ] 権限なしでの管理者機能アクセス
- [ ] 他医療機関のユーザー情報アクセス
- [ ] 存在しないユーザーID指定
- [ ] 無効なメールアドレス形式
- [ ] ユーザーID採番範囲上限到達

---

## 12. 今後の拡張予定 / Future Enhancements

### 12.1 機能拡張 / Feature Enhancement

- パスワードリセット機能 / Password reset functionality
- ユーザープロファイル画像対応 / User profile image support
- ログイン履歴管理 / Login history management
- 一括ユーザー登録機能 / Bulk user registration functionality

### 12.2 セキュリティ強化 / Security Enhancement

- 二要素認証対応 / Two-factor authentication support
- パスワード強度チェック / Password strength validation
- アカウントロック機能 / Account lock functionality

---

## 13. 関連資料 / Related Documents

- **プログラム仕様書**: `design/backend/proc/proc_users.md`
- **スキーマ定義**: `src/schemas/mst_user.py`
- **テストケース**: `tests/test_user_api.py`
- **データベース設計**: `design/database/pg_optigate/mst_user.yaml`
- **認証管理**: `src/utils/auth.py`
- **パスワード生成**: `src/utils/password.py`