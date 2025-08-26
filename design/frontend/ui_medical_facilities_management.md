# 画面仕様書 / Screen Specification

- Revision

    | Rev | Date       | Auth       | Note    |
    |----:|------------|------------|---------|
    | 1.0 | 2025.08.25 | Claude     | 新規作成 |

## 1. 画面名称 / Screen Title

- 日本語: 医療機関マスタ管理画面
- English: Medical Facilities Management Screen

### 1-1. 機能ID / Functional Identifier

- 機能ID（日本語）: 医療機関マスタ管理
- Functional Name (English): medical-facilities-management
- 使用例（SPAルーティング）: `/medical-facilities` または `/admin/facilities`

## 2. 機能概要 / Function Overview

[Japanese]

医療機関マスタ情報の管理機能を提供する画面です。医療機関の一覧表示、個別詳細表示、新規登録、情報更新の機能を含みます。権限に基づくアクセス制御により、システム管理者は全機能、医療機関ユーザーは自医療機関の情報閲覧のみ可能です。

**主な機能**:
- 医療機関情報のCRUD操作（新規登録・参照・更新、削除機能は意図的に未提供）
- 権限別アクセス制御（管理者：全医療機関、一般ユーザー：自医療機関のみ）
- ページネーション対応の一覧表示
- 医療機関情報の検索・フィルタリング
- 住所情報の詳細管理（郵便番号、都道府県、市区町村、住所1・2）

**注意事項**: データの整合性とトレーサビリティを保つため、削除機能は意図的に提供されていません。

[English]

This screen provides medical facility master information management functionality. It includes features for medical facility list display, individual detail display, new registration, and information updates. Role-based access control allows system administrators full functionality, while medical facility users can only view their own facility information.

**Main Features**:
- CRUD operations for medical facility information (create, read, update - delete functionality intentionally not provided)
- Permission-based access control (administrators: all facilities, general users: own facility only)
- List display with pagination support
- Search and filtering of medical facility information
- Detailed address information management (postal code, prefecture, city, address lines 1 & 2)

**Important Note**: Delete functionality is intentionally not provided to maintain data integrity and traceability.

## 3. 画面利用対象ユーザー / Target Users

- システム管理者 (user_id: "900001"-"999999"): 全医療機関情報へのアクセス・管理・新規登録・更新可能
- 医療機関ユーザー (entity_type=1): 自医療機関の情報閲覧のみ可能（更新機能は管理者のみ）

## 4. 運用概要 / Operational Usage

[Japanese]

医療機関マスタは、OptiServeシステムの基盤となる重要な情報です。正確性と一貫性を保つため、管理者権限でのみ編集が可能となっています。

**本番運用の流れ**:
1. **DataHub連携**: 厚生労働省提供の医療機関情報をオンプレ側DBに保管
2. **医療機関登録**: SMDS登録時は厚生労働省の情報を利用して新規登録
   - 現在は厚生労働省の情報テーブルが無いため画面から手作業入力
   - 将来的にはオンプレ側の情報を利用した更新システムを検討
3. **個別情報管理**: 厚生労働省データにない情報はuser_entity_link側で管理

**典型的な運用シナリオ**:
- **新規医療機関登録**: 契約時にシステム管理者が基本情報を登録
- **情報更新**: 住所変更、電話番号変更等の基本情報メンテナンス
- **情報確認**: 医療機関ユーザーが自施設の登録情報を確認

[English]

Medical facility master data is critical information that forms the foundation of the OptiServe system. To maintain accuracy and consistency, editing is only possible with administrator privileges.

**Production Operation Flow**:
1. **DataHub Integration**: Store medical facility information provided by the Ministry of Health, Labour and Welfare in on-premises DB
2. **Medical Facility Registration**: Use Ministry information for new registration during SMDS registration
   - Currently manual input via screen as Ministry information table doesn't exist
   - Future consideration for update system using on-premises information
3. **Individual Information Management**: Information not in Ministry data is managed via user_entity_link

**Typical Operational Scenarios**:
- **New Medical Facility Registration**: System administrators register basic information at contract time
- **Information Updates**: Maintenance of basic information such as address changes, phone number changes
- **Information Verification**: Medical facility users verify their facility's registration information

## 5. 処理の流れ / Processing Flow

[Japanese]

1. **医療機関一覧取得**
   - `GET /api/v1/facilities` でデータ取得
   - 認証ヘッダー `X-User-Id` が必須
   - skip/limitによるページング（デフォルト100件、最大100件）
   - システム管理者: 全医療機関、医療機関ユーザー: 自医療機関のみ表示
   - 医療機関名での部分一致検索が可能

2. **医療機関詳細表示**
   - 一覧から行を選択して詳細情報を表示
   - `GET /api/v1/facilities/{facility_id}` で個別取得
   - 権限に応じたアクセス制御を実施

3. **新規医療機関登録**（管理者のみ）
   - **新規登録**ボタンクリックで登録フォーム表示
   - 必須項目: medical_name（医療機関名）のみ
   - その他項目（住所、電話番号等）は任意入力
   - `POST /api/v1/facilities` で登録処理
   - medical_idは自動採番される

4. **医療機関情報更新**（管理者のみ）
   - 詳細表示から**編集**ボタンクリックで編集モード
   - 全項目編集可能（medical_idは読み取り専用）
   - `PUT /api/v1/facilities/{facility_id}` で更新処理
   - 更新後は詳細表示モードに戻る

5. **検索・フィルタリング**
   - 医療機関名での部分一致検索
   - 都道府県でのフィルタリング
   - 電話番号での検索
   - 検索条件はリアルタイムでAPI呼び出し

[English]

1. **Retrieve Medical Facility List**
   - Retrieve data via `GET /api/v1/facilities`
   - Authentication header `X-User-Id` is required
   - Pagination with skip/limit (default 100 records, max 100)
   - System administrators: all facilities, Medical facility users: own facility only
   - Partial match search by medical facility name is available

2. **Medical Facility Detail Display**
   - Select row from list to display detailed information
   - Retrieve individually via `GET /api/v1/facilities/{facility_id}`
   - Apply access control according to permissions

3. **New Medical Facility Registration** (Administrators only)
   - Click **New Registration** button to display registration form
   - Required field: medical_name (medical facility name) only
   - Other fields (address, phone number, etc.) are optional
   - Register via `POST /api/v1/facilities`
   - medical_id is automatically assigned

4. **Medical Facility Information Update** (Administrators only)
   - Click **Edit** button from detail display to enter edit mode
   - All fields editable (medical_id is read-only)
   - Update via `PUT /api/v1/facilities/{facility_id}`
   - Return to detail display mode after update

5. **Search and Filtering**
   - Partial match search by medical facility name
   - Filtering by prefecture
   - Search by phone number
   - Search conditions trigger real-time API calls

## 6. 入出力仕様 / Input/Output Specifications

### 6.1 一覧表示項目 / List Display Fields

| 項目名 | フィールド名 | 表示内容 | ソート可否 |
|--------|--------------|----------|------------|
| 医療機関ID | medical_id | 数値表示 | ○ |
| 医療機関名 | medical_name | 文字列表示 | ○ |
| 郵便番号 | address_postal_code | XXX-XXXX形式 | ○ |
| 都道府県 | address_prefecture | 文字列表示 | ○ |
| 市区町村 | address_city | 文字列表示 | ○ |
| 電話番号 | phone_number | XXX-XXXX-XXXX形式 | ○ |
| 最終更新日時 | lastupdate | YYYY-MM-DD HH:mm形式 | ○ |

### 6.2 詳細表示・編集フォーム項目 / Detail Display and Edit Form Fields

| 項目名 | フィールド名 | 入力形式 | バリデーション | 必須 |
|--------|--------------|----------|----------------|------|
| 医療機関ID | medical_id | 表示のみ | - | - |
| 医療機関名 | medical_name | テキスト入力 | 最大255文字 | ✅ |
| 郵便番号 | address_postal_code | テキスト入力 | XXX-XXXX形式 | - |
| 都道府県 | address_prefecture | テキスト入力 | 最大20文字 | - |
| 市区町村 | address_city | テキスト入力 | 最大50文字 | - |
| 住所1 | address_line1 | テキスト入力 | 最大100文字 | - |
| 住所2 | address_line2 | テキスト入力 | 最大100文字 | - |
| 電話番号 | phone_number | テキスト入力 | 電話番号形式 | - |

### 6.3 検索・フィルタ項目 / Search and Filter Fields

| 項目名 | フィールド名 | 入力形式 | 説明 |
|--------|--------------|----------|------|
| 医療機関名検索 | medical_name | テキスト入力 | 部分一致検索 |
| 都道府県フィルタ | address_prefecture | セレクトボックス | 完全一致フィルタ |
| 電話番号検索 | phone_number | テキスト入力 | 部分一致検索 |

### 6.4 システム情報項目 / System Information Fields

| 項目名 | フィールド名 | 表示内容 | 表示場所 |
|--------|--------------|----------|----------|
| 登録ユーザーID | reg_user_id | 文字列表示 | 詳細表示のみ |
| 登録日時 | regdate | YYYY-MM-DD HH:mm:ss | 詳細表示のみ |
| 更新ユーザーID | update_user_id | 文字列表示 | 詳細表示のみ |
| 最終更新日時 | lastupdate | YYYY-MM-DD HH:mm:ss | 詳細表示のみ |

## 7. バリデーション仕様 / Validation Rules

[Japanese]

### 7.1 必須項目
- 医療機関名（medical_name）は必須入力

### 7.2 文字数制限
- 医療機関名: 最大255文字
- 都道府県: 最大20文字
- 市区町村: 最大50文字
- 住所1、住所2: 最大100文字

### 7.3 形式チェック
- 郵便番号: XXX-XXXX形式（例: 100-0001）
- 電話番号: 適切な電話番号形式（ハイフンあり・なし両対応）

### 7.4 重複チェック
- 同一医療機関名での重複登録チェック（警告表示）

### 7.5 権限チェック
- 新規登録・更新はシステム管理者のみ
- 医療機関ユーザーは自医療機関の閲覧のみ

[English]

### 7.1 Required Fields
- Medical facility name (medical_name) is required input

### 7.2 Character Limits
- Medical facility name: Maximum 255 characters
- Prefecture: Maximum 20 characters
- City: Maximum 50 characters
- Address line 1, 2: Maximum 100 characters

### 7.3 Format Validation
- Postal code: XXX-XXXX format (e.g., 100-0001)
- Phone number: Appropriate phone number format (with or without hyphens)

### 7.4 Duplicate Check
- Duplicate registration check for same medical facility name (warning display)

### 7.5 Permission Check
- New registration and updates only for system administrators
- Medical facility users can only view their own facility

## 8. API連携仕様 / API Integration

### 8.1 `GET /api/v1/facilities`

**認証**: `X-User-Id` ヘッダー必須
**権限**: システム管理者（全データ）、医療機関ユーザー（自医療機関のみ）
**パラメータ**:
- skip: スキップ件数（デフォルト: 0）
- limit: 取得件数（デフォルト: 100、最大: 100）

**レスポンス例**:
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

### 8.2 `GET /api/v1/facilities/{facility_id}`

**認証**: `X-User-Id` ヘッダー必須
**権限**: システム管理者（全データ）、医療機関ユーザー（自医療機関のみ）

### 8.3 `POST /api/v1/facilities` （管理者のみ）

**認証**: `X-User-Id` ヘッダー必須
**権限**: システム管理者権限が必要
**リクエストボディ**:
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

### 8.4 `PUT /api/v1/facilities/{facility_id}` （管理者のみ）

**認証**: `X-User-Id` ヘッダー必須
**権限**: システム管理者権限が必要
**リクエストボディ**: POST時と同じ形式

## 9. 画面遷移 / Screen Navigation

| 操作 | 説明 | 遷移先 |
|------|------|--------|
| 前へ | 前ページ表示 | 同画面（ページング） |
| 次へ | 次ページ表示 | 同画面（ページング） |
| 詳細表示 | 一覧行選択で詳細表示 | 同画面（詳細モード） |
| 新規登録 | 新規登録フォーム表示 | 同画面（新規登録モード） |
| 編集 | 詳細から編集モードへ | 同画面（編集モード） |
| 保存 | 登録・更新の保存 | 同画面（詳細表示または一覧） |
| キャンセル | 編集のキャンセル | 同画面（詳細表示または一覧） |
| 戻る | 詳細から一覧へ | 同画面（一覧表示） |

### 9.1 画面レイアウト構成 / Screen Layout Configuration

#### 9.1.1 医療機関マスタ管理画面全体表示

![医療機関マスタメンテナンス画面](assets/mock_facilities_management.png)

画面は以下の主要エリアで構成されています：

- **ヘッダー部**: 画面タイトル「医療機関マスタ メンテナンス」
- **検索条件部**: 医療機関名・都道府県・市区町村による絞り込み機能
- **医療機関一覧部**: 医療機関の一覧表示とページング機能
- **医療機関情報部**: 選択された医療機関の詳細情報表示・編集エリア（右側パネル）

#### 9.1.2 主要な画面構成要素

**検索条件エリア:**
- 医療機関名: 部分一致検索用テキストフィールド
- 都道府県: セレクトボックスによる都道府県フィルタ
- 市区町村: セレクトボックスによる市区町村フィルタ
- 検索ボタン: フィルタ条件を適用

**医療機関一覧エリア:**
- 各行には医療機関ID・医療機関名・都道府県・市区町村・更新日時が表示
- ページング: ページ番号と件数表示（例：1ページ、36件）
- 選択機能: ラジオボタンによる単一行選択

**詳細情報エリア（右側パネル）:**
- 医療機関ID: 読み取り専用の識別子
- 医療機関名: 必須項目（※必須項目マーク付き）
- 郵便番号: ハイフン付き郵便番号フォーマット
- 都道府県・市区町村: 住所情報
- 住所詳細: 建物名などの補足住所情報
- 電話番号・FAX番号・Email: 連絡先情報
- ホームページURL: Web サイト情報
- 備考: その他の情報用テキストエリア
- 操作ボタン: 「新規登録」「更新」ボタン（管理者権限のみ）

#### 9.1.3 主要な操作フロー

1. **医療機関検索**: 上部の検索条件フィールドで医療機関を絞り込み
2. **医療機関選択**: 一覧から医療機関をクリック選択（ラジオボタン）
3. **詳細情報表示**: 選択した医療機関の詳細が右側パネルに表示
4. **情報編集**: 管理者権限の場合、詳細情報の編集が可能
5. **新規登録**: 「新規登録」ボタンで新しい医療機関を登録（管理者のみ）
6. **情報更新**: 「更新」ボタンで変更内容を保存（管理者のみ）

## 10. PoC制約事項 / Limitations for PoC Version

[Japanese]

- 医療機関検索機能は基本的な部分一致検索のみ
- 住所の自動入力機能（郵便番号からの住所検索等）は未実装
- 医療機関カテゴリ分類機能は未実装
- 一括登録・更新機能は未実装
- エクスポート/インポート機能は未実装
- 地図表示機能は未実装

[English]

- Medical facility search functionality is basic partial match search only
- Automatic address input functionality (address search from postal code, etc.) is not implemented
- Medical facility category classification functionality is not implemented
- Bulk registration and update functionality is not implemented
- Export/import functionality is not implemented
- Map display functionality is not implemented

## 11. フロントエンド開発者向け補足 / Notes for Frontend Developer

この画面は、Next.js等のフロントエンドSPAがFastAPIバックエンドとREST APIで接続する構成を想定しています。

### 🔌 接続情報 / Connection Details

| 項目 | 内容 |
|------|------|
| 接続先API | `http://192.168.99.118:8000`（PoC用）<br>※将来的にAWS上での実装を予定 |
| 通信方式 | REST（`fetch` や `axios` など） |
| データ形式 | JSON（リクエスト/レスポンス共通） |
| 認証 | `X-User-Id` ヘッダーによる認証が必要 |
| CORS | `Access-Control-Allow-Origin: *` を許可済（開発用途） |

### 📦 APIレスポンス構造例

```json
// 医療機関一覧取得レスポンス
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

// 医療機関詳細取得レスポンス（同じ構造）
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

### 🛠 axiosを使ったアクセス例

```typescript
import axios from 'axios';

const apiBase = 'http://192.168.99.118:8000/api/v1/facilities';

// 医療機関一覧取得
export const fetchFacilities = async (
  skip = 0,
  limit = 100,
  currentUserId: string
) => {
  const res = await axios.get(`${apiBase}?skip=${skip}&limit=${limit}`, {
    headers: {
      'X-User-Id': currentUserId
    }
  });
  return res.data;
};

// 医療機関詳細取得
export const fetchFacility = async (
  facilityId: number,
  currentUserId: string
) => {
  const res = await axios.get(`${apiBase}/${facilityId}`, {
    headers: {
      'X-User-Id': currentUserId
    }
  });
  return res.data;
};

// 医療機関新規登録（管理者のみ）
export const createFacility = async (
  facilityData: Omit<MedicalFacility, 'medical_id' | 'reg_user_id' | 'regdate' | 'update_user_id' | 'lastupdate'>,
  currentUserId: string
) => {
  const res = await axios.post(
    apiBase,
    facilityData,
    {
      headers: {
        'X-User-Id': currentUserId,
        'Content-Type': 'application/json'
      }
    }
  );
  return res.data;
};

// 医療機関情報更新（管理者のみ）
export const updateFacility = async (
  facilityId: number,
  facilityData: Omit<MedicalFacility, 'medical_id' | 'reg_user_id' | 'regdate' | 'update_user_id' | 'lastupdate'>,
  currentUserId: string
) => {
  const res = await axios.put(
    `${apiBase}/${facilityId}`,
    facilityData,
    {
      headers: {
        'X-User-Id': currentUserId,
        'Content-Type': 'application/json'
      }
    }
  );
  return res.data;
};
```

### 💡 UI実装のヒント

#### 権限による機能制御
```typescript
interface UserPermissions {
  isAdmin: boolean;
  canEdit: boolean;
  canCreate: boolean;
  viewableFacilities: number[]; // 閲覧可能な医療機関IDリスト
}

// 管理者権限の判定
const isSystemAdmin = (userId: string): boolean => {
  return userId >= "900001" && userId <= "999999";
};

// 権限に基づくUIの表示制御
const FacilityManagementPage = ({ currentUser }) => {
  const permissions = {
    isAdmin: isSystemAdmin(currentUser.user_id),
    canEdit: isSystemAdmin(currentUser.user_id),
    canCreate: isSystemAdmin(currentUser.user_id),
    viewableFacilities: isSystemAdmin(currentUser.user_id) 
      ? [] // 管理者は全施設閲覧可能 
      : [currentUser.medical_id] // 一般ユーザーは自医療機関のみ
  };

  return (
    <div>
      {permissions.canCreate && (
        <button onClick={handleNewRegistration}>新規登録</button>
      )}
      {/* 他のコンポーネント */}
    </div>
  );
};
```

#### 入力フォームのバリデーション
```typescript
interface FacilityFormData {
  medical_name: string;
  address_postal_code?: string;
  address_prefecture?: string;
  address_city?: string;
  address_line1?: string;
  address_line2?: string;
  phone_number?: string;
}

// バリデーション関数
const validateFacilityForm = (data: FacilityFormData): Record<string, string> => {
  const errors: Record<string, string> = {};
  
  if (!data.medical_name || data.medical_name.trim().length === 0) {
    errors.medical_name = "医療機関名は必須です。";
  } else if (data.medical_name.length > 255) {
    errors.medical_name = "医療機関名は255文字以内で入力してください。";
  }
  
  if (data.address_postal_code && !/^\d{3}-\d{4}$/.test(data.address_postal_code)) {
    errors.address_postal_code = "郵便番号はXXX-XXXX形式で入力してください。";
  }
  
  if (data.address_prefecture && data.address_prefecture.length > 20) {
    errors.address_prefecture = "都道府県は20文字以内で入力してください。";
  }
  
  // 電話番号の基本的な形式チェック
  if (data.phone_number && !/^[\d-]+$/.test(data.phone_number)) {
    errors.phone_number = "電話番号は数字とハイフンのみで入力してください。";
  }
  
  return errors;
};
```

#### 検索・フィルタリング機能
```typescript
const [searchFilters, setSearchFilters] = useState({
  medical_name: '',
  address_prefecture: '',
  phone_number: ''
});

// 検索実行（デバウンス付き）
const debouncedSearch = useCallback(
  debounce((filters) => {
    fetchFacilitiesWithFilters(filters);
  }, 500),
  []
);

// フィルタ変更時の処理
const handleFilterChange = (key: keyof typeof searchFilters, value: string) => {
  const newFilters = { ...searchFilters, [key]: value };
  setSearchFilters(newFilters);
  debouncedSearch(newFilters);
};

// APIパラメータに検索条件を追加
const fetchFacilitiesWithFilters = async (filters: typeof searchFilters) => {
  const params = new URLSearchParams({
    skip: '0',
    limit: '100'
  });
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value.trim()) {
      params.append(key, value);
    }
  });
  
  // API呼び出し
  const response = await fetchFacilities(0, 100, currentUserId, params.toString());
  setFacilities(response);
};
```

#### モーダル・フォーム状態管理
```typescript
type ModalMode = 'none' | 'detail' | 'edit' | 'create';

const [modalState, setModalState] = useState({
  mode: 'none' as ModalMode,
  selectedFacility: null as MedicalFacility | null,
  formData: {} as Partial<FacilityFormData>
});

// 新規登録モード
const handleNewRegistration = () => {
  setModalState({
    mode: 'create',
    selectedFacility: null,
    formData: {}
  });
};

// 詳細表示モード
const handleShowDetail = (facility: MedicalFacility) => {
  setModalState({
    mode: 'detail',
    selectedFacility: facility,
    formData: facility
  });
};

// 編集モード
const handleEdit = () => {
  if (modalState.selectedFacility) {
    setModalState({
      ...modalState,
      mode: 'edit',
      formData: { ...modalState.selectedFacility }
    });
  }
};
```

### 🧪 curlでの簡易テスト例

```bash
# 医療機関一覧取得
curl -X GET "http://192.168.99.118:8000/api/v1/facilities" \
  -H "X-User-Id: 900001"

# 医療機関詳細取得
curl -X GET "http://192.168.99.118:8000/api/v1/facilities/22" \
  -H "X-User-Id: 900001"

# 医療機関新規登録（管理者のみ）
curl -X POST "http://192.168.99.118:8000/api/v1/facilities" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 900001" \
  -d '{
    "medical_name": "新規医療機関",
    "address_postal_code": "100-0002",
    "address_prefecture": "東京都",
    "address_city": "千代田区",
    "address_line1": "千代田2-2-2",
    "address_line2": "○○タワー10F",
    "phone_number": "03-9999-9999"
  }'

# 医療機関情報更新（管理者のみ）
curl -X PUT "http://192.168.99.118:8000/api/v1/facilities/23" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 900001" \
  -d '{
    "medical_name": "更新された医療機関名",
    "address_postal_code": "100-0003",
    "address_prefecture": "東京都",
    "address_city": "千代田区",
    "address_line1": "千代田3-3-3",
    "address_line2": "更新ビル5F",
    "phone_number": "03-8888-8888"
  }'
```

## 12. 処理メッセージ仕様 / Operation Messages

### 12.1 成功メッセージ / Success Messages

| タイミング | ステータス | 表示メッセージ | 備考 |
|------------|------------|----------------|------|
| 新規登録成功 | 200 OK | 医療機関を登録しました。 | POST /facilities |
| 更新成功 | 200 OK | 医療機関情報を更新しました。 | PUT /facilities/{id} |
| 詳細取得成功 | 200 OK | - | 無音で詳細表示 |
| 検索完了 | 200 OK | {件数}件の医療機関が見つかりました。 | 検索結果表示時 |

### 12.2 エラーメッセージ / Error Messages

| タイミング | ステータス | 表示メッセージ | 備考 |
|------------|------------|----------------|------|
| 権限エラー | 403 | 管理者権限が必要です。 | 新規登録・更新時 |
| アクセス権限エラー | 403 | 指定された医療機関へのアクセス権限がありません。 | 他医療機関データアクセス時 |
| 医療機関不存在 | 404 | 医療機関が見つかりません。 | facility_id不正 |
| バリデーションエラー | 422 | 入力内容に不備があります。 | 必須項目未入力など |
| 重複名称警告 | 400 | 同名の医療機関が既に存在します。登録を続行しますか？ | 重複チェック時 |
| サーバーエラー | 500 | サーバーでエラーが発生しました。後で再度お試しください。 | システム障害 |

### 12.3 フィールド別バリデーションメッセージ

| フィールド | エラーメッセージ |
|------------|------------------|
| medical_name | 医療機関名は必須です。 |
| medical_name | 医療機関名は255文字以内で入力してください。 |
| address_postal_code | 郵便番号はXXX-XXXX形式で入力してください。 |
| address_prefecture | 都道府県は20文字以内で入力してください。 |
| address_city | 市区町村は50文字以内で入力してください。 |
| address_line1 | 住所1は100文字以内で入力してください。 |
| address_line2 | 住所2は100文字以内で入力してください。 |
| phone_number | 適切な電話番号形式で入力してください。 |

### 12.4 確認メッセージ / Confirmation Messages

| タイミング | 表示メッセージ | 説明 |
|------------|----------------|------|
| 新規登録確認 | この内容で医療機関を登録しますか？ | 新規登録前の最終確認 |
| 更新確認 | この内容で医療機関情報を更新しますか？ | 更新前の最終確認 |
| 編集キャンセル確認 | 編集中の内容を破棄して戻りますか？ | 未保存変更がある場合 |

### 12.5 情報メッセージ / Information Messages

| タイミング | 表示メッセージ | 説明 |
|------------|----------------|------|
| 検索結果なし | 検索条件に該当する医療機関がありません。 | 検索結果0件時 |
| 読み取り専用表示 | この医療機関の情報は閲覧のみ可能です。 | 一般ユーザーでの表示時 |
| データ読み込み中 | 医療機関情報を読み込んでいます... | ローディング表示 |
| 保存中 | 保存しています... | 保存処理中 |

### 12.6 表示方法の推奨

[Japanese]
- 成功メッセージは画面右上のトースト通知で3秒間表示
- エラーメッセージは該当フィールドの下部に赤字で表示
- 確認メッセージはモーダルダイアログで表示し、ユーザーの応答を待つ
- 情報メッセージは画面上部に青色背景で表示
- 重要な権限エラーはページ中央にアラートボックスで表示

[English]
- Success messages should be displayed as toast notifications in the upper right corner for 3 seconds
- Error messages should be displayed in red text below the corresponding field
- Confirmation messages should be displayed in modal dialogs waiting for user response
- Information messages should be displayed with blue background at the top of the screen
- Important permission errors should be displayed in alert boxes at the center of the page