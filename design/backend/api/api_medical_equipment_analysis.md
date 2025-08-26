# 🔬 医療機器分析設定API仕様書 / Medical Equipment Analysis Settings API Specification

**対象API**: `/api/v1/medical-equipment-analysis-settings`

---

## 1. 概要 / Overview

### 1.1 API説明 / API Description

医療機器台帳のデフォルト設定に対する医療機関別の上書き設定を管理するAPIです。機器ごとの分析対象フラグと分類上書き設定を管理し、デフォルト値と同じ設定は保存しない差分管理により効率化を図ります。各設定には変更履歴（note）が記録され、変更理由と実施者を追跡可能です。

This API manages medical facility-specific override settings for default settings in the medical equipment ledger. It manages analysis target flags and classification override settings for each equipment, achieving efficiency through differential management that does not save settings identical to default values. Each setting records change history (note) for tracking reasons and implementers.

### 1.2 エンドポイント一覧 / Endpoint List

| エンドポイント / Endpoint | メソッド / Method | 説明 / Description |
| -------------------- | --------------- | ------------------- |
| `/api/v1/medical-equipment-analysis-settings` | GET | 分析設定一覧取得 / Get analysis settings list |
| `/api/v1/medical-equipment-analysis-settings/{ledger_id}/analysis-target` | PUT | 分析対象フラグ更新 / Update analysis target flag |
| `/api/v1/medical-equipment-analysis-settings/{ledger_id}/classification` | PUT | 分類上書き更新 / Update classification override |
| `/api/v1/medical-equipment-analysis-settings` | DELETE | 全設定デフォルト復帰 / Restore all settings to default |
| `/api/v1/medical-equipment-analysis-settings/{ledger_id}` | DELETE | 単一設定デフォルト復帰 / Restore single setting to default |

### 1.3 実装ファイル / Implementation Files

- **Router**: `src/routers/medical_equipment_analysis.py`
- **Schema**: `src/schemas/medical_equipment_analysis.py`
- **Model**: `src/models/pg_optigate/medical_equipment_ledger.py`, `src/models/pg_optigate/medical_equipment_analysis_setting.py`
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

- **システム管理者** (user_id: 900001-999999): 全医療機関の分析設定へのアクセス可能
- **医療機関ユーザー** (entity_type=1): 自医療機関の分析設定のみアクセス可能
- **System Administrator** (user_id: 900001-999999): Access to all medical facility analysis settings
- **Medical Facility User** (entity_type=1): Access only to their own medical facility analysis settings

### 2.3 データ管理概念 / Data Management Concept

#### 2.3.1 差分管理 / Differential Management

- デフォルト値と同じ設定は保存しない / Do not save settings identical to default values
- 上書き設定のみをデータベースに保存 / Save only override settings to database
- 効率的なストレージ使用 / Efficient storage usage

#### 2.3.2 変更履歴管理 / Change History Management

- 各設定変更時に理由と実施者を記録 / Record reason and implementer for each setting change
- JSON形式での履歴保存 / Save history in JSON format
- 完全な変更追跡 / Complete change tracking

---

## 3. GET /api/v1/medical-equipment-analysis-settings - 分析設定一覧取得 / Get Analysis Settings List

### 3.1 リクエスト仕様 / Request Specification

```
GET /api/v1/medical-equipment-analysis-settings?medical_id={id}&classification_id={cid}&skip={offset}&limit={count}
```

#### 3.1.1 クエリパラメータ / Query Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| medical_id | int | ❌ | 医療機関ID（省略時は認証ユーザーの医療機関）/ Medical facility ID (defaults to authenticated user's facility) |
| classification_id | int | ❌ | 分類IDでフィルタ / Filter by classification ID |
| skip | int | ❌ | スキップ件数（デフォルト: 0）/ Skip count (default: 0) |
| limit | int | ❌ | 取得件数（デフォルト: 100、最大: 1000）/ Limit count (default: 100, max: 1000) |

#### 3.1.2 リクエスト例 / Request Examples

```
# 認証ユーザーの医療機関の全件取得
GET /api/v1/medical-equipment-analysis-settings

# 指定医療機関の全件取得
GET /api/v1/medical-equipment-analysis-settings?medical_id=22

# 指定分類でフィルタ
GET /api/v1/medical-equipment-analysis-settings?classification_id=123

# ページング取得
GET /api/v1/medical-equipment-analysis-settings?skip=100&limit=100
```

### 3.2 レスポンス仕様 / Response Specification

#### 3.2.1 成功時レスポンス / Success Response

```json
{
  "items": [
    {
      "ledger_id": 1001,
      "medical_id": 22,
      "model_number": "ABC-123",
      "product_name": "医療用監視装置",
      "maker_name": "○○メディカル",
      "stock_quantity": 5,
      "default_is_included": true,
      "default_classification_id": 101,
      "effective_is_included": false,
      "effective_classification_id": 102,
      "has_override": true,
      "override_is_included": false,
      "override_classification_id": 102,
      "classification_name": "監視装置（上書き）",
      "classification_level": 2,
      "note_history": [
        {
          "user_id": "100001",
          "timestamp": "2025-08-19T10:30:00",
          "note": "院内ルールにより監視装置分類に変更"
        }
      ],
      "last_modified": "2025-08-19T10:30:00",
      "last_modified_user_id": "100001"
    }
  ],
  "total_count": 1500,
  "has_next": true
}
```

#### 3.2.2 レスポンスフィールド / Response Fields

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| items | array | 機器分析設定一覧 / Equipment analysis settings list |
| total_count | int | 総件数 / Total count |
| has_next | bool | 次ページ有無 / Has next page |

#### 3.2.3 機器分析設定項目 / Equipment Analysis Setting Item Fields

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| ledger_id | int | 機器台帳ID / Equipment ledger ID |
| medical_id | int | 医療機関ID / Medical facility ID |
| model_number | string | 型番 / Model number |
| product_name | string | 製品名 / Product name |
| maker_name | string | メーカー名 / Maker name |
| stock_quantity | int | 在庫数 / Stock quantity |
| default_is_included | bool | デフォルト分析対象フラグ / Default analysis target flag |
| default_classification_id | int | デフォルト分類ID / Default classification ID |
| effective_is_included | bool | 有効分析対象フラグ / Effective analysis target flag |
| effective_classification_id | int | 有効分類ID / Effective classification ID |
| has_override | bool | 上書き設定有無 / Has override settings |
| override_is_included | bool | 上書き分析対象フラグ / Override analysis target flag |
| override_classification_id | int | 上書き分類ID / Override classification ID |
| classification_name | string | 分類名 / Classification name |
| classification_level | int | 分類レベル / Classification level |
| note_history | array | 変更履歴 / Change history |
| last_modified | datetime | 最終更新日時 / Last modified date |
| last_modified_user_id | str | 最終更新ユーザーID / Last modified user ID |

### 3.3 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常取得 / Successful retrieval |
| 403 Forbidden | アクセス権限なし / No access permission |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 4. PUT /api/v1/medical-equipment-analysis-settings/{ledger_id}/analysis-target - 分析対象フラグ更新 / Update Analysis Target Flag

### 4.1 リクエスト仕様 / Request Specification

#### 4.1.1 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| ledger_id | int | ✅ | 機器台帳ID / Equipment ledger ID |

#### 4.1.2 リクエストボディ / Request Body

```json
{
  "override_is_included": false,
  "note": "重要機器のため分析対象から除外"
}
```

#### 4.1.3 リクエストフィールド / Request Fields

| フィールド / Field | 型 / Type | 必須 / Required | 説明 / Description |
| ---------------- | -------- | ------------- | ------------------- |
| override_is_included | bool | ✅ | 上書きする分析対象フラグ / Analysis target flag to override |
| note | string | ✅ | 変更理由・補足情報（最大500文字）/ Reason for change (max 500 chars) |

#### 4.1.4 バリデーション / Validation

- デフォルト値と同じ値は設定不可 / Cannot set same value as default
- 変更理由（note）は必須 / Change reason (note) is required
- noteは最大500文字 / note maximum 500 characters

### 4.2 レスポンス仕様 / Response Specification

#### 4.2.1 成功時レスポンス / Success Response

```json
{
  "ledger_id": 1001,
  "override_is_included": false,
  "effective_is_included": false,
  "updated_at": "2025-08-19T10:30:00",
  "message": "分析対象フラグを更新しました"
}
```

#### 4.2.2 レスポンスフィールド / Response Fields

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| ledger_id | int | 機器台帳ID / Equipment ledger ID |
| override_is_included | bool | 上書き分析対象フラグ / Override analysis target flag |
| effective_is_included | bool | 有効分析対象フラグ / Effective analysis target flag |
| updated_at | datetime | 更新日時 / Update datetime |
| message | string | 処理結果メッセージ / Process result message |

### 4.3 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常更新 / Successful update |
| 400 Bad Request | デフォルト値と同じ値を設定 / Trying to set same value as default |
| 404 Not Found | 機器が見つからない / Equipment not found |
| 422 Unprocessable Entity | バリデーションエラー / Validation error |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 5. PUT /api/v1/medical-equipment-analysis-settings/{ledger_id}/classification - 分類上書き更新 / Update Classification Override

### 5.1 リクエスト仕様 / Request Specification

#### 5.1.1 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| ledger_id | int | ✅ | 機器台帳ID / Equipment ledger ID |

#### 5.1.2 リクエストボディ / Request Body

```json
{
  "override_classification_id": 456,
  "note": "院内ルールにより呼吸器分類に変更"
}
```

#### 5.1.3 リクエストフィールド / Request Fields

| フィールド / Field | 型 / Type | 必須 / Required | 説明 / Description |
| ---------------- | -------- | ------------- | ------------------- |
| override_classification_id | int | ✅ | 上書きする分類ID / Classification ID to override |
| note | string | ✅ | 変更理由・補足情報（最大500文字）/ Reason for change (max 500 chars) |

#### 5.1.4 バリデーション / Validation

- デフォルト値と同じ分類IDは設定不可 / Cannot set same classification ID as default
- 指定した分類IDが存在すること / Specified classification ID must exist
- 変更理由（note）は必須 / Change reason (note) is required

### 5.2 レスポンス仕様 / Response Specification

#### 5.2.1 成功時レスポンス / Success Response

```json
{
  "ledger_id": 1001,
  "override_classification_id": 456,
  "effective_classification_id": 456,
  "classification_name": "呼吸器",
  "updated_at": "2025-08-19T10:30:00",
  "message": "分類上書きを更新しました"
}
```

#### 5.2.2 レスポンスフィールド / Response Fields

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| ledger_id | int | 機器台帳ID / Equipment ledger ID |
| override_classification_id | int | 上書き分類ID / Override classification ID |
| effective_classification_id | int | 有効分類ID / Effective classification ID |
| classification_name | string | 分類名 / Classification name |
| updated_at | datetime | 更新日時 / Update datetime |
| message | string | 処理結果メッセージ / Process result message |

### 5.3 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常更新 / Successful update |
| 400 Bad Request | デフォルト値と同じ分類IDまたは存在しない分類ID / Same classification ID as default or non-existent classification ID |
| 404 Not Found | 機器が見つからない / Equipment not found |
| 422 Unprocessable Entity | バリデーションエラー / Validation error |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 6. DELETE /api/v1/medical-equipment-analysis-settings - 全設定デフォルト復帰 / Restore All Settings to Default

### 6.1 リクエスト仕様 / Request Specification

```
DELETE /api/v1/medical-equipment-analysis-settings?medical_id={id}
```

#### 6.1.1 クエリパラメータ / Query Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| medical_id | int | ✅ | 医療機関ID / Medical facility ID |

#### 6.1.2 リクエスト例 / Request Example

```
DELETE /api/v1/medical-equipment-analysis-settings?medical_id=22
```

### 6.2 レスポンス仕様 / Response Specification

#### 6.2.1 成功時レスポンス / Success Response

```json
{
  "affected_count": 150,
  "ledger_ids": [1001, 1005, 1023, 1047],
  "message": "医療機関ID 22 の 150 件の設定をデフォルトに復帰しました"
}
```

#### 6.2.2 レスポンスフィールド / Response Fields

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| affected_count | int | 削除された設定数 / Number of deleted settings |
| ledger_ids | array[int] | 影響を受けた機器台帳IDリスト / List of affected equipment ledger IDs |
| message | string | 処理結果メッセージ / Process result message |

### 6.3 注意事項 / Important Notes

⚠️ **この操作は取り消しできません / This operation cannot be undone**

- 該当医療機関のすべての上書き設定が削除される / All override settings for the medical facility will be deleted
- 変更履歴も完全に削除される / Change history will also be completely deleted
- 復帰処理後は機器台帳のデフォルト設定が適用される / Default settings from equipment ledger will be applied after restoration

### 6.4 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常削除 / Successful deletion |
| 403 Forbidden | アクセス権限なし / No access permission |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 7. DELETE /api/v1/medical-equipment-analysis-settings/{ledger_id} - 単一設定デフォルト復帰 / Restore Single Setting to Default

### 7.1 リクエスト仕様 / Request Specification

```
DELETE /api/v1/medical-equipment-analysis-settings/{ledger_id}
```

#### 7.1.1 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| ledger_id | int | ✅ | 機器台帳ID / Equipment ledger ID |

#### 7.1.2 リクエスト例 / Request Example

```
DELETE /api/v1/medical-equipment-analysis-settings/1001
```

### 7.2 レスポンス仕様 / Response Specification

#### 7.2.1 成功時レスポンス / Success Response

```json
{
  "affected_count": 1,
  "ledger_ids": [1001],
  "message": "機器台帳ID 1001 の設定をデフォルトに復帰しました"
}
```

### 7.3 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常削除 / Successful deletion |
| 404 Not Found | 機器または設定が見つからない / Equipment or setting not found |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 8. データモデル / Data Model

### 8.1 機器台帳 / Equipment Ledger

#### 8.1.1 medical_equipment_ledger テーブル / medical_equipment_ledger Table

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| ledger_id | int | 機器台帳ID（自動採番）/ Equipment ledger ID (auto-generated) |
| medical_id | int | 医療機関ID / Medical facility ID |
| model_number | string | 型番 / Model number |
| product_name | string | 製品名 / Product name |
| maker_name | string | メーカー名 / Maker name |
| stock_quantity | int | 在庫数 / Stock quantity |
| is_included | bool | デフォルト分析対象フラグ / Default analysis target flag |
| classification_id | int | デフォルト分類ID / Default classification ID |

### 8.2 分析設定上書き / Analysis Setting Override

#### 8.2.1 medical_equipment_analysis_setting テーブル / medical_equipment_analysis_setting Table

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| ledger_id | int | 機器台帳ID（主キー）/ Equipment ledger ID (primary key) |
| override_is_included | bool | 上書き分析対象フラグ / Override analysis target flag |
| override_classification_id | int | 上書き分類ID / Override classification ID |
| note | text | 変更履歴（JSON形式）/ Change history (JSON format) |
| reg_user_id | str | 登録ユーザーID / Registration user ID |
| regdate | datetime | 登録日時 / Registration date |
| update_user_id | str | 更新ユーザーID / Update user ID |
| lastupdate | datetime | 最終更新日時 / Last update date |

### 8.3 変更履歴 / Change History

#### 8.3.1 履歴項目形式 / History Item Format

```json
{
  "user_id": "100001",
  "timestamp": "2025-08-19T10:30:00",
  "note": "院内ルールにより呼吸器分類に変更"
}
```

#### 8.3.2 履歴配列形式 / History Array Format

```json
[
  {
    "user_id": "100001",
    "timestamp": "2025-08-19T10:30:00",
    "note": "初回設定"
  },
  {
    "user_id": 100002,
    "timestamp": "2025-08-20T14:15:00",
    "note": "院内ルールにより呼吸器分類に変更"
  }
]
```

---

## 9. 実装詳細 / Implementation Details

### 9.1 差分管理システム / Differential Management System

#### 9.1.1 設定保存ロジック / Setting Save Logic

```python
# デフォルト値との比較
if request.override_is_included == ledger.is_included:
    raise HTTPException(
        status_code=400, 
        detail=f"デフォルト値（{ledger.is_included}）と同じ値は設定できません"
    )
```

#### 9.1.2 有効値の決定 / Effective Value Determination

```python
# 有効な値を決定
effective_is_included = (
    analysis_setting.override_is_included 
    if analysis_setting else ledger.is_included
)
effective_classification_id = (
    analysis_setting.override_classification_id 
    if analysis_setting and analysis_setting.override_classification_id 
    else ledger.classification_id
)
```

### 9.2 変更履歴管理 / Change History Management

#### 9.2.1 履歴項目作成 / History Item Creation

```python
def create_note_history_item(user_id: str, note: str) -> Dict[str, Any]:
    """履歴アイテムを作成"""
    return {
        "user_id": user_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "note": note
    }
```

#### 9.2.2 履歴追加 / History Append

```python
def append_note_history(existing_note: str, new_item: Dict[str, Any]) -> str:
    """既存の履歴に新しいアイテムを追加"""
    try:
        if existing_note:
            history = json.loads(existing_note)
        else:
            history = []
        history.append(new_item)
        return json.dumps(history, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        return json.dumps([new_item], ensure_ascii=False)
```

### 9.3 複雑なクエリ処理 / Complex Query Processing

#### 9.3.1 機器台帳と上書き設定の結合 / Joining Equipment Ledger and Override Settings

```python
base_query = db.query(
    MedicalEquipmentLedger,
    MedicalEquipmentAnalysisSetting,
    MstEquipmentClassification
).outerjoin(
    MedicalEquipmentAnalysisSetting,
    MedicalEquipmentLedger.ledger_id == MedicalEquipmentAnalysisSetting.ledger_id
).outerjoin(
    MstEquipmentClassification,
    MedicalEquipmentLedger.classification_id == MstEquipmentClassification.classification_id
).filter(
    MedicalEquipmentLedger.medical_id == target_medical_id
)
```

---

## 10. エラーハンドリング / Error Handling

### 10.1 差分管理エラー / Differential Management Errors

#### 10.1.1 デフォルト値と同じ値エラー / Same Value as Default Error

```json
{
  "detail": "デフォルト値（true）と同じ値は設定できません。デフォルト値を使用する場合は設定を削除してください。"
}
```

#### 10.1.2 存在しない分類IDエラー / Non-existent Classification ID Error

```json
{
  "detail": "指定された分類IDが存在しません"
}
```

### 10.2 権限エラー / Permission Errors

```json
{
  "detail": "指定された医療機関へのアクセス権限がありません"
}
```

### 10.3 データ不存在エラー / Data Not Found Errors

```json
{
  "detail": "指定された機器が見つかりません"
}
```

---

## 11. セキュリティ考慮事項 / Security Considerations

### 11.1 アクセス制御 / Access Control

- 医療機関ユーザーは自医療機関の機器設定のみアクセス可能
- 機器台帳IDの所有権チェック
- Medical facility users can only access their own facility equipment settings
- Ownership check for equipment ledger IDs

### 11.2 データ整合性 / Data Integrity

- 分類IDの存在チェック / Classification ID existence check
- 差分管理による不正値の防止 / Prevention of invalid values through differential management
- 変更履歴の改ざん防止 / Prevention of change history tampering

### 11.3 監査証跡 / Audit Trail

- 全変更の完全な履歴記録 / Complete history record of all changes
- 変更理由の必須化 / Mandatory change reasons
- 実施者の追跡可能性 / Traceability of implementers

---

## 12. パフォーマンス考慮事項 / Performance Considerations

### 12.1 クエリ最適化 / Query Optimization

#### 12.1.1 外部結合の効率化 / Efficient Outer Joins

- 必要最小限のテーブル結合 / Minimum necessary table joins
- インデックスの効果的な活用 / Effective use of indexes

#### 12.1.2 ページネーション / Pagination

- 大量データの効率的な取得 / Efficient retrieval of large amounts of data
- 最大取得件数制限（1000件）/ Maximum retrieval limit (1000 records)

### 12.2 差分管理の効率性 / Efficiency of Differential Management

- デフォルト値と同じ設定は保存しない / Do not save settings identical to default values
- ストレージ使用量の最適化 / Optimization of storage usage
- 処理速度の向上 / Improvement of processing speed

---

## 13. テスト項目 / Test Cases

### 13.1 正常系テスト / Normal Test Cases

- [ ] 分析設定一覧取得（管理者）
- [ ] 分析設定一覧取得（医療機関ユーザー）
- [ ] 分類IDフィルタでの検索
- [ ] 分析対象フラグ更新
- [ ] 分類上書き更新
- [ ] 単一設定デフォルト復帰
- [ ] 全設定デフォルト復帰
- [ ] 変更履歴の追跡

### 13.2 異常系テスト / Error Test Cases

- [ ] 権限なしでの他医療機関設定アクセス
- [ ] 存在しない機器IDでの操作
- [ ] デフォルト値と同じ値での更新
- [ ] 存在しない分類IDでの上書き
- [ ] 変更理由なしでの更新
- [ ] 無効なページングパラメータ

---

## 14. 今後の拡張予定 / Future Enhancements

### 14.1 機能拡張 / Feature Enhancement

- 一括設定更新機能 / Bulk setting update functionality
- 設定テンプレート機能 / Setting template functionality
- 自動設定推奨機能 / Automatic setting recommendation functionality
- 設定の複製機能 / Setting duplication functionality

### 14.2 分析機能拡張 / Analysis Functionality Enhancement

- 設定変更の影響分析 / Impact analysis of setting changes
- 使用頻度に基づく自動最適化 / Automatic optimization based on usage frequency
- 分析結果の比較機能 / Analysis result comparison functionality

### 14.3 運用機能強化 / Operational Functionality Enhancement

- 設定変更の承認ワークフロー / Approval workflow for setting changes
- 一時的な設定適用機能 / Temporary setting application functionality
- 設定のスケジュール変更 / Scheduled setting changes

---

## 15. 関連資料 / Related Documents

- **プログラム仕様書**: `design/backend/proc/proc_medical_equipment_analysis.md`
- **スキーマ定義**: `src/schemas/medical_equipment_analysis.py`
- **テストケース**: `tests/test_07_medical_equipment_analysis_api.py`
- **データベース設計**: `design/database/pg_optigate/medical_equipment_ledger.yaml`, `design/database/pg_optigate/medical_equipment_analysis_setting.yaml`
- **認証管理**: `src/utils/auth.py`
- **機器分類マスタ**: `src/models/pg_optigate/mst_equipment_classification.py`