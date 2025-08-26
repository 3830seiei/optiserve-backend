# 画面仕様書 / Screen Specification

- Revision

    | Rev | Date       | Auth       | Note        |
    |----:|------------|------------|-------------|
    | 1.0 | 2025-08-19 | Claude     | 初版作成 / Initial version |
    | 2.0 | 2025-08-25 | Claude     | user_id型変更・モック操作仕様統合・12章構成統一 |

## 1. 画面名称 / Screen Title

- 日本語: 組織連携管理画面
- English: User Entity Links Management Screen

### 1-1. 機能ID / Functional Identifier

- 機能ID（日本語）: user-entity-links-management
- Functional Name (English): user-entity-links-management
- 使用例（SPAルーティング）: `/admin/user-entity-links`

## 2. 機能概要 / Function Overview

[Japanese]

- ユーザーと組織（医療機関等）の連携情報を管理する画面
- 複合主キー（user_id + entity_type）による連携データの管理
- 通知設定・分析分類レベル・レポート出力設定等の詳細管理
- システム管理者専用機能として、ユーザー登録時の自動連携作成に対応

[English]

- Management screen for user and organization (medical facilities, etc.) linkage information
- Management of linked data using composite primary key (user_id + entity_type)
- Detailed management of notification settings, analysis classification levels, report output settings, etc.
- System administrator-only functionality supporting automatic link creation during user registration

---

## 3. 画面利用対象ユーザー / Target Users

- システム管理者 (user_id: "900001"-"999999"): 全ユーザーの組織連携情報を管理可能
- ※医療機関ユーザーは本画面にアクセス不可（権限制限）

<div style="page-break-before: always;"></div>

## 4. 運用概要 / Operational Usage

[Japanese]

- ユーザーマスタメンテナンス画面でのユーザー追加時に自動的に組織連携レコードを作成
- 既存の連携レコードがある場合は、既存レコードを活用（重複作成回避）
- 各医療機関の通知先メールアドレス設定・レポート出力設定の管理
- 分析対象機器分類レベルの設定による、機器分析機能の制御
- 組織連携情報の参照・更新による運用管理業務の支援

[English]

- Automatically creates organization link records when adding users in the User Master Maintenance screen
- Uses existing records when available (avoids duplicate creation)
- Management of notification email address settings and report output settings for each medical facility
- Control of equipment analysis functions through setting analysis target equipment classification levels
- Support for operational management tasks through viewing and updating organization link information

<div style="page-break-before: always;"></div>

## 5. 処理の流れ / Processing Flow

[Japanese]

1. **画面初期表示**: `GET /api/v1/user-entity-links` で組織連携一覧を取得（管理者権限チェック）
2. **検索・フィルタ**: ユーザーID、entity_type、医療機関ID等での絞り込み実行
3. **詳細表示**: 一覧から連携情報を選択し、詳細情報をフォームに表示
4. **新規作成**: 「新規作成」ボタンでフォーム初期化、必要情報入力後 `POST /api/v1/user-entity-links` で登録
5. **情報更新**: 既存情報を編集後 `PUT /api/v1/user-entity-links` で更新実行（複合主キー使用）
6. **連携削除**: 確認ダイアログ後 `DELETE /api/v1/user-entity-links` で削除実行
7. **結果表示**: 各操作の成功・失敗結果をユーザーに通知

[English]

1. **Initial screen display**: Retrieve organization link list via `GET /api/v1/user-entity-links` (administrator permission check)
2. **Search and filter**: Execute filtering by user ID, entity_type, medical facility ID, etc.
3. **Detail display**: Select link information from list and display detailed information in form
4. **New creation**: Initialize form with "New Creation" button, register via `POST /api/v1/user-entity-links` after inputting required information
5. **Information update**: Update via `PUT /api/v1/user-entity-links` after editing existing information (using composite primary key)
6. **Link deletion**: Execute deletion via `DELETE /api/v1/user-entity-links` after confirmation dialog
7. **Result display**: Notify users of success/failure results for each operation

<div style="page-break-before: always;"></div>

## 6. 入出力仕様 / Input / Output Specifications

### 6.1 入力フォーム項目 / Input Form Fields

| 項目 / Item | フィールド / Field | 要件 / Requirements |
|-------------|-------------------|---------------------|
| ユーザーID / User ID | user_id | 必須、文字列型（"100001"-"999999"）|
| 組織種別 / Entity Type | entity_type | 必須、選択肢（1:医療機関、2:ディーラー、3:メーカー、9:管理者権限） |
| 組織関連ID / Entity Relation ID | entity_relation_id | 必須、整数 |
| 通知メールリスト / Notification Email List | notification_email_list | 任意、カンマ区切りメールアドレス |
| レポート出力分類数 / Report Classification Count | count_reportout_classification | 任意、整数（1-20、デフォルト:5） |
| 分析分類レベル / Analysis Classification Level | analiris_classification_level | 任意、選択肢（1:大分類、2:中分類、3:小分類） |
| 備考 / Notes | notes | 任意、最大500文字 |

### 6.2 一覧表示項目 / List Display Fields

| 項目 / Item | 表示対象 / Display | フィールド / Field | ソート順 / Sort |
|-------------|-------------------|-------------------|-----------------|
| ユーザーID / User ID | ○ | user_id | 1 |
| ユーザー名 / User Name | ○ | user_name | - |
| 組織種別 / Entity Type | ○ | entity_type | 2 |
| 組織関連ID / Entity Relation ID | ○ | entity_relation_id | 3 |
| 組織名 / Entity Name | ○ | entity_name | - |
| 通知メール数 / Email Count | ○ | email_count | - |
| レポート出力数 / Report Count | ○ | count_reportout_classification | - |
| 更新日時 / Last Update | ○ | lastupdate | 4 |

---

## 7. バリデーション仕様 / Validation Rules

[Japanese]

- **ユーザーID**: 文字列型、"100001"-"999999"の範囲内
- **組織種別**: 必須、1(医療機関)・2(ディーラー)・3(メーカー)・9(管理者権限)から選択
- **組織関連ID**: 必須、正の整数、指定した組織種別に対応する組織の存在チェック
- **通知メールリスト**: カンマ区切り形式、各メールアドレスの形式チェック、最大10件
- **レポート出力分類数**: 1-20の範囲内、整数のみ
- **分析分類レベル**: 1(大分類)・2(中分類)・3(小分類)から選択
- **備考**: 最大500文字以内

[English]

- **User ID**: String type, within range "100001"-"999999"
- **Entity Type**: Required, select from 1(Medical Facility), 2(Dealer), 3(Manufacturer), 9(Administrator)
- **Entity Relation ID**: Required, positive integer, existence check for organization corresponding to specified entity type
- **Notification Email List**: Comma-separated format, format check for each email address, maximum 10 entries
- **Report Classification Count**: Within range 1-20, integers only
- **Analysis Classification Level**: Select from 1(Major), 2(Sub), 3(Detailed)
- **Notes**: Maximum 500 characters

<div style="page-break-before: always;"></div>

## 8. API連携仕様 / API Integration

### 8.1 `GET /api/v1/user-entity-links`

- **必須ヘッダー**: `X-User-Id: {user_id}`（システム管理者のみ）
- **クエリパラメータ**: 
  - skip: スキップ件数（デフォルト: 0）
  - limit: 取得件数（デフォルト: 100、最大: 1000）
  - user_id: ユーザーIDでフィルタ
  - entity_type: 組織種別でフィルタ
  - entity_relation_id: 組織関連IDでフィルタ
- **レスポンス**: 組織連携一覧、ユーザー名・組織名を含む結合データ
- **権限**: システム管理者のみアクセス可能

### 8.2 `POST /api/v1/user-entity-links`

- **必須ヘッダー**: `X-User-Id: {user_id}`（システム管理者のみ）
- **リクエストボディ**: 組織連携情報（user_id, entity_type, entity_relation_idは必須）
- **レスポンス**: 作成された組織連携情報
- **権限**: システム管理者のみ
- **注意**: 既存の複合主キー（user_id + entity_type）と重複する場合はエラー

### 8.3 `PUT /api/v1/user-entity-links`

- **必須ヘッダー**: `X-User-Id: {user_id}`（システム管理者のみ）
- **リクエストボディ**: 更新する組織連携情報（複合主キー含む）
- **レスポンス**: 更新された組織連携情報
- **権限**: システム管理者のみ

### 8.4 `DELETE /api/v1/user-entity-links`

- **必須ヘッダー**: `X-User-Id: {user_id}`（システム管理者のみ）
- **リクエストボディ**: 削除対象の複合主キー（user_id + entity_type）
- **レスポンス**: 削除結果メッセージ
- **権限**: システム管理者のみ

<div style="page-break-before: always;"></div>

## 9. 画面遷移 / Screen Navigation

| 操作 / Operation | 説明 / Description |
|------------------|-------------------|
| 検索実行 / Search | 条件入力後、一覧表示を更新 |
| 新規作成 / New Creation | フォーム初期化、入力後登録実行 |
| 詳細表示 / View Details | 一覧から選択、詳細情報をフォーム表示 |
| 情報更新 / Update Information | 詳細表示状態で編集、更新実行 |
| 連携削除 / Delete Link | 確認ダイアログ後、削除実行 |
| ページ移動 / Pagination | 前へ・次へボタンでページ遷移 |

### 9.1 画面レイアウト / Screen Layout

![組織設定管理画面](assets/mock_user_entity_links_01.png)

**画面構成:**
- **組織検索・フィルタ部** (上部)
  - 組織名検索フィールド：部分一致検索
  - 組織種別フィルタ：「すべて」ドロップダウン
  - 分析レベルフィルタ：「すべて」ドロップダウン
  - 検索ボタン：絞り込み実行
- **組織設定一覧部** (左下)
  - 統計情報表示：「組織統計: 全5組織(医療機関:10, ディーラー:3, メーカー:2)」
  - ページング対応テーブル：15件単位で組織種別・組織ID・組織名・分析レベル・レポート出力数を表示
- **組織設定詳細部** (右下)
  - 操作ガイド表示：組織設定管理についての説明
  - 組織選択時の詳細情報フォーム表示エリア
- **組織設定統計部** (下部)
  - 種別別統計：医療機関 10組織・ディーラー 3組織・メーカー 2組織・平均レポート出力数 8分類

<div style="page-break-before: always;"></div>

## 10. PoC制約事項 / Limitations for PoC Version

[Japanese]

- 通知機能は現状未対応（notification_email_listの設定のみ）
- 一括インポート・エクスポート機能は未実装
- 組織連携の履歴管理機能は未実装
- entity_typeの動的追加（ディーラー・メーカー等の詳細管理）は未対応

[English]

- Notification functionality is currently not supported (only notification_email_list settings)
- Bulk import/export functionality is not implemented
- Organization link history management functionality is not implemented
- Dynamic addition of entity_type (detailed management of dealers, manufacturers, etc.) is not supported

## 11. フロントエンド開発者向け補足 / Notes for Frontend Developer

この画面は、Next.js等のフロントエンドSPAがFastAPIバックエンドとREST APIで接続する構成を想定しています。

### 🔌 接続情報 / Connection Details

| 項目 / Item | 内容 / Content |
|-------------|---------------|
| 接続先API / API Endpoint | `http://192.168.99.118:8000/api/v1/user-entity-links`（PoC用） |
| 通信方式 / Communication | REST（`fetch` や `axios` など） |
| データ形式 / Data Format | JSON（リクエスト／レスポンス共通） |
| 認証 / Authentication | `X-User-Id` ヘッダーによる認証が必要（システム管理者のみ） |
| CORS | `Access-Control-Allow-Origin: *` を許可済（開発用途） |
| ステータスコード / Status Codes | `200 OK`, `403 Forbidden`, `404 Not Found`, `422 Validation Error`, `500 Internal Server Error` |

### 📦 APIレスポンス構造（例）

```json
{
  "user_id": "100001",
  "user_name": "田中太郎",
  "entity_type": 1,
  "entity_relation_id": 22,
  "entity_name": "○○総合病院",
  "notification_email_list": "admin@hospital.jp,manager@hospital.jp",
  "count_reportout_classification": 5,
  "analiris_classification_level": 2,
  "notes": "レポート担当者: 田中",
  "regdate": "2025-07-22T10:00:00",
  "lastupdate": "2025-08-19T15:30:00"
}
```

### 🛠 axios使用例

```ts
import axios from 'axios';

const apiBase = 'http://192.168.99.118:8000/api/v1/user-entity-links';

export const fetchUserEntityLinks = async (currentUserId: string, skip = 0, limit = 100) => {
  const res = await axios.get(`${apiBase}?skip=${skip}&limit=${limit}`, {
    headers: {
      'X-User-Id': currentUserId  // user_idは文字列型
    }
  });
  return res.data;
};

export const createUserEntityLink = async (currentUserId: string, linkData: any) => {
  const res = await axios.post(apiBase, linkData, {
    headers: {
      'X-User-Id': currentUserId,  // user_idは文字列型
      'Content-Type': 'application/json'
    }
  });
  return res.data;
};
```

### 🔗 複合主キー管理のポイント

```ts
// 複合主キーでの更新・削除処理例
const updateUserEntityLink = async (currentUserId: string, linkData: any) => {
  // 複合主キー（user_id + entity_type）を含む更新データ
  const updateData = {
    user_id: linkData.user_id,  // 文字列型
    entity_type: linkData.entity_type,
    entity_relation_id: linkData.entity_relation_id,
    notification_email_list: linkData.notification_email_list,
    // ... その他のフィールド
  };
  
  const res = await axios.put(apiBase, updateData, {
    headers: {
      'X-User-Id': currentUserId,  // user_idは文字列型
      'Content-Type': 'application/json'
    }
  });
  return res.data;
};
```

### 💡 UI操作詳細（モック画面との統合仕様）

#### 検索・フィルタ機能（画面上部）：
- **組織名検索**: 「部分一致検索」フィールドで組織名による絞り込み
- **組織種別フィルタ**: 「すべて」ドロップダウンで医療機関・ディーラー・メーカー・管理者権限で絞り込み
- **分析レベルフィルタ**: 「すべて」ドロップダウンで大分類・中分類・小分類で絞り込み
- **検索ボタン**: 絞り込み条件で一覧更新実行

#### 組織設定一覧テーブル（左下部）：
- **統計情報**: 「組織統計: 全5組織(医療機関:10, ディーラー:3, メーカー:2)」表示
- **ページネーション**: 「ページ(全1ページ、15件)」でページ選択
- **テーブル列**: 組織種別・組織ID・組織名・分析レベル・レポート出力数を表示
- **行選択**: テーブルから組織を1行選択で詳細情報を右側に表示

#### 組織設定詳細管理（右下部）：
- **選択時表示**: 組織選択時に右側エリアに詳細フォームを表示
- **操作ガイド**: 未選択時は組織設定管理についての説明を表示
- **重要事項表示**:
  - 複合主キー: (entity_type + entity_relation_id)
  - 管理対象: 医療機関・ディーラー・メーカーの設定
  - 通知機能: ファイル処理完了時の自動通知
  - 分析設定: レポート生成の分類レベル設定
- **操作手順**: 左の一覧から組織を選択 → 組織情報・分析設定を確認・編集 → 連絡先情報を更新 → 「設定更新」で保存

#### 組織設定統計（下部）：
- **種別別統計**: 医療機関 10組織・ディーラー 3組織・メーカー 2組織・平均レポート出力数 8分類のメトリクス表示
- **利用状況**: 各組織種別の登録数とアクティブ率を視覚的に表示

<div style="page-break-before: always;"></div>

## 12. 処理メッセージ仕様 / Operation Messages

この画面では、ユーザーに対して各操作の結果を明示的に伝えるために、以下のようなメッセージを表示します。

### 12.1 共通メッセージ / Common Messages

| タイミング / Timing | ステータス / Status | 表示メッセージ / Message | 備考 / Notes |
|--------------------|--------------------|-----------------------|-------------|
| 作成成功 / Creation Success | 200 OK | 組織連携情報を作成しました。 | 新規作成時 |
| 更新成功 / Update Success | 200 OK | 組織連携情報を更新しました。 | 情報更新時 |
| 削除成功 / Deletion Success | 200 OK | 組織連携情報を削除しました。 | 削除処理時 |
| 権限エラー / Permission Error | 403 Forbidden | アクセス権限がありません。システム管理者のみ利用可能です。 | 権限不足時 |
| データ不存在 / Data Not Found | 404 Not Found | 指定された組織連携情報が見つかりません。 | データ不存在時 |
| 重複エラー / Duplicate Error | 400 Bad Request | 同じユーザーと組織種別の組織連携情報が既に存在します。 | 複合主キー重複時 |
| バリデーションエラー / Validation Error | 422 Unprocessable Entity | 入力内容に不備があります。再確認してください。 | 入力検証エラー |
| サーバーエラー / Server Error | 500 Internal Server Error | サーバーでエラーが発生しました。後で再度お試しください。 | システムエラー |

### 12.2 フィールド別バリデーションエラーメッセージ例

| フィールド / Field | エラーメッセージ / Error Message |
|-------------------|--------------------------------|
| user_id | ユーザーIDは"100001"-"999999"の範囲で入力してください。 |
| entity_type | 組織種別を選択してください。 |
| entity_relation_id | 組織関連IDは正の整数で入力してください。指定した組織が存在することを確認してください。 |
| notification_email_list | 通知メールアドレスの形式が正しくありません。カンマ区切りで最大10件まで入力できます。 |
| count_reportout_classification | レポート出力分類数は1-20の範囲で入力してください。 |
| notes | 備考は500文字以内で入力してください。 |

### 12.3 API別メッセージまとめ

| APIエンドポイント / API Endpoint | 成功時メッセージ / Success Message | 失敗時メッセージ / Error Message |
|----------------------------------|-----------------------------------|--------------------------------|
| `POST /api/v1/user-entity-links` | 組織連携情報を作成しました。 | 入力に不備があります。または既に同じ連携情報が存在します。 |
| `PUT /api/v1/user-entity-links` | 組織連携情報を更新しました。 | 対象の組織連携情報が見つかりません。 |
| `DELETE /api/v1/user-entity-links` | 組織連携情報を削除しました。 | 対象の組織連携情報が存在しません。 |

### 12.4 表示方法の推奨 / Display Recommendations

[Japanese]

- メッセージは画面右下の**トースト通知**または上部への**アラート表示**が望ましい
- 重大エラー（500番台など）はモーダルでブロッキング表示してもよい
- バリデーションエラーは該当項目の**下部 or 横に赤字表示**（フィールド単位）
- 削除処理時は**確認ダイアログ**で誤操作を防止

[English]

- Toast notifications at the bottom right of the screen or alert messages at the top are preferred
- For critical errors (e.g., 500 series), a blocking modal dialog may be used
- Validation errors should be displayed in red text below or beside the corresponding field
- Use confirmation dialog for deletion operations to prevent accidental operations

---

以上