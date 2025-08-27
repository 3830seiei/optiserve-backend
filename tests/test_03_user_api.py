"""test_user_api.py

pytestを使用してユーザーAPIとログインAPIのテストを行います。

実行方法
- startup_optiserve.shを実行してAPIサーバーを起動
- pytest test_user_api.py -v
"""

import pytest
import requests
import random
import string
import os

# 環境に応じたAPI接続先の自動判定
API_HOST = os.environ.get("OPTISERVE_API_HOST", "localhost")
BASE_URL = f"http://{API_HOST}:8000/api/v1"

# テスト用の共通ヘッダー（認証情報）
TEST_HEADERS = {"X-User-Id": "900001"}  # システム管理者のuser_id

def random_email():
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"pytest_{rand}@example.com"

@pytest.fixture(scope="module")
def test_user():
    # 1. ユーザー新規作成
    e_mail = random_email()
    payload = {
        "user_name": "Pytestユーザー",
        "entity_type": 1,
        "entity_relation_id": 1,
        "e_mail": e_mail,
        "mobile_number": "090-1234-5678",
    }
    res = requests.post(f"{BASE_URL}/users", json=payload, headers=TEST_HEADERS)
    assert res.status_code == 200
    user = res.json()
    # パスワードが返るなら取得、返らない場合はテストユーザーで仮パスワードを個別管理
    temp_password = user.get("password", "pytest_dummy_password")
    return {
        "user_id": user["user_id"],
        "e_mail": e_mail,
        "password": temp_password,
        "payload": payload,
    }

def test_login_with_temp_password(test_user):
    # 2. 仮パスワードでログイン
    login_payload = {
        "e_mail": test_user["e_mail"],
        "password": test_user["password"],
    }
    res = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    assert res.status_code == 200
    data = res.json()
    assert data.get("success") is True
    assert "next_action" in data
    assert "user_id" in data

def test_update_user(test_user):
    # 3. ユーザー情報更新
    user_id = test_user["user_id"]
    update_payload = {
        "user_name": "Pytestユーザー更新",
        "phone_number": "03-5678-1234",
        "mobile_number": "090-0000-9999"
    }
    res = requests.put(f"{BASE_URL}/users/{user_id}", json=update_payload, headers=TEST_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["user_name"] == "Pytestユーザー更新"
    assert data["phone_number"] == "03-5678-1234"

def test_get_user(test_user):
    # 4. アカウント取得
    user_id = test_user["user_id"]
    res = requests.get(f"{BASE_URL}/users/{user_id}", headers=TEST_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["user_id"] == user_id
    assert data["user_name"].startswith("Pytestユーザー")

def test_retire_user(test_user):
    # 5. アカウント inactivate（退会）
    user_id = test_user["user_id"]
    user_inactive_payload = {
        "reason_code": 1,
        "note": "テスト退会"
    }
    res = requests.put(f"{BASE_URL}/users/{user_id}/inactive", json=user_inactive_payload, headers=TEST_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["user_status"] == 9

def test_login_suspended_user(test_user):
    # 6. 利用停止ユーザー（user_status=9）でのログイン試行
    login_payload = {
        "e_mail": test_user["e_mail"],
        "password": test_user["password"],
    }
    res = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    assert res.status_code == 200
    data = res.json()
    
    # ログイン失敗であることを確認
    assert data.get("success") is False
    assert data.get("user_id") is None
    assert data.get("entity_type") is None
    assert data.get("entity_relation_id") is None
    assert data.get("user_status") is None
    assert data.get("next_action") == "none"
    assert data.get("message") == "対象のユーザーは利用できません。"
