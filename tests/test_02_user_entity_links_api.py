"""test_user_entity_links_api.py

pytestを使用してユーザー組織連携APIのテストを行います。

実行方法
- startup_optiserve.shを実行してAPIサーバーを起動
- pytest tests/test_user_entity_links_api.py -v

前提条件:
- entity_relation_id=6でテスト用医療機関が登録済みであること
- テスト実行前に自動でクリーンアップが実行されます
"""

import pytest
import requests
import random
import string
import json
import sys
import os

# プロジェクトルートをsys.pathに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# 環境に応じたAPI接続先の自動判定
API_HOST = os.environ.get("OPTISERVE_API_HOST", "localhost")
BASE_URL = f"http://{API_HOST}:8000/api/v1"

# テスト用の共通ヘッダー（認証情報）
TEST_HEADERS = {"X-User-Id": "900001"}  # システム管理者のuser_id

def cleanup_test_links():
    """テスト実行前のクリーンアップ - entity_relation_id=6の連携データを削除"""
    try:
        print("🔍 クリーンアップ開始: entity_relation_id=6のデータをチェック中...")
        # 既存の連携データを取得
        res = requests.get(f"{BASE_URL}/user-entity-links/", headers=TEST_HEADERS)
        print(f"API レスポンス: status_code={res.status_code}")

        if res.status_code == 200:
            links = res.json()
            print(f"取得した連携データ数: {len(links)}")
            deleted_count = 0
            for link in links:
                print(f"チェック中: entity_relation_id={link.get('entity_relation_id')}")
                if link.get("entity_relation_id") == 6:
                    print(f"削除対象発見: entity_type={link.get('entity_type')}, entity_relation_id={link.get('entity_relation_id')}")
                    # 直接DB操作で削除（API削除エンドポイントが無いため）
                    from src.database import SessionLocal
                    from src.models.pg_optigate.user_entity_link import UserEntityLink

                    db = SessionLocal()
                    try:
                        # 複合主キーで検索
                        db_link = db.query(UserEntityLink).filter(
                            UserEntityLink.entity_type == link["entity_type"],
                            UserEntityLink.entity_relation_id == link["entity_relation_id"]
                        ).first()
                        if db_link:
                            db.delete(db_link)
                            db.commit()
                            deleted_count += 1
                    except Exception as e:
                        print(f"削除エラー (entry_type: {link['entity_type']} entity_relation_id: {link['entity_relation_id']}): {e}")
                        db.rollback()
                    finally:
                        db.close()
            if deleted_count > 0:
                print(f"🧹 テスト前クリーンアップ: {deleted_count}件の古い連携データを削除しました")
            else:
                print("✨ クリーンアップ対象なし: entity_relation_id=6のデータは存在しません")
        else:
            print(f"⚠️ API取得失敗: status_code={res.status_code}, response={res.text[:200]}")
            print("クリーンアップをスキップしてテストを続行します")
    except Exception as e:
        print(f"クリーンアップ処理でエラーが発生しましたが、テストを続行します: {e}")
        import traceback
        print(f"詳細エラー: {traceback.format_exc()}")

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """テスト環境のセットアップ - 全テスト実行前に一度だけ実行"""
    print("\n🚀 テスト環境セットアップ開始...")
    cleanup_test_links()
    print("✅ テスト環境セットアップ完了\n")

def random_string(length=6):
    """ランダムな文字列生成"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def random_entity_name():
    """ランダムな組織名生成"""
    rand = random_string()
    return f"pytest連携組織_{rand}"

def random_email_list():
    """シンプルなメールアドレス文字列生成（SQLite対応）"""
    return f"pytest_{random_string()}@example.com"

def find_available_entity_relation_id():
    """医療機関マスタに存在し、かつ未使用のentity_relation_idを見つける"""
    import random
    
    try:
        # 医療機関マスタから利用可能なIDを取得
        facilities_res = requests.get(f"{BASE_URL}/facilities/", headers=TEST_HEADERS)
        if facilities_res.status_code != 200:
            return 7  # フォールバック
        
        available_ids = {facility["medical_id"] for facility in facilities_res.json()}
        
        # 既存の連携データから使用中のIDを取得
        links_res = requests.get(f"{BASE_URL}/user-entity-links/", headers=TEST_HEADERS)
        if links_res.status_code == 200:
            used_ids = {link["entity_relation_id"] for link in links_res.json()}
        else:
            used_ids = set()
        
        # 医療機関マスタに存在し、かつ未使用のIDを探す
        unused_ids = available_ids - used_ids
        if unused_ids:
            # ランダムに選択して競合を避ける
            return random.choice(list(unused_ids))
        
        # 全て使用済みの場合は新しい医療機関を作成
        print("Warning: 全IDが使用済み。新しい医療機関を作成します")
        return create_test_medical_facility()
        
    except Exception as e:
        print(f"Warning: {e}, フォールバックIDを使用: 7")
        return 7  # 医療機関マスタに存在するIDをフォールバック


def create_test_medical_facility():
    """テスト用医療機関を新規作成し、そのIDを返す"""
    import random
    import string
    
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    facility_name = f"pytest用テスト病院_{rand}"
    
    payload = {
        "medical_name": facility_name,
        "address_postal_code": "123-4567",
        "address_prefecture": "テスト県",
        "address_city": "テスト市",
        "address_line1": f"テスト町{random.randint(1,999)}-{random.randint(1,99)}-{random.randint(1,99)}",
        "phone_number": f"0{random.randint(1,9)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/facilities/", json=payload, headers=TEST_HEADERS)
        if res.status_code == 200:
            facility = res.json()
            medical_id = facility["medical_id"]
            print(f"新しいテスト用医療機関を作成: {facility_name} (ID: {medical_id})")
            return medical_id
        else:
            print(f"医療機関作成失敗: {res.status_code}, {res.text}")
            return 999  # 最終フォールバック
    except Exception as e:
        print(f"医療機関作成エラー: {e}")
        return 999  # 最終フォールバック

@pytest.fixture(scope="function")
def test_link():
    """テスト用ユーザー組織連携情報を新規作成するfixture"""
    entity_name = random_entity_name()
    entity_relation_id = find_available_entity_relation_id()
    payload = {
        "entity_type": 1,  # 医療機関
        "entity_relation_id": entity_relation_id,  # 未使用のテスト用医療機関ID
        "entity_name": entity_name,
        "notification_email_list": random_email_list(),
        "count_reportout_classification": 5,  # 運用レベル基準
        "analiris_classification_level": 2  # 中分類
    }
    res = requests.post(f"{BASE_URL}/user-entity-links/", json=payload, headers=TEST_HEADERS)
    assert res.status_code == 200, f"フィクスチャ作成失敗: status={res.status_code}, response={res.text}"
    link = res.json()
    return {
        "entity_type": link["entity_type"],
        "entity_relation_id": link["entity_relation_id"],
        "entity_name": entity_name,
        "payload": payload,
    }

def test_create_user_entity_link():
    """ユーザー組織連携情報新規登録テスト"""
    entity_name = random_entity_name()
    payload = {
        "entity_type": 1,
        "entity_relation_id": 6,  # テスト用医療機関ID（例: 6）
        "entity_name": entity_name,
        "notification_email_list": random_email_list(),
        "count_reportout_classification": 5,
        "analiris_classification_level": 1  # 大分類
    }
    res = requests.post(f"{BASE_URL}/user-entity-links/", json=payload, headers=TEST_HEADERS)
    assert res.status_code == 200
    link = res.json()

    # レスポンス検証
    assert link["entity_type"] == 1
    assert link["entity_relation_id"] == 6
    assert link["entity_name"] == entity_name
    assert link["count_reportout_classification"] == 5
    assert link["analiris_classification_level"] == 1
    # 複合主キーのため、個別のidフィールドはなし
    assert link["entity_type"] == 1 and link["entity_relation_id"] == 6
    print(f"✅ ユーザー組織連携情報作成成功: entity_type={link['entity_type']}, entity_relation_id={link['entity_relation_id']}, 組織名={entity_name}")

def test_create_invalid_entity_type():
    """無効な組織種別でのエラーテスト"""
    payload = {
        "entity_type": 2,  # ディーラー（未サポート）
        "entity_relation_id": 6,
        "entity_name": "テスト組織",
        "notification_email_list": random_email_list(),
        "count_reportout_classification": 5,
        "analiris_classification_level": 1
    }
    res = requests.post(f"{BASE_URL}/user-entity-links/", json=payload, headers=TEST_HEADERS)
    assert res.status_code == 400
    error = res.json()
    assert "組織種別（entity_type）は1のみサポート" in error["detail"]
    print(f"✅ 無効な組織種別エラー: {error['detail']}")

def test_create_invalid_entity_relation_id():
    """存在しない医療機関IDでのエラーテスト"""
    payload = {
        "entity_type": 1,
        "entity_relation_id": 99999,  # 存在しない医療機関ID
        "entity_name": "テスト組織",
        "notification_email_list": random_email_list(),
        "count_reportout_classification": 5,
        "analiris_classification_level": 1
    }
    res = requests.post(f"{BASE_URL}/user-entity-links/", json=payload, headers=TEST_HEADERS)
    assert res.status_code == 400
    error = res.json()
    assert "医療機関ID（entity_relation_id）" in error["detail"]
    assert "は存在しません" in error["detail"]
    print(f"✅ 存在しない医療機関IDエラー: {error['detail']}")

def test_create_invalid_classification_level():
    """無効な分析レベルでのエラーテスト"""
    payload = {
        "entity_type": 1,
        "entity_relation_id": 7,  # 存在する医療機関ID（未使用）
        "entity_name": "テスト組織",
        "notification_email_list": random_email_list(),
        "count_reportout_classification": 5,
        "analiris_classification_level": 4  # 無効な値（1-3のみ有効）
    }
    res = requests.post(f"{BASE_URL}/user-entity-links/", json=payload, headers=TEST_HEADERS)
    # Pydanticのvalidatorエラーは422を返す
    assert res.status_code == 422
    error = res.json()
    print(f"✅ 無効な分析レベルエラー: {error}")
    # Pydanticのエラー形式を確認
    assert "detail" in error
    # バリデーションエラーの詳細確認
    if isinstance(error["detail"], list) and len(error["detail"]) > 0:
        validation_error = error["detail"][0]
        assert "analiris_classification_level" in str(validation_error)
    else:
        # 単純な文字列の場合
        assert "分析レポート分類レベル" in error["detail"]

def test_create_missing_required_fields():
    """必須フィールド不足エラーテスト"""
    # entity_nameなし
    payload = {
        "entity_type": 1,
        "entity_relation_id": 7,
        "notification_email_list": random_email_list(),
        "count_reportout_classification": 5,
        "analiris_classification_level": 1
    }
    res = requests.post(f"{BASE_URL}/user-entity-links/", json=payload, headers=TEST_HEADERS)
    assert res.status_code == 422  # Pydanticバリデーションエラー
    print(f"✅ 必須フィールド不足エラー（entity_name）")

def test_read_user_entity_links():
    """ユーザー組織連携情報一覧取得テスト"""
    res = requests.get(f"{BASE_URL}/user-entity-links/", headers=TEST_HEADERS)
    assert res.status_code == 200
    links = res.json()
    print(f"取得した連携情報: {links}")
    assert isinstance(links, list)
    if links:
        # 最初の項目の構造確認
        first_link = links[0]
        required_fields = ["entity_type", "entity_relation_id", "entity_name"]
        for field in required_fields:
            assert field in first_link
    print(f"✅ 連携情報一覧取得成功: {len(links)}件")

def test_read_user_entity_links_with_pagination():
    """ページネーション付き一覧取得テスト"""
    res = requests.get(f"{BASE_URL}/user-entity-links/?skip=0&limit=5", headers=TEST_HEADERS)
    assert res.status_code == 200
    links = res.json()
    assert isinstance(links, list)
    assert len(links) <= 5
    print(f"✅ ページネーション付き一覧取得成功: {len(links)}件")

def test_read_user_entity_link_by_id(test_link):
    """ユーザー組織連携情報個別取得テスト"""
    entity_type = test_link["entity_type"]
    entity_relation_id = test_link["entity_relation_id"]
    res = requests.get(f"{BASE_URL}/user-entity-links/{entity_type}/{entity_relation_id}", headers=TEST_HEADERS)
    assert res.status_code == 200
    link = res.json()

    # レスポンス検証
    assert link["entity_type"] == entity_type
    assert link["entity_relation_id"] == entity_relation_id
    assert link["entity_name"] == test_link["entity_name"]
    print(f"✅ 連携情報個別取得成功: entity_type={entity_type}, entity_relation_id={entity_relation_id}, 組織名={link['entity_name']}")

def test_read_nonexistent_user_entity_link():
    """存在しない連携情報取得でのエラーテスト"""
    res = requests.get(f"{BASE_URL}/user-entity-links/1/99999", headers=TEST_HEADERS)  # 存在しないentity_relation_id
    assert res.status_code == 404
    error = res.json()
    assert "User entity link not found" in error["detail"]
    print(f"✅ 存在しない連携情報エラー: {error['detail']}")

def test_update_user_entity_link(test_link):
    """ユーザー組織連携情報更新テスト"""
    entity_type = test_link["entity_type"]
    entity_relation_id = test_link["entity_relation_id"]
    updated_name = f"更新済み_{random_entity_name()}"
    payload = {
        "entity_type": 1,
        "entity_relation_id": entity_relation_id,  # フィクスチャと同じIDを使用
        "entity_name": updated_name,
        "notification_email_list": random_email_list(),
        "count_reportout_classification": 3,  # 変更
        "analiris_classification_level": 3  # 小分類に変更
    }
    res = requests.put(f"{BASE_URL}/user-entity-links/{entity_type}/{entity_relation_id}", json=payload, headers=TEST_HEADERS)
    assert res.status_code == 200
    link = res.json()

    # 更新確認
    assert link["entity_type"] == entity_type
    assert link["entity_relation_id"] == entity_relation_id
    assert link["entity_name"] == updated_name
    assert link["count_reportout_classification"] == 3
    assert link["analiris_classification_level"] == 3
    print(f"✅ 連携情報更新成功: entity_type={entity_type}, entity_relation_id={entity_relation_id}, 新組織名={updated_name}")

def test_update_with_invalid_data(test_link):
    """無効なデータでの更新エラーテスト"""
    entity_type = test_link["entity_type"]
    entity_relation_id = test_link["entity_relation_id"]
    payload = {
        "entity_type": 3,  # 無効な組織種別
        "entity_relation_id": 6,
        "entity_name": "テスト",
        "notification_email_list": random_email_list(),
        "count_reportout_classification": 5,
        "analiris_classification_level": 1
    }
    res = requests.put(f"{BASE_URL}/user-entity-links/{entity_type}/{entity_relation_id}", json=payload, headers=TEST_HEADERS)
    assert res.status_code == 400
    error = res.json()
    assert "組織種別（entity_type）は1のみサポート" in error["detail"]
    print(f"✅ 更新時の無効データエラー: {error['detail']}")

def test_update_nonexistent_link():
    """存在しない連携情報更新でのエラーテスト"""
    payload = {
        "entity_type": 1,
        "entity_relation_id": 99999,  # 存在しないentity_relation_id
        "entity_name": "存在しない連携情報",
        "notification_email_list": random_email_list(),
        "count_reportout_classification": 5,
        "analiris_classification_level": 1
    }
    res = requests.put(f"{BASE_URL}/user-entity-links/1/99999", json=payload, headers=TEST_HEADERS)  # 存在しない複合キー
    assert res.status_code == 404
    error = res.json()
    assert "User entity link not found" in error["detail"]
    print(f"✅ 存在しない連携情報更新エラー: {error['detail']}")

if __name__ == "__main__":
    print("ユーザー組織連携APIテストを実行します...")
    print("前提: APIサーバーがlocalhost:8000で起動していること")
    print("前提: entity_relation_id=6でテスト用医療機関が登録済みであること")
