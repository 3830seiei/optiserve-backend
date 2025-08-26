
# OptiServe 認証モジュール 設計仕様書 / Auth Module Design Specification

## 概要 / Overview

このモジュールは、ユーザーのログイン機能を提供します。
ログイン時には、認証情報の検証、ユーザーの状態確認、ログイン後の画面遷移指示（`next_action`）を含んだレスポンスを返します。

## 1. システム構成 / System Architecture

| 項目 | 内容 |
|------|------|
| 使用フレームワーク | FastAPI |
| 認証方式 | パスワード認証（bcryptによるハッシュ） |
| トークン | JWTトークン未使用（PoC段階ではトークンレス） |
| DB接続 | SQLite（開発用） / PostgreSQL（本番想定） |
| APIパス | `/api/v1/auth/login` |

## 2. 関連ファイル / File Responsibilities

| ファイル名 | 役割 |
|------------|------|
| `routers/auth.py` | APIエンドポイントの定義 |
| `schemas/auth.py` | リクエスト・レスポンスのPydanticモデル定義 |
| `models/mst_user.py` | `mst_user` テーブルのORMモデル |
| `core/password.py` | パスワードのハッシュ／照合関数群 |

## 3. API仕様 / API Specification

### エンドポイント

```plaintext

POST /api/v1/auth/login

```

### リクエスト（`schemas.auth.LoginRequest`）

| フィールド名 | 型 | 必須 | 補足 |
|--------------|----|------|------|
| `e_mail` | str | ✅ | ログインIDとして使用 |
| `password` | str | ✅ | 平文で送信し、サーバー側で照合 |

### レスポンス（`schemas.auth.LoginResponse`）

| フィールド名 | 型 | 説明 |
|--------------|----|------|
| `user_id` | int | 一意なユーザーID |
| `user_name` | str | 表示名 |
| `entity_type` | int | 組織種別（1=医療機関など） |
| `entity_relation_id` | int | 組織ID |
| `user_status` | int | 0=仮登録, 1=稼働中, 9=利用停止 |
| `next_action` | str | 次に遷移すべき画面の指示 |
| `message` | str | 結果メッセージ（成功・エラー内容など） |

## 4. next_action の定義 / Next Action Mapping

| user_status | next_action | 意味 |
|-------------|-------------|------|
| 0 | `need_profile` | 初回ログインとして、ユーザーマスタの更新画面へ遷移 |
| 1 | `dashboard` | ダッシュボード画面へ遷移（通常運用） |
| 9 | `inactive` | 利用停止のためログイン不可（エラー表示） |

## 5. 認証処理の流れ / Authentication Flow

1. メールアドレスで該当ユーザーを `mst_user` テーブルから検索
2. ユーザーが存在しない場合：
   - HTTP 404 エラーを返す
   - message: 「ユーザーが存在しません。」
3. パスワードが一致しない場合：
   - HTTP 401 エラーを返す
   - message: 「パスワードが正しくありません。」
4. `user_status == 9`（利用停止） の場合：
   - HTTP 403 エラーを返す
   - message: 「このアカウントは利用停止中です。」
5. 正常ログインの場合：
   - `next_action` を付けて HTTP 200 で返却
      - 0: 仮登録 → next_action: `need_profile`
      - 1: 稼働中 → next_action: `dashboard`

## 6. バリデーション / Validation Rules

- `e_mail`：
  - メール形式であること（PydanticのEmailStr使用）
- `password`：
  - 最低8文字以上（現時点では形式チェックは行わず照合のみ）

## 7. エラーとステータスコード / Error Handling

| ステータス | 内容 | 条件 |
|------------|------|------|
| 200 OK | ログイン成功 | ユーザー認証が成功した場合 |
| 401 Unauthorized | パスワード不一致 | パスワードが正しくない |
| 403 Forbidden | 利用停止中 | `user_status = 9` |
| 404 Not Found | ユーザー未登録 | 該当メールアドレスなし |
| 500 Internal Server Error | 予期しないエラー | DBエラー等 |

## 8. 備考 / Notes

- 現時点ではセッション管理やJWTの発行は行わず、**PoC向けの単純な認証処理**に留めています。
- 将来的には `user_status = 1` 以外はログイン不可にする予定。
- 本番環境ではHTTPS通信・トークン発行などのセキュリティ強化が必要です。


## 9. 参考

- routers/auth.py
- schemas/auth.py
- models/mst_user.py
- core/password.py
