# 画面仕様書 / Screen Specification

- Revision

    | Rev | Date       | Auth       | Note        |
    |----:|------------|------------|-------------|
    | 1.0 | 2025-08-19 | Claude     | 初版作成 / Initial version |

## 1. 画面名称 / Screen Title

- 日本語: [画面名称]
- English: [Screen Name]

### 1-1. 機能ID / Functional Identifier

- 機能ID（日本語）: [function-name]
- Functional Name (English): [function-name]
- 使用例（SPAルーティング）: `/[route-path]`

## 2. 機能概要 / Function Overview

[Japanese]

- [機能の概要説明]
- [主要な機能・特徴]

[English]

- [Function overview description]
- [Main features and characteristics]

---

## 3. 画面利用対象ユーザー / Target Users

- [対象ユーザーの権限・役割]
- システム管理者 (user_id: 900001-999999): [アクセス範囲]
- 医療機関ユーザー (entity_type=1): [アクセス範囲]

<div style="page-break-before: always;"></div>

## 4. 運用概要 / Operational Usage

[Japanese]

- [業務的な背景・利用目的]
- [運用上の考慮事項]

[English]

- [Business background and purpose]
- [Operational considerations]

<div style="page-break-before: always;"></div>

## 5. 処理の流れ / Processing Flow

[Japanese]

1. [処理ステップ1の説明]
2. [処理ステップ2の説明]
3. [API連携の詳細]
4. [結果表示・後続処理]

[English]

1. [Processing step 1 description]
2. [Processing step 2 description]
3. [API integration details]
4. [Result display and subsequent processing]

<div style="page-break-before: always;"></div>

## 6. 入出力仕様 / Input / Output Specifications

### 6.1 入力フォーム項目 / Input Form Fields

| 項目 / Item | フィールド / Field | 要件 / Requirements |
|-------------|-------------------|---------------------|
| [項目名] | [field_name] | [必須/任意、制約条件] |

### 6.2 一覧表示項目 / List Display Fields

| 項目 / Item | 表示対象 / Display | フィールド / Field | ソート順 / Sort |
|-------------|-------------------|-------------------|-----------------|
| [項目名] | [○/×] | [field_name] | [順序] |

---

## 7. バリデーション仕様 / Validation Rules

[Japanese]

- [フィールド名]: [バリデーション条件・制約]
- [エラーメッセージ例]

[English]

- [Field name]: [Validation conditions and constraints]
- [Error message examples]

<div style="page-break-before: always;"></div>

## 8. API連携仕様 / API Integration

### 8.1 `GET /api/v1/[endpoint]`

- **必須ヘッダー**: `X-User-Id: {user_id}`
- **クエリパラメータ**: [パラメータ説明]
- **レスポンス**: [レスポンス構造説明]
- **権限**: [必要な権限]

### 8.2 `POST /api/v1/[endpoint]`

- **必須ヘッダー**: `X-User-Id: {user_id}`
- **リクエストボディ**: [リクエスト構造説明]
- **レスポンス**: [レスポンス構造説明]
- **権限**: [必要な権限]

### 8.3 `PUT /api/v1/[endpoint]/{id}`

- **必須ヘッダー**: `X-User-Id: {user_id}`
- **パスパラメータ**: [パラメータ説明]
- **リクエストボディ**: [リクエスト構造説明]
- **権限**: [必要な権限]

### 8.4 `DELETE /api/v1/[endpoint]/{id}`

- **必須ヘッダー**: `X-User-Id: {user_id}`
- **パスパラメータ**: [パラメータ説明]
- **権限**: [必要な権限]

<div style="page-break-before: always;"></div>

## 9. 画面遷移 / Screen Navigation

| 操作 / Operation | 説明 / Description |
|------------------|-------------------|
| [操作名] | [遷移先・処理内容] |

### 9.1 画面イメージ

<p style="border: 1px solid #ccc; display: inline-block;">
  <img src="./assets/[image-file].png" alt="[画面名]" width="600" />
</p>

<div style="page-break-before: always;"></div>

## 10. PoC制約事項 / Limitations for PoC Version

[Japanese]

- [PoC版での制限事項]
- [将来的な改善予定]

[English]

- [Limitations in PoC version]
- [Future improvement plans]

## 11. フロントエンド開発者向け補足 / Notes for Frontend Developer

この画面は、Next.js等のフロントエンドSPAがFastAPIバックエンドとREST APIで接続する構成を想定しています。

### 🔌 接続情報 / Connection Details

| 項目 / Item | 内容 / Content |
|-------------|---------------|
| 接続先API / API Endpoint | `http://192.168.99.118:8000`（PoC用） |
| 通信方式 / Communication | REST（`fetch` や `axios` など） |
| データ形式 / Data Format | JSON（リクエスト／レスポンス共通） |
| 認証 / Authentication | `X-User-Id` ヘッダーによる認証が必要 |
| CORS | `Access-Control-Allow-Origin: *` を許可済（開発用途） |
| ステータスコード / Status Codes | `200 OK`, `403 Forbidden`, `404 Not Found`, `422 Validation Error`, `500 Internal Server Error` |

### 📦 APIレスポンス構造（例）

```json
{
  "field1": "value1",
  "field2": "value2",
  "field3": 123,
  "created_at": "2025-08-19T10:00:00",
  "updated_at": "2025-08-19T10:05:00"
}
```

### 🛠 axios使用例

```ts
import axios from 'axios';

const apiBase = 'http://192.168.99.118:8000/api/v1/[endpoint]';

export const fetchData = async (currentUserId: number) => {
  const res = await axios.get(apiBase, {
    headers: {
      'X-User-Id': currentUserId.toString()
    }
  });
  return res.data;
};
```

<div style="page-break-before: always;"></div>

## 12. 処理メッセージ仕様 / Operation Messages

この画面では、ユーザーに対して各操作の結果を明示的に伝えるために、以下のようなメッセージを表示します。

### 12.1 共通メッセージ / Common Messages

| タイミング / Timing | ステータス / Status | 表示メッセージ / Message | 備考 / Notes |
|--------------------|--------------------|-----------------------|-------------|
| 処理成功 / Success | 200 OK | [操作]が完了しました。 | 正常処理時 |
| 権限エラー / Permission Error | 403 Forbidden | アクセス権限がありません。管理者にお問い合わせください。 | 権限不足時 |
| データ不存在 / Not Found | 404 Not Found | 指定された[対象]が見つかりません。 | データ不存在時 |
| バリデーションエラー / Validation Error | 422 Unprocessable Entity | 入力内容に不備があります。再確認してください。 | 入力検証エラー |
| サーバーエラー / Server Error | 500 Internal Server Error | サーバーでエラーが発生しました。後で再度お試しください。 | システムエラー |

### 12.2 フィールド別バリデーションエラーメッセージ例

| フィールド / Field | エラーメッセージ / Error Message |
|-------------------|--------------------------------|
| [field_name] | [具体的なエラーメッセージ] |

### 12.3 API別メッセージまとめ

| APIエンドポイント / API Endpoint | 成功時メッセージ / Success Message | 失敗時メッセージ / Error Message |
|----------------------------------|-----------------------------------|--------------------------------|
| `POST /[endpoint]` | [操作対象]を登録しました。 | 入力に不備があります。 |
| `PUT /[endpoint]/{id}` | [操作対象]を更新しました。 | 対象データが見つかりません。 |
| `DELETE /[endpoint]/{id}` | [操作対象]を削除しました。 | 対象データが存在しません。 |

### 12.4 表示方法の推奨 / Display Recommendations

[Japanese]

- メッセージは画面右下の**トースト通知**または上部への**アラート表示**が望ましい
- 重大エラー（500番台など）はモーダルでブロッキング表示してもよい
- バリデーションエラーは該当項目の**下部 or 横に赤字表示**（フィールド単位）

[English]

- Toast notifications at the bottom right of the screen or alert messages at the top are preferred
- For critical errors (e.g., 500 series), a blocking modal dialog may be used
- Validation errors should be displayed in red text below or beside the corresponding field

---

以上