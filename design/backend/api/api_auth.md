# 🔐 認証API仕様書 / Authentication API Specification

**対象API**: `/api/v1/auth/login`

---

## 1. 概要 / Overview

### 1.1 API説明 / API Description

メールアドレスとパスワードを用いてログイン認証を行い、ユーザーの状態に応じた `next_action` を返します。この `next_action` によりフロントエンド側で次画面への遷移先を判断します。

This API performs login authentication using email address and password, returning a `next_action` based on the user's status. The frontend determines the destination screen based on this `next_action`.

### 1.2 エンドポイント / Endpoint

`POST /api/v1/auth/login`

### 1.3 実装ファイル / Implementation Files

- **Router**: `src/routers/auth.py`
- **Schema**: `src/schemas/auth.py`
- **Model**: `src/models/pg_optigate/mst_user.py`

---

## 2. リクエスト仕様 / Request Specification

### 2.1 リクエスト形式 / Request Format

```json
{
  "e_mail": "user@example.com",
  "password": "password123!"
}
```

### 2.2 リクエストパラメータ / Request Parameters

| フィールド名 / Field | 型 / Type | 必須 / Required | 説明 / Description |
| -------------- | -------- | ------------- | ---------------- |
| e\_mail        | string   | ✅             | メールアドレス形式であること / Must be valid email format   |
| password       | string   | ✅             | 平文（PoCではハッシュなし）/ Plain text (no hash in PoC)  |

### 2.3 バリデーション / Validation

- **e_mail**: メールアドレス形式（RFC 5322準拠）/ Email format (RFC 5322 compliant)
- **password**: 1文字以上 / At least 1 character

---

## 3. レスポンス仕様 / Response Specification

### 3.1 成功時レスポンス / Success Response

```json
{
  "success": true,
  "user_id": "101",
  "user_status": 0,
  "next_action": "show_user_registration",
  "message": "仮登録状態です"
}
```

### 3.2 失敗時レスポンス / Error Response

```json
{
  "detail": "メールアドレスまたはパスワードが正しくありません"
}
```

### 3.3 レスポンスフィールド / Response Fields

| フィールド名 / Field | 型 / Type | 説明 / Description     |
| -------------- | -------- | -------------------- |
| success        | bool     | ログイン成功なら true / true if login successful        |
| user\_id       | str      | ユーザーID（DBのPK）/ User ID (DB Primary Key)        |
| user\_status   | int      | 0:仮登録, 1:稼働中, 9:利用停止 / 0:Provisional, 1:Active, 9:Suspended |
| next\_action   | string   | 次に取るべきアクション（下記参照）/ Next action to take (see below)    |
| message        | string   | 状態に応じた説明メッセージ（表示用）/ Status message for display   |

---

## 4. next_action定義 / next_action Definition

### 4.1 next_actionマッピング / next_action Mapping

| user\_status | next\_action             | 意味 / Meaning       |
| ------------ | ------------------------ | ------------------ |
| 0            | show\_user\_registration | 仮登録 → 本登録画面へ / Provisional → Registration screen       |
| 1            | show\_main\_menu         | 稼働中ユーザー → メニュー画面へ / Active user → Main menu  |
| 9            | inactive                 | 利用停止中 → 通知してログイン不可 / Suspended → Show notice, prevent login |
| その他 / Others | error                    | 不正な状態 → ログ調査対象 / Invalid status → Requires investigation     |

### 4.2 補足 / Notes

- `inactive` や `error` の場合は `success: false` として返すことを想定
- Cases for `inactive` or `error` are expected to return `success: false`

---

## 5. HTTPステータスコード / HTTP Status Codes

| ステータス / Status    | 内容 / Meaning                 |
| ----------------- | ---------------------------- |
| 200 OK            | 認証成功、`next_action` を含んだレスポンス / Authentication success with `next_action` |
| 401 Unauthorized  | 認証失敗（パスワード不一致など）/ Authentication failure (password mismatch, etc.) |
| 404 Not Found     | メールアドレスが登録されていない / Email address not registered |
| 422 Unprocessable | バリデーションエラー / Validation error |
| 500 Server Error  | サーバー内部エラー / Internal server error |

---

## 6. 実装詳細 / Implementation Details

### 6.1 認証フロー / Authentication Flow

1. リクエストデータのバリデーション / Request data validation
2. データベースからユーザー情報取得 / Retrieve user information from database
3. パスワード照合（現在は平文比較）/ Password verification (currently plain text)
4. `user_status`に基づく`next_action`決定 / Determine `next_action` based on `user_status`
5. レスポンス返却 / Return response

### 6.2 セキュリティ考慮事項 / Security Considerations

- **現在の制限**: パスワードハッシュ化未実装（PoC仕様）/ Current limitation: Password hashing not implemented (PoC specification)
- **今後の予定**: JWT認証、セッション管理導入予定 / Future plans: JWT authentication, session management

### 6.3 データベース連携 / Database Integration

- **テーブル**: `mst_user`
- **検索条件**: `e_mail` フィールドでのマッチング / Search condition: Matching by `e_mail` field
- **参照項目**: `user_id`, `password`, `user_status` / Referenced fields: `user_id`, `password`, `user_status`

---

## 7. エラーハンドリング / Error Handling

### 7.1 エラーケース / Error Cases

| エラーケース / Error Case | HTTPステータス / HTTP Status | レスポンス / Response |
| -------------------- | ------------------------- | ------------------- |
| メールアドレス未登録 / Email not registered | 404 | `{"detail": "メールアドレスが登録されていません"}` |
| パスワード不一致 / Password mismatch | 401 | `{"detail": "メールアドレス、またはパスワードが間違っています"}` |
| バリデーションエラー / Validation error | 422 | Pydanticのエラー詳細 / Pydantic error details |

### 7.2 ログ出力 / Logging

- 認証失敗時のIPアドレスとメールアドレス記録 / Record IP address and email on authentication failure
- セキュリティ監査用のアクセスログ / Access logs for security auditing

---

## 8. テスト項目 / Test Cases

### 8.1 正常系テスト / Normal Test Cases

- [ ] 仮登録ユーザーのログイン → `next_action: "show_user_registration"`
- [ ] 稼働中ユーザーのログイン → `next_action: "show_main_menu"`

### 8.2 異常系テスト / Error Test Cases

- [ ] 未登録メールアドレスでのログイン試行
- [ ] 正しいメールアドレス、間違ったパスワード
- [ ] 利用停止ユーザーのログイン試行
- [ ] 不正な形式のメールアドレス

---

## 9. 今後の拡張予定 / Future Enhancements

### 9.1 セキュリティ強化 / Security Enhancement

- パスワードハッシュ化（bcrypt等）/ Password hashing (bcrypt, etc.)
- JWT認証トークン導入 / JWT authentication token implementation
- ログイン試行回数制限 / Login attempt rate limiting
- 二要素認証対応 / Two-factor authentication support

### 9.2 機能拡張 / Feature Enhancement

- セッション管理 / Session management
- ログイン履歴管理 / Login history management
- パスワードリセット機能 / Password reset functionality

---

## 10. 関連資料 / Related Documents

- **プログラム仕様書**: `design/backend/proc/proc_auth.md`
- **スキーマ定義**: `src/schemas/auth.py`
- **テストケース**: `tests/test_user_api.py`
- **データベース設計**: `design/database/pg_optigate/mst_user.yaml`
