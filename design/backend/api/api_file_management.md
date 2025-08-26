# 📁 ファイル管理API仕様書 / File Management API Specification

**対象API**: `/api/v1/files`

---

## 1. 概要 / Overview

### 1.1 API説明 / API Description

医療機関からのファイルアップロードとシステム生成レポートのダウンロード機能を提供するAPIです。月次運用に対応し、3種類のファイル（医療機器台帳・貸出履歴・故障履歴）の同時アップロードと、3種類のレポート（分析レポート・故障リスト・未実績リスト）の配信機能をサポートします。

This API provides file upload functionality from medical facilities and download functionality for system-generated reports. It supports monthly operations with simultaneous upload of 3 types of files (medical equipment ledger, rental history, failure history) and distribution of 3 types of reports (analysis report, failure list, unachieved list).

### 1.2 エンドポイント一覧 / Endpoint List

| エンドポイント / Endpoint | メソッド / Method | 説明 / Description | 対象ユーザー / Target Users |
| -------------------- | --------------- | ------------------- | -------------------------- |
| `/api/v1/files/upload-files/{medical_id}` | POST | 月次ファイル一括アップロード / Monthly file bulk upload | 医療機関ユーザー / Medical facility users |
| `/api/v1/files/upload-status/{medical_id}` | GET | アップロード状況取得 / Get upload status | 医療機関ユーザー / Medical facility users |
| `/api/v1/files/reports/available/{medical_id}` | GET | ダウンロード可能レポート一覧 / Get available reports | 医療機関ユーザー / Medical facility users |
| `/api/v1/files/reports/download/{publication_id}` | GET | レポートダウンロード / Download report | 医療機関ユーザー / Medical facility users |
| `/api/v1/files/system/fetch-uploaded/{medical_id}` | GET | システム用ファイル取得 / System file fetch | システム / System |
| `/api/v1/files/reports/publish/{medical_id}` | POST | 月次レポート公開 / Publish monthly reports | システム / System |

### 1.3 実装ファイル / Implementation Files

- **Router**: `src/routers/file_management.py`
- **Schema**: `src/schemas/facility_upload.py`, `src/schemas/report_publication.py`, `src/schemas/file_management.py`
- **Model**: `src/models/pg_optigate/facility_upload_log.py`, `src/models/pg_optigate/report_publication_log.py`
- **Utils**: `src/utils/auth.py`

---

## 2. 共通仕様 / Common Specifications

### 2.1 認証ヘッダー / Authentication Header

ユーザー向けエンドポイントで必須：
Required for user-facing endpoints:

```
X-User-Id: {user_id}
```

システム向けエンドポイントで必須：
Required for system endpoints:

```
X-System-Key: {system_api_key}
```

### 2.2 ファイル構成 / File Structure

```
files/
├── uploads/                    # 医療機関からのアップロード（1世代保管）
│   └── {medical_id}/
│       ├── equipment.csv       # 医療機器台帳（上書き保存）
│       ├── rental.csv          # 貸出履歴（上書き保存）
│       └── failure.csv         # 故障履歴（上書き保存）
└── reports/                    # システム生成レポート
    └── {medical_id}/
        └── {YYYY}/{MM}/        # 年/月階層構造
            ├── analysis_report.pdf    # 分析レポート
            ├── failure_list.xlsx      # 故障リスト
            └── unachieved_list.xlsx   # 未実績リスト
```

### 2.3 ファイル種別定義 / File Type Definition

#### 2.3.1 アップロードファイル / Upload Files

| file_type | ファイル名 / Filename | 拡張子 / Extension | 説明 / Description |
| --------- | ------------------- | ------------------ | ------------------- |
| 1 | equipment.csv | .csv | 医療機器台帳 / Medical equipment ledger |
| 2 | rental.csv | .csv | 貸出履歴 / Rental history |
| 3 | failure.csv | .csv | 故障履歴 / Failure history |

#### 2.3.2 レポートファイル / Report Files

| file_type | ファイル名 / Filename | 拡張子 / Extension | 説明 / Description |
| --------- | ------------------- | ------------------ | ------------------- |
| 1 | analysis_report.pdf | .pdf | 分析レポート / Analysis report |
| 2 | failure_list.xlsx | .xlsx | 故障リスト / Failure list |
| 3 | unachieved_list.xlsx | .xlsx | 未実績リスト / Unachieved list |

---

## 3. POST /api/v1/files/upload-files/{medical_id} - 月次ファイル一括アップロード / Monthly File Bulk Upload

### 3.1 リクエスト仕様 / Request Specification

#### 3.1.1 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| medical_id | int | ✅ | 医療機関ID / Medical facility ID |

#### 3.1.2 フォームデータ / Form Data

| フィールド / Field | 型 / Type | 必須 / Required | 説明 / Description |
| ---------------- | -------- | ------------- | ------------------- |
| upload_user_id | str | ✅ | アップロードを行うユーザーID / Upload user ID |
| equipment_file | UploadFile | ✅ | 医療機器台帳ファイル（CSV）/ Medical equipment file (CSV) |
| rental_file | UploadFile | ✅ | 貸出履歴ファイル（CSV）/ Rental history file (CSV) |
| failure_file | UploadFile | ✅ | 故障履歴ファイル（CSV）/ Failure history file (CSV) |

#### 3.1.3 リクエスト例 / Request Example

```http
POST /api/v1/files/upload-files/22
Content-Type: multipart/form-data
X-User-Id: "100001"

Form data:
- upload_user_id: "100001"
- equipment_file: equipment_202508.csv
- rental_file: rental_202508.csv
- failure_file: failure_202508.csv
```

### 3.2 レスポンス仕様 / Response Specification

#### 3.2.1 成功時レスポンス / Success Response

```json
{
  "success": true,
  "message": "3つのファイルのアップロードが完了しました",
  "medical_id": 22,
  "upload_datetime": "2025-08-19T10:30:00",
  "uploaded_files": [
    {
      "uploadlog_id": 101,
      "medical_id": 22,
      "file_type": 1,
      "original_filename": "equipment_202508.csv",
      "file_size": 1024000,
      "upload_user_id": "100001",
      "upload_datetime": "2025-08-19T10:30:00",
      "download_datetime": null,
      "reg_user_id": "100001",
      "regdate": "2025-08-19T10:30:00",
      "update_user_id": "100001",
      "lastupdate": "2025-08-19T10:30:00"
    },
    {
      "uploadlog_id": 102,
      "medical_id": 22,
      "file_type": 2,
      "original_filename": "rental_202508.csv",
      "file_size": 512000,
      "upload_user_id": "100001",
      "upload_datetime": "2025-08-19T10:30:00",
      "download_datetime": null,
      "reg_user_id": "100001",
      "regdate": "2025-08-19T10:30:00",
      "update_user_id": "100001",
      "lastupdate": "2025-08-19T10:30:00"
    },
    {
      "uploadlog_id": 103,
      "medical_id": 22,
      "file_type": 3,
      "original_filename": "failure_202508.csv",
      "file_size": 256000,
      "upload_user_id": "100001",
      "upload_datetime": "2025-08-19T10:30:00",
      "download_datetime": null,
      "reg_user_id": "100001",
      "regdate": "2025-08-19T10:30:00",
      "update_user_id": "100001",
      "lastupdate": "2025-08-19T10:30:00"
    }
  ],
  "notification_sent": true
}
```

### 3.3 機能詳細 / Feature Details

#### 3.3.1 アップロード処理 / Upload Process

1. ファイル拡張子バリデーション（.csv必須）/ File extension validation (.csv required)
2. 医療機関アクセス権限チェック / Medical facility access permission check
3. ファイル保存（既存ファイル上書き）/ File saving (overwrite existing files)
4. アップロード履歴DB記録 / Upload history DB recording
5. 通知メール送信 / Notification email sending

#### 3.3.2 通知機能 / Notification Feature

- `user_entity_link.notification_email_list`のメンバーに自動通知
- Auto-notification to members in `user_entity_link.notification_email_list`

### 3.4 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常アップロード / Successful upload |
| 400 Bad Request | ファイル形式エラー / File format error |
| 403 Forbidden | アクセス権限なし / No access permission |
| 422 Unprocessable Entity | バリデーションエラー / Validation error |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 4. GET /api/v1/files/upload-status/{medical_id} - アップロード状況取得 / Get Upload Status

### 4.1 リクエスト仕様 / Request Specification

#### 4.1.1 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| medical_id | int | ✅ | 医療機関ID / Medical facility ID |

#### 4.1.2 クエリパラメータ / Query Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | デフォルト / Default | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- | ------------------- |
| months | int | ❌ | 6 | 取得対象月数 / Number of months to retrieve |

### 4.2 レスポンス仕様 / Response Specification

#### 4.2.1 成功時レスポンス / Success Response

```json
[
  {
    "month": "2025-08",
    "equipment_file": {
      "uploaded": true,
      "upload_date": "2025-08-19T10:30:00",
      "file_size": 1024000
    },
    "rental_file": {
      "uploaded": true,
      "upload_date": "2025-08-19T10:30:00",
      "file_size": 512000
    },
    "failure_file": {
      "uploaded": true,
      "upload_date": "2025-08-19T10:30:00",
      "file_size": 256000
    }
  }
]
```

**注意**: このエンドポイントは現在実装中です（TODO）
**Note**: This endpoint is currently under implementation (TODO)

---

## 5. GET /api/v1/files/reports/available/{medical_id} - ダウンロード可能レポート一覧 / Get Available Reports

### 5.1 リクエスト仕様 / Request Specification

#### 5.1.1 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| medical_id | int | ✅ | 医療機関ID / Medical facility ID |

#### 5.1.2 クエリパラメータ / Query Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | デフォルト / Default | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- | ------------------- |
| months | int | ❌ | 12 | 取得対象月数 / Number of months to retrieve |

### 5.2 レスポンス仕様 / Response Specification

#### 5.2.1 成功時レスポンス / Success Response

```json
[
  {
    "publication_id": 201,
    "medical_id": 22,
    "publication_ym": "2025-08",
    "file_type": 1,
    "file_name": "analysis_report.pdf",
    "file_size": 2048000,
    "publication_datetime": "2025-08-25T09:00:00",
    "download_datetime": null,
    "downloaded": false
  },
  {
    "publication_id": 202,
    "medical_id": 22,
    "publication_ym": "2025-08",
    "file_type": 2,
    "file_name": "failure_list.xlsx",
    "file_size": 1024000,
    "publication_datetime": "2025-08-25T09:00:00",
    "download_datetime": "2025-08-26T14:30:00",
    "downloaded": true
  }
]
```

**注意**: このエンドポイントは現在実装中です（TODO）
**Note**: This endpoint is currently under implementation (TODO)

---

## 6. GET /api/v1/files/reports/download/{publication_id} - レポートダウンロード / Download Report

### 6.1 リクエスト仕様 / Request Specification

#### 6.1.1 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| publication_id | int | ✅ | レポート公開ID / Report publication ID |

#### 6.1.2 クエリパラメータ / Query Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| user_id | str | ✅ | ダウンロードを行うユーザーID / Download user ID |

#### 6.1.3 リクエスト例 / Request Example

```http
GET /api/v1/files/reports/download/201?user_id="100001"
X-User-Id: "100001"
```

### 6.2 レスポンス仕様 / Response Specification

#### 6.2.1 成功時レスポンス / Success Response

```
Content-Type: application/pdf (or appropriate MIME type)
Content-Disposition: attachment; filename="analysis_report.pdf"

[Binary file content]
```

### 6.3 機能詳細 / Feature Details

#### 6.3.1 ダウンロード処理 / Download Process

1. レポート公開情報の取得 / Retrieve report publication information
2. ファイル存在チェック / File existence check
3. 初回ダウンロード時のDB更新 / DB update on first download
4. ファイル配信 / File delivery

#### 6.3.2 MIMEタイプ設定 / MIME Type Setting

| 拡張子 / Extension | MIMEタイプ / MIME Type |
| ----------------- | --------------------- |
| .pdf | application/pdf |
| .xlsx, .xls | application/vnd.openxmlformats-officedocument.spreadsheetml.sheet |
| .pptx | application/vnd.openxmlformats-officedocument.presentationml.presentation |
| その他 / Others | application/octet-stream |

### 6.4 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常ダウンロード / Successful download |
| 404 Not Found | レポートまたはファイルが見つからない / Report or file not found |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 7. GET /api/v1/files/system/fetch-uploaded/{medical_id} - システム用ファイル取得 / System File Fetch

### 7.1 リクエスト仕様 / Request Specification

#### 7.1.1 認証要件 / Authentication Requirements

システム認証キーが必須です：
System authentication key required:

```
X-System-Key: {system_api_key}
```

#### 7.1.2 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| medical_id | int | ✅ | 医療機関ID / Medical facility ID |

#### 7.1.3 クエリパラメータ / Query Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| file_type | int | ✅ | ファイル種別（1-3）/ File type (1-3) |

### 7.2 レスポンス仕様 / Response Specification

#### 7.2.1 成功時レスポンス / Success Response

```
Content-Type: text/csv
Content-Disposition: attachment; filename="equipment.csv"

[CSV file content]
```

### 7.3 機能詳細 / Feature Details

#### 7.3.1 システムアクセス / System Access

- オンプレミスシステムからの内部API呼び出し用
- ダウンロード時に `facility_upload_log.download_datetime` を更新
- For internal API calls from on-premise systems
- Updates `facility_upload_log.download_datetime` on download

### 7.4 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常取得 / Successful fetch |
| 400 Bad Request | 無効なファイル種別 / Invalid file type |
| 401 Unauthorized | システムキー認証失敗 / System key authentication failed |
| 404 Not Found | ファイルが見つからない / File not found |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 8. POST /api/v1/files/reports/publish/{medical_id} - 月次レポート公開 / Publish Monthly Reports

### 8.1 リクエスト仕様 / Request Specification

#### 8.1.1 認証要件 / Authentication Requirements

システム認証キーが必須です：
System authentication key required:

```
X-System-Key: {system_api_key}
```

#### 8.1.2 パスパラメータ / Path Parameters

| パラメータ / Parameter | 型 / Type | 必須 / Required | 説明 / Description |
| -------------------- | -------- | ------------- | ------------------- |
| medical_id | int | ✅ | 医療機関ID / Medical facility ID |

#### 8.1.3 フォームデータ / Form Data

| フィールド / Field | 型 / Type | 必須 / Required | 説明 / Description |
| ---------------- | -------- | ------------- | ------------------- |
| publication_ym | string | ✅ | 公開年月（YYYY-MM形式）/ Publication month (YYYY-MM format) |

### 8.2 レスポンス仕様 / Response Specification

#### 8.2.1 成功時レスポンス / Success Response

```json
{
  "success": true,
  "message": "月次レポートの公開が完了しました",
  "medical_id": 22,
  "publication_ym": "2025-08",
  "publication_datetime": "2025-08-25T09:00:00",
  "published_reports": [
    {
      "publication_id": 201,
      "medical_id": 22,
      "publication_ym": "2025-08",
      "file_type": 1,
      "file_name": "analysis_report.pdf",
      "file_size": 2048000,
      "publication_datetime": "2025-08-25T09:00:00",
      "download_datetime": null,
      "download_user_id": null,
      "reg_user_id": "0",
      "regdate": "2025-08-25T09:00:00",
      "update_user_id": "0",
      "lastupdate": "2025-08-25T09:00:00"
    }
  ],
  "notification_sent": true
}
```

### 8.3 機能詳細 / Feature Details

#### 8.3.1 公開処理 / Publication Process

1. オンプレミス生成レポートの取得 / Retrieve on-premise generated reports
2. 公開ディレクトリへのコピー / Copy to publication directory
3. DB公開履歴の記録 / Record publication history in DB
4. 通知メール送信 / Send notification email

### 8.4 HTTPステータスコード / HTTP Status Codes

| ステータス / Status | 説明 / Description |
| ----------------- | ------------------- |
| 200 OK | 正常公開 / Successful publication |
| 400 Bad Request | 年月フォーマットエラー / Month format error |
| 401 Unauthorized | システムキー認証失敗 / System key authentication failed |
| 404 Not Found | レポートが見つからない / Reports not found |
| 500 Internal Server Error | サーバー内部エラー / Internal server error |

---

## 9. データモデル / Data Model

### 9.1 アップロード履歴 / Upload History

#### 9.1.1 facility_upload_log テーブル / facility_upload_log Table

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| uploadlog_id | int | アップロードログID（自動採番）/ Upload log ID (auto-generated) |
| medical_id | int | 医療機関ID / Medical facility ID |
| file_type | int | ファイル種別（1-3）/ File type (1-3) |
| original_filename | string | 元ファイル名 / Original filename |
| file_size | int | ファイルサイズ（バイト）/ File size (bytes) |
| upload_user_id | int | アップロードユーザーID / Upload user ID |
| upload_datetime | datetime | アップロード日時 / Upload datetime |
| download_datetime | datetime | ダウンロード日時 / Download datetime |

### 9.2 レポート公開履歴 / Report Publication History

#### 9.2.1 report_publication_log テーブル / report_publication_log Table

| フィールド / Field | 型 / Type | 説明 / Description |
| ---------------- | -------- | ------------------- |
| publication_id | int | 公開ID（自動採番）/ Publication ID (auto-generated) |
| medical_id | int | 医療機関ID / Medical facility ID |
| publication_ym | string | 公開年月（YYYY-MM）/ Publication month (YYYY-MM) |
| file_type | int | ファイル種別（1-3）/ File type (1-3) |
| file_name | string | ファイル名 / Filename |
| file_size | int | ファイルサイズ（バイト）/ File size (bytes) |
| publication_datetime | datetime | 公開日時 / Publication datetime |
| download_datetime | datetime | ダウンロード日時 / Download datetime |
| download_user_id | str | ダウンロードユーザーID / Download user ID |

---

## 10. 実装詳細 / Implementation Details

### 10.1 ファイルパス管理 / File Path Management

#### 10.1.1 アップロードファイルパス / Upload File Path

```python
def get_upload_file_path(medical_id: int, file_type: int) -> Path:
    """アップロードファイルのパスを生成（医療機関単位・1世代保管）"""
    file_names = {1: "equipment", 2: "rental", 3: "failure"}
    filename = f"{file_names[file_type]}.csv"
    return UPLOADS_PATH / str(medical_id) / filename
```

#### 10.1.2 レポートファイルパス / Report File Path

```python
def get_report_file_path(medical_id: int, publication_ym: str, file_type: int) -> Path:
    """レポートファイルのパスを生成（年/月階層構造）"""
    file_names = {1: "analysis_report", 2: "failure_list", 3: "unachieved_list"}
    file_extensions = {1: ".pdf", 2: ".xlsx", 3: ".xlsx"}
    
    year, month = publication_ym.split("-")
    month_padded = f"{int(month):02d}"
    filename = f"{file_names[file_type]}{file_extensions[file_type]}"
    return REPORTS_PATH / str(medical_id) / year / month_padded / filename
```

### 10.2 システム認証 / System Authentication

```python
def verify_system_key(x_system_key: str = Header(None, alias="X-System-Key")):
    """システム用APIキーの認証"""
    if not x_system_key or x_system_key != SYSTEM_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="System API key is required for this endpoint"
        )
```

### 10.3 通知機能 / Notification Feature

```python
async def send_notification_email(medical_id: int, notification_type: str, target_month: str):
    """通知メール送信（将来実装）"""
    # user_entity_linkからnotification_email_listを取得
    # 実際のメール送信実装は将来予定
```

---

## 11. エラーハンドリング / Error Handling

### 11.1 ファイル形式エラー / File Format Error

```json
{
  "detail": "CSVファイルのみアップロード可能です: equipment_file"
}
```

### 11.2 システム認証エラー / System Authentication Error

```json
{
  "detail": "System API key is required for this endpoint"
}
```

### 11.3 ファイル不存在エラー / File Not Found Error

```json
{
  "detail": "指定されたファイルが存在しません: 医療機関ID=22, ファイル種別=1"
}
```

### 11.4 権限エラー / Permission Error

```json
{
  "detail": "指定された医療機関へのアクセス権限がありません"
}
```

---

## 12. セキュリティ考慮事項 / Security Considerations

### 12.1 アクセス制御 / Access Control

- 医療機関ユーザーは自医療機関のファイルのみアクセス可能
- システムエンドポイントは専用認証キーが必要
- Medical facility users can only access their own facility files
- System endpoints require dedicated authentication keys

### 12.2 ファイルセキュリティ / File Security

- アップロードファイルの拡張子チェック / Upload file extension check
- ファイルサイズ制限（実装予定）/ File size limits (planned)
- ウイルススキャン（実装予定）/ Virus scanning (planned)

### 12.3 監査ログ / Audit Logs

- 全ファイル操作の詳細ログ記録 / Detailed logging of all file operations
- アップロード・ダウンロード履歴の永続化 / Persistent upload/download history
- セキュリティ監査用のアクセス追跡 / Access tracking for security auditing

---

## 13. パフォーマンス考慮事項 / Performance Considerations

### 13.1 ファイルストレージ / File Storage

- ローカルファイルシステム（開発）/ Local filesystem (development)
- AWS S3対応予定（本番）/ AWS S3 support planned (production)
- 大容量ファイル対応 / Large file support

### 13.2 バックアップとリストア / Backup and Restore

- アップロードファイルの定期バックアップ / Regular backup of uploaded files
- レポートファイルの世代管理 / Version management of report files

---

## 14. テスト項目 / Test Cases

### 14.1 正常系テスト / Normal Test Cases

- [ ] 3ファイル同時アップロード
- [ ] アップロード状況取得
- [ ] ダウンロード可能レポート一覧取得
- [ ] レポートダウンロード
- [ ] システム用ファイル取得
- [ ] 月次レポート公開
- [ ] 通知メール送信

### 14.2 異常系テスト / Error Test Cases

- [ ] 無効なファイル形式でのアップロード
- [ ] 権限なしでの他医療機関ファイルアクセス
- [ ] システムキーなしでのシステムAPI呼び出し
- [ ] 存在しないファイルのダウンロード
- [ ] 無効な年月フォーマットでのレポート公開

---

## 15. 今後の拡張予定 / Future Enhancements

### 15.1 機能拡張 / Feature Enhancement

- ファイルプレビュー機能 / File preview functionality
- 一括ダウンロード機能 / Bulk download functionality
- ファイル履歴管理 / File history management
- 自動ファイル処理 / Automated file processing

### 15.2 インフラ拡張 / Infrastructure Enhancement

- AWS S3ストレージ対応 / AWS S3 storage support
- CDNによるファイル配信最適化 / File delivery optimization with CDN
- マルチリージョン対応 / Multi-region support

### 15.3 セキュリティ強化 / Security Enhancement

- ファイル暗号化 / File encryption
- ウイルススキャン / Virus scanning
- API レート制限 / API rate limiting
- ファイル完整性チェック / File integrity checking

---

## 16. 関連資料 / Related Documents

- **プログラム仕様書**: `design/backend/proc/proc_file_management.md`
- **スキーマ定義**: `src/schemas/facility_upload.py`, `src/schemas/report_publication.py`
- **テストケース**: `tests/test_05_file_management_api.py`
- **データベース設計**: `design/database/pg_optigate/facility_upload_log.yaml`, `design/database/pg_optigate/report_publication_log.yaml`
- **認証管理**: `src/utils/auth.py`
- **ファイル管理ユーティリティ**: `src/schemas/file_management.py`