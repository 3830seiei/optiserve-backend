# 🏷️ 機器分類・レポート出力選択API仕様書 / Equipment Classifications & Report Selection API Specification

**対象API**: `/api/v1/equipment-classifications`

---

## 1. 概要 / Overview

### 1.1 API説明 / API Description

機器分類マスタの照会とレポート出力用機器分類選択機能を提供するAPIです。医療機関向けのレポート作成時に、どの機器分類をレポートに含めるかを管理し、user_entity_link.count_reportout_classificationに基づく選択数制限を適用します。

This API provides equipment classification master lookup and equipment classification selection functionality for report output. It manages which equipment classifications to include in reports for medical facilities, applying selection count limits based on user_entity_link.count_reportout_classification.

### 1.2 エンドポイント一覧 / Endpoint List

| エンドポイント / Endpoint | メソッド / Method | 説明 / Description |
| -------------------- | --------------- | ------------------- |
| `/api/v1/equipment-classifications/{medical_id}` | GET | 機器分類一覧取得 / Get equipment classification list |
| `/api/v1/equipment-classifications/report-selection/{medical_id}` | GET | レポート選択情報取得 / Get report selection configuration |
| `/api/v1/equipment-classifications/report-selection/{medical_id}` | POST | レポート選択情報登録 / Create report selection configuration |
| `/api/v1/equipment-classifications/report-selection/{medical_id}` | DELETE | レポート選択情報削除 / Delete report selection configuration |

### 1.3 実装ファイル / Implementation Files

- **Router**: `src/routers/equipment_classifications.py`
- **Schema**: `src/schemas/equipment_classification.py`
- **Model**: `src/models/pg_optigate/mst_equipment_classification.py`, `src/models/pg_optigate/equipment_classification_report_selection.py`
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

- **システム管理者** (user_id: 900001-999999): 全医療機関の機器分類情報へのアクセス可能
- **医療機関ユーザー** (entity_type=1): 自医療機関の機器分類情報のみアクセス可能
- **System Administrator** (user_id: 900001-999999): Access to all medical facility equipment classification information
- **Medical Facility User** (entity_type=1): Access only to their own medical facility equipment classification information

### 2.3 機器分類階層構造 / Equipment Classification Hierarchy

機器分類は3階層構造を持ちます：
Equipment classifications have a 3-level hierarchy:

- **大分類** (classification_level: 1): 主要カテゴリ / Major categories
- **中分類** (classification_level: 2): サブカテゴリ / Sub categories  
- **小分類** (classification_level: 3): 詳細カテゴリ / Detailed categories

---

## 3. GET /api/v1/equipment-classifications/{medical_id} - 機器分類一覧取得 / Get Equipment Classification List

### 3.1 リクエスト仕様 / Request Specification

```
GET /api/v1/equipment-classifications/{medical_id}?skip={offset}&limit={count}
```

#### 3.1.1 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| medical_id | int | ✅ | 医療機関ID / Medical facility ID |

#### 3.1.2 クエリパラメータ / Query Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| skip | int | ❌ | スキップ件数（デフォルト: 0）/ Skip count (default: 0) |
| limit | int | ❌ | 取得件数（デフォルト: 100、最大: 1000）/ Limit count (default: 100, max: 1000) |

#### 3.1.3 リクエスト例 / Request Examples

```
# 全件取得 / Get all classifications
GET /api/v1/equipment-classifications/22

# ページング取得 / Get with pagination
GET /api/v1/equipment-classifications/22?skip=0&limit=50
GET /api/v1/equipment-classifications/22?skip=50&limit=50
```

### 3.2 レスポンス仕様 / Response Specification

#### 3.2.1 成功時レスポンス / Success Response

```json
{
  "total": 150,
  "skip": 0,
  "limit": 100,
  "items": [
    {
      "classification_id": 1001,
      "medical_id": 22,
      "classification_level": 1,
      "parent_classification_id": null,
      "classification_name": "手術器械",
      "classification_code": "SURGERY",
      "sort_order": 1
    },
    {
      "classification_id": 1002,
      "medical_id": 22,
      "classification_level": 2,
      "parent_classification_id": 1001,
      "classification_name": "切開器械",
      "classification_code": "SURGERY_CUT",
      "sort_order": 1
    },
    {
      "classification_id": 1003,
      "medical_id": 22,
      "classification_level": 3,
      "parent_classification_id": 1002,
      "classification_name": "メス",
      "classification_code": "SCALPEL",
      "sort_order": 1
    }
  ]
}
```

#### 3.2.2 レスポンスフィールド / Response Fields

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| total | int | 総件数 / Total count |
| skip | int | スキップ件数 / Skip count |
| limit | int | 制限件数 / Limit count |
| items | array | 機器分類一覧 / Equipment classification list |

#### 3.2.3 機器分類項目 / Classification Item Fields

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| classification_id | int | 分類ID / Classification ID |
| medical_id | int | 医療機関ID / Medical facility ID |
| classification_level | int | 階層レベル（1-3）/ Hierarchy level (1-3) |
| parent_classification_id | int | 親分類ID / Parent classification ID |
| classification_name | string | 分類名 / Classification name |
| classification_code | string | 分類コード / Classification code |
| sort_order | int | ソート順 / Sort order |

### 3.3 ソート順序 / Sort Order

機器分類は以下の順序でソートされます：
Equipment classifications are sorted in the following order:

1. `classification_level` (階層レベル昇順 / Hierarchy level ascending)
2. `parent_classification_id` (親分類ID昇順 / Parent classification ID ascending)
3. `classification_name` (分類名昇順 / Classification name ascending)

### 3.4 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常取得 / Successful retrieval |
| 403 Forbidden | アクセス権限なし / No access permission |
| 404 Not Found | 医療機関が見つからない / Medical facility not found |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 4. GET /api/v1/equipment-classifications/report-selection/{medical_id} - レポート選択情報取得 / Get Report Selection Configuration

### 4.1 リクエスト仕様 / Request Specification

```
GET /api/v1/equipment-classifications/report-selection/{medical_id}
```

#### 4.1.1 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| medical_id | int | ✅ | 医療機関ID / Medical facility ID |

### 4.2 レスポンス仕様 / Response Specification

#### 4.2.1 成功時レスポンス / Success Response

```json
{
  "medical_id": 22,
  "max_count": 10,
  "selections": [
    {
      "rank": 1,
      "classification_id": 1003,
      "classification_name": "メス"
    },
    {
      "rank": 2,
      "classification_id": 1015,
      "classification_name": "内視鏡"
    },
    {
      "rank": 3,
      "classification_id": 1027,
      "classification_name": "人工呼吸器"
    }
  ]
}
```

#### 4.2.2 レスポンスフィールド / Response Fields

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| medical_id | int | 医療機関ID / Medical facility ID |
| max_count | int | 最大選択可能数 / Maximum selectable count |
| selections | array | 選択された分類一覧 / Selected classification list |

#### 4.2.3 選択項目 / Selection Item Fields

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| rank | int | 優先順位 / Priority rank |
| classification_id | int | 分類ID / Classification ID |
| classification_name | string | 分類名 / Classification name |

### 4.3 最大選択数の決定 / Maximum Count Determination

最大選択数は以下の順序で決定されます：
Maximum count is determined in the following order:

1. `user_entity_link.count_reportout_classification` の値
2. デフォルト値: 5
3. Value from `user_entity_link.count_reportout_classification`
4. Default value: 5

### 4.4 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常取得 / Successful retrieval |
| 403 Forbidden | アクセス権限なし / No access permission |
| 404 Not Found | 医療機関が見つからない / Medical facility not found |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 5. POST /api/v1/equipment-classifications/report-selection/{medical_id} - レポート選択情報登録 / Create Report Selection Configuration

### 5.1 リクエスト仕様 / Request Specification

#### 5.1.1 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| medical_id | int | ✅ | 医療機関ID / Medical facility ID |

#### 5.1.2 リクエストボディ / Request Body

```json
{
  "classification_ids": [1003, 1015, 1027, 1041, 1052]
}
```

#### 5.1.3 リクエストフィールド / Request Fields

| フィールド / Field | 型 / Type | 必須 / Required | 説明 / Description |
| ---------------- | -------- | ------------- | ------------------- |
| classification_ids | array[int] | ✅ | 機器分類IDリスト（順序が優先順位となる）/ Equipment classification ID list (order becomes priority) |

#### 5.1.4 バリデーション / Validation

- 指定された全ての分類IDが対象医療機関に存在すること / All specified classification IDs must exist for the target medical facility
- 重複する分類IDがないこと / No duplicate classification IDs
- 最大選択数を超えないこと / Must not exceed maximum selectable count

### 5.2 レスポンス仕様 / Response Specification

#### 5.2.1 成功時レスポンス / Success Response

```json
{
  "medical_id": 22,
  "created_count": 5,
  "selections": [
    {
      "rank": 1,
      "classification_id": 1003,
      "classification_name": "メス"
    },
    {
      "rank": 2,
      "classification_id": 1015,
      "classification_name": "内視鏡"
    },
    {
      "rank": 3,
      "classification_id": 1027,
      "classification_name": "人工呼吸器"
    },
    {
      "rank": 4,
      "classification_id": 1041,
      "classification_name": "除細動器"
    },
    {
      "rank": 5,
      "classification_id": 1052,
      "classification_name": "手術台"
    }
  ]
}
```

#### 5.2.2 レスポンスフィールド / Response Fields

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| medical_id | int | 医療機関ID / Medical facility ID |
| created_count | int | 作成された選択数 / Number of created selections |
| selections | array | 作成された選択一覧 / Created selection list |

### 5.3 登録処理詳細 / Registration Process Details

#### 5.3.1 既存データの処理 / Existing Data Processing

- 既存の選択情報は全て削除される / All existing selection information is deleted
- 新しい選択情報で完全に置き換えられる / Completely replaced with new selection information

#### 5.3.2 優先順位の設定 / Priority Setting

- `classification_ids` 配列の順序が優先順位となる / Order of `classification_ids` array becomes priority
- 1番目の要素が rank=1、2番目の要素が rank=2... / 1st element becomes rank=1, 2nd element becomes rank=2...

### 5.4 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常登録 / Successful registration |
| 400 Bad Request | 存在しない分類ID / Non-existent classification ID |
| 403 Forbidden | アクセス権限なし / No access permission |
| 404 Not Found | 医療機関が見つからない / Medical facility not found |
| 422 Unprocessable Entity | バリデーションエラー / Validation error |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 6. DELETE /api/v1/equipment-classifications/report-selection/{medical_id} - レポート選択情報削除 / Delete Report Selection Configuration

### 6.1 リクエスト仕様 / Request Specification

```
DELETE /api/v1/equipment-classifications/report-selection/{medical_id}
```

#### 6.1.1 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| medical_id | int | ✅ | 医療機関ID / Medical facility ID |

### 6.2 レスポンス仕様 / Response Specification

#### 6.2.1 成功時レスポンス / Success Response

```json
{
  "medical_id": 22,
  "deleted_count": 5,
  "message": "レポート選択情報を削除しました"
}
```

#### 6.2.2 レスポンスフィールド / Response Fields

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| medical_id | int | 医療機関ID / Medical facility ID |
| deleted_count | int | 削除された件数 / Number of deleted records |
| message | string | 処理結果メッセージ / Process result message |

### 6.3 削除処理詳細 / Deletion Process Details

- 指定医療機関の全ての選択情報が物理削除される / All selection information for specified medical facility is physically deleted
- 論理削除ではなく、テーブルからレコードが完全に削除される / Records are completely deleted from table, not logical deletion

### 6.4 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常削除 / Successful deletion |
| 403 Forbidden | アクセス権限なし / No access permission |
| 404 Not Found | 医療機関が見つからない / Medical facility not found |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 7. データモデル / Data Model

### 7.1 機器分類マスタ / Equipment Classification Master

#### 7.1.1 mst_equipment_classification テーブル / mst_equipment_classification Table

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| classification_id | int | 分類ID（自動採番）/ Classification ID (auto-generated) |
| medical_id | int | 医療機関ID / Medical facility ID |
| classification_level | int | 階層レベル（1-3）/ Hierarchy level (1-3) |
| parent_classification_id | int | 親分類ID / Parent classification ID |
| classification_name | string | 分類名 / Classification name |
| classification_code | string | 分類コード / Classification code |
| sort_order | int | ソート順 / Sort order |

### 7.2 レポート出力選択 / Report Output Selection

#### 7.2.1 equipment_classification_report_selection テーブル / equipment_classification_report_selection Table

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| medical_id | int | 医療機関ID / Medical facility ID |
| rank | int | 優先順位 / Priority rank |
| classification_id | int | 分類ID / Classification ID |
| reg_user_id | str | 登録ユーザーID / Registration user ID |
| regdate | datetime | 登録日時 / Registration date |
| update_user_id | str | 更新ユーザーID / Update user ID |
| lastupdate | datetime | 最終更新日時 / Last update date |

### 7.3 複合主キー / Composite Primary Key

`equipment_classification_report_selection` テーブルは以下の複合主キーを持ちます：
The `equipment_classification_report_selection` table has the following composite primary key:

- `medical_id` + `rank`

---

## 8. 実装詳細 / Implementation Details

### 8.1 権限チェック / Permission Checking

#### 8.1.1 医療機関アクセス権限チェック / Medical Facility Access Permission Check

```python
# 全エンドポイントで医療機関アクセス権限をチェック
AuthManager.require_medical_permission(current_user_id, medical_id, db)
```

### 8.2 データ検索・ソート / Data Search and Sorting

#### 8.2.1 機器分類の階層順ソート / Hierarchical Sorting of Equipment Classifications

```python
classifications = db.query(MstEquipmentClassification).filter(
    MstEquipmentClassification.medical_id == medical_id
).order_by(
    MstEquipmentClassification.classification_level,
    MstEquipmentClassification.parent_classification_id,
    MstEquipmentClassification.classification_name
).offset(skip).limit(limit).all()
```

#### 8.2.2 レポート選択の優先順ソート / Priority Sorting of Report Selection

```python
selections_query = db.query(
    EquipmentClassificationReportSelection,
    MstEquipmentClassification.classification_name
).join(
    MstEquipmentClassification,
    EquipmentClassificationReportSelection.classification_id == MstEquipmentClassification.classification_id
).filter(
    EquipmentClassificationReportSelection.medical_id == medical_id
).order_by(
    EquipmentClassificationReportSelection.rank
).limit(max_count)
```

### 8.3 トランザクション管理 / Transaction Management

#### 8.3.1 レポート選択情報の登録 / Registration of Report Selection Information

1. 既存データの削除 / Delete existing data
2. 新しいデータの挿入 / Insert new data
3. コミット処理 / Commit process
4. エラー時の自動ロールバック / Automatic rollback on error

---

## 9. エラーハンドリング / Error Handling

### 9.1 バリデーションエラー / Validation Errors

#### 9.1.1 存在しない分類IDエラー / Non-existent Classification ID Error

```json
{
  "detail": "指定された機器分類IDが存在しません: [9999, 8888]"
}
```

#### 9.1.2 医療機関不存在エラー / Medical Facility Not Found Error

```json
{
  "detail": "医療機関ID 999 は存在しません"
}
```

### 9.2 権限エラー / Permission Errors

```json
{
  "detail": "指定された医療機関へのアクセス権限がありません"
}
```

### 9.3 データ整合性エラー / Data Integrity Errors

機器分類の参照整合性チェックにより、存在しない分類IDの選択を防止します。
Reference integrity checks for equipment classifications prevent selection of non-existent classification IDs.

---

## 10. セキュリティ考慮事項 / Security Considerations

### 10.1 アクセス制御 / Access Control

- 医療機関ユーザーは自医療機関の分類情報のみアクセス可能
- 分類IDの存在チェックによるSQLインジェクション対策
- Medical facility users can only access their own facility classification information
- SQL injection prevention through classification ID existence checks

### 10.2 データ保護 / Data Protection

- 機器分類情報は医療機関固有のデータとして適切に分離
- 選択情報の変更履歴は監査ログで追跡可能
- Equipment classification information is properly separated as medical facility-specific data
- Changes to selection information are trackable through audit logs

### 10.3 入力検証 / Input Validation

- 分類IDの数値型チェック / Numeric type check for classification IDs
- 配列の重複チェック / Duplicate check for arrays
- 最大選択数の制限チェック / Maximum selection count limit check

---

## 11. パフォーマンス考慮事項 / Performance Considerations

### 11.1 ページネーション / Pagination

- 最大取得件数: 1000件 / Maximum retrieval limit: 1000 records
- デフォルトページサイズ: 100件 / Default page size: 100 records
- 大量データの効率的な取得をサポート / Supports efficient retrieval of large amounts of data

### 11.2 データベース最適化 / Database Optimization

#### 11.2.1 インデックス活用 / Index Utilization

- `medical_id` による効率的なフィルタリング / Efficient filtering by `medical_id`
- 階層構造による効率的なソート / Efficient sorting by hierarchy structure

#### 11.2.2 JOIN最適化 / JOIN Optimization

- 必要最小限のテーブル結合 / Minimum necessary table joins
- 分類名取得時の効率的なクエリ / Efficient queries when retrieving classification names

---

## 12. テスト項目 / Test Cases

### 12.1 正常系テスト / Normal Test Cases

- [ ] 機器分類一覧取得（管理者）
- [ ] 機器分類一覧取得（医療機関ユーザー）
- [ ] 機器分類ページング取得
- [ ] レポート選択情報取得
- [ ] レポート選択情報登録
- [ ] レポート選択情報削除
- [ ] 階層構造のソート確認

### 12.2 異常系テスト / Error Test Cases

- [ ] 権限なしでの他医療機関分類アクセス
- [ ] 存在しない医療機関IDでの操作
- [ ] 存在しない分類IDでの選択登録
- [ ] 最大選択数超過での登録
- [ ] 重複分類IDでの登録
- [ ] 無効なページング パラメータ

---

## 13. 今後の拡張予定 / Future Enhancements

### 13.1 機能拡張 / Feature Enhancement

- 機器分類の動的追加・編集機能 / Dynamic addition and editing of equipment classifications
- 分類階層の可視化機能 / Visualization of classification hierarchy
- 選択履歴の管理機能 / Selection history management functionality
- 一括選択・解除機能 / Bulk selection and deselection functionality

### 13.2 レポート機能拡張 / Report Functionality Enhancement

- 選択基準の詳細設定 / Detailed selection criteria settings
- 条件付き選択ルール / Conditional selection rules
- 自動選択推奨機能 / Automatic selection recommendation functionality

### 13.3 データ管理強化 / Data Management Enhancement

- 分類マスタの自動同期 / Automatic synchronization of classification master
- 分類統計情報の提供 / Provision of classification statistics
- 使用頻度に基づく選択候補提示 / Presentation of selection candidates based on usage frequency

---

## 14. 関連資料 / Related Documents

- **プログラム仕様書**: `design/backend/proc/proc_equipment_classifications.md`
- **スキーマ定義**: `src/schemas/equipment_classification.py`
- **テストケース**: `tests/test_06_equipment_classifications_api.py`
- **データベース設計**: `design/database/pg_optigate/mst_equipment_classification.yaml`, `design/database/pg_optigate/equipment_classification_report_selection.yaml`
- **認証管理**: `src/utils/auth.py`
- **ユーザー組織連携**: `src/models/pg_optigate/user_entity_link.py`