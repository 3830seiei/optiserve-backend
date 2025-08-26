"""test_facilities_api.py

pytestを使用して医療機関マスタAPIのテストを行います。

実行方法
- startup_optiserve.shを実行してAPIサーバーを起動
- pytest tests/test_facilities_api.py -v
"""

import pytest
import requests
import random
import string

BASE_URL = "http://localhost:8000/api/v1"

# テスト用の共通ヘッダー（認証情報）
TEST_HEADERS = {"X-User-Id": "900001"}  # システム管理者のuser_id

def random_facility_name():
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"pytest病院_{rand}"

def random_phone_number():
    return f"0{random.randint(1, 9)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

@pytest.fixture(scope="module")
def test_facility():
    """テスト用医療機関を新規作成するfixture"""
    facility_name = random_facility_name()
    payload = {
        "medical_name": facility_name,
        "address_postal_code": "100-0001",
        "address_prefecture": "東京都",
        "address_city": "千代田区",
        "address_line1": "テスト町1-1-1",
        "phone_number": random_phone_number(),
    }
    res = requests.post(f"{BASE_URL}/facilities/", json=payload, headers=TEST_HEADERS)
    assert res.status_code == 200
    facility = res.json()
    return {
        "facility_id": facility["medical_id"],
        "facility_name": facility_name,
        "payload": payload,
    }

def test_create_facility():
    """医療機関新規登録テスト"""
    facility_name = random_facility_name()
    payload = {
        "medical_name": facility_name,
        "address_postal_code": "530-0001",
        "address_prefecture": "大阪府",
        "address_city": "大阪市北区",
        "address_line1": "テスト区2-2-2",
        "phone_number": random_phone_number(),
    }
    res = requests.post(f"{BASE_URL}/facilities/", json=payload, headers=TEST_HEADERS)
    print("-"*50)
    print("リクエストペイロード:", payload)
    print("レスポンス:", res.json())  # レスポンスの内容を出力
    assert res.status_code == 200
    data = res.json()
    assert data["medical_name"] == facility_name
    assert data["address_postal_code"] == payload["address_postal_code"]
    assert data["address_prefecture"] == payload["address_prefecture"]
    assert data["address_city"] == payload["address_city"]
    assert data["address_line1"] == payload["address_line1"]
    assert data["phone_number"] == payload["phone_number"]
    assert "medical_id" in data

def test_create_facility_minimum_fields():
    """医療機関新規登録テスト（最小限のフィールドのみ）"""
    facility_name = random_facility_name()
    payload = {
        "medical_name": facility_name,
    }
    res = requests.post(f"{BASE_URL}/facilities/", json=payload, headers=TEST_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["medical_name"] == facility_name
    assert data["address_postal_code"] is None
    assert data["address_prefecture"] is None
    assert data["address_city"] is None
    assert data["address_line1"] is None
    assert data["address_line2"] is None
    assert data["phone_number"] is None
    assert "medical_id" in data

def test_get_facilities():
    """医療機関一覧取得テスト"""
    res = requests.get(f"{BASE_URL}/facilities/", headers=TEST_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if data:  # データが存在する場合
        assert "medical_id" in data[0]
        assert "medical_name" in data[0]

def test_get_facilities_with_pagination():
    """医療機関一覧取得テスト（ページネーション付き）"""
    res = requests.get(f"{BASE_URL}/facilities/?skip=0&limit=5", headers=TEST_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) <= 5

def test_get_facility(test_facility):
    """医療機関個別取得テスト"""
    facility_id = test_facility["facility_id"]
    res = requests.get(f"{BASE_URL}/facilities/{facility_id}", headers=TEST_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["medical_id"] == facility_id
    assert data["medical_name"] == test_facility["facility_name"]

def test_get_facility_not_found():
    """存在しない医療機関の取得でエラーテスト"""
    nonexistent_id = 99999
    res = requests.get(f"{BASE_URL}/facilities/{nonexistent_id}", headers=TEST_HEADERS)
    assert res.status_code == 404
    data = res.json()
    assert "detail" in data
    assert data["detail"] == "Medical facility not found"

def test_update_facility(test_facility):
    """医療機関更新テスト"""
    facility_id = test_facility["facility_id"]
    update_payload = {
        "medical_name": f"{test_facility['facility_name']}_更新",
        "address_postal_code": "231-0001",
        "address_prefecture": "神奈川県",
        "address_city": "横浜市中区",
        "address_line1": "テスト区3-3-3",
        "phone_number": "045-1234-5678"
    }
    res = requests.put(f"{BASE_URL}/facilities/{facility_id}", json=update_payload, headers=TEST_HEADERS)
    print("-"*50)
    print("リクエストペイロード:", update_payload)
    print("レスポンス:", res.json())  # レスポンスの内容を出力
    assert res.status_code == 200
    data = res.json()
    assert data["medical_name"] == update_payload["medical_name"]
    assert data["address_postal_code"] == update_payload["address_postal_code"]
    assert data["address_prefecture"] == update_payload["address_prefecture"]
    assert data["address_city"] == update_payload["address_city"]
    assert data["address_line1"] == update_payload["address_line1"]
    assert data["phone_number"] == update_payload["phone_number"]

def test_update_facility_not_found():
    """存在しない医療機関の更新でエラーテスト"""
    nonexistent_id = 99999
    update_payload = {
        "medical_name": "存在しない病院",
        "address_postal_code": "000-0000",
        "address_prefecture": "テスト県",
        "address_city": "テスト市",
        "address_line1": "テストアドレス",
        "phone_number": "000-0000-0000"
    }
    res = requests.put(f"{BASE_URL}/facilities/{nonexistent_id}", json=update_payload, headers=TEST_HEADERS)
    assert res.status_code == 404
    data = res.json()
    assert "detail" in data
    assert data["detail"] == "Medical facility not found"

# 医療機関マスタの削除機能は提供されないため、削除テストはコメントアウトしています。
# def test_delete_facility():
#     """医療機関削除テスト"""
#     # 削除用の医療機関を新規作成
#     facility_name = random_facility_name()
#     create_payload = {
#         "medical_name": facility_name,
#         "address_postal_code": "123-4567",
#         "address_prefecture": "テスト県",
#         "address_city": "テスト市",
#         "address_line1": "削除テスト用住所",
#         "phone_number": random_phone_number(),
#     }
#     create_res = requests.post(f"{BASE_URL}/facilities/", json=create_payload)
#     assert create_res.status_code == 200
#     facility = create_res.json()
#     facility_id = facility["medical_id"]
#
#     # 削除実行
#     delete_res = requests.delete(f"{BASE_URL}/facilities/{facility_id}")
#     assert delete_res.status_code == 200
#     delete_data = delete_res.json()
#     assert delete_data["result"] == "ok"
#
#     # 削除後の取得確認（404になることを確認）
#     get_res = requests.get(f"{BASE_URL}/facilities/{facility_id}")
#     assert get_res.status_code == 404

# def test_delete_facility_not_found():
#     """存在しない医療機関の削除でエラーテスト"""
#     nonexistent_id = 99999
#     res = requests.delete(f"{BASE_URL}/facilities/{nonexistent_id}")
#     assert res.status_code == 404
#     data = res.json()
#     assert "detail" in data
#     assert data["detail"] == "Medical facility not found"

def test_create_facility_invalid_data():
    """不正なデータでの医療機関作成エラーテスト"""
    # medical_nameが空の場合
    payload = {
        "medical_name": "",
        "address_postal_code": "123-4567",
        "address_prefecture": "テスト県",
    }
    res = requests.post(f"{BASE_URL}/facilities/", json=payload, headers=TEST_HEADERS)
    assert res.status_code == 422  # バリデーションエラー

    # medical_nameが未指定の場合
    payload = {
        "address_postal_code": "123-4567",
        "address_prefecture": "テスト県",
    }
    res = requests.post(f"{BASE_URL}/facilities/", json=payload, headers=TEST_HEADERS)
    assert res.status_code == 422  # バリデーションエラー
