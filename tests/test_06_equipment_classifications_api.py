"""test_equipment_classifications_api.py

pytestを使用して機器分類・レポート出力選択APIのテストを行います。

実行方法:
- startup_optiserve.shを実行してAPIサーバーを起動
- テスト用データを作成: python tests/create_equipment_classification.py
- pytest tests/test_equipment_classifications_api.py -v

前提条件:
- medical_id=5でテスト用医療機関が登録済みであること
- テスト実行前に自動でクリーンアップが実行されます
- 機器分類マスタデータが登録されていること
"""

import pytest
import requests
import random
import sys
import os
from pathlib import Path

# プロジェクトルートをsys.pathに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# 環境に応じたAPI接続先の自動判定
API_HOST = os.environ.get("OPTISERVE_API_HOST", "localhost")
BASE_URL = f"http://{API_HOST}:8000/api/v1"

# テスト用の共通ヘッダー（認証情報）
TEST_HEADERS = {"X-User-Id": "900001"}  # システム管理者のuser_id

def cleanup_test_data():
    """テスト実行前のクリーンアップ - テスト用レポート選択データを削除"""
    try:
        print("🔍 クリーンアップ開始: テストレポート選択データをチェック中...")

        # DBテストレコードのクリーンアップ
        from src.database import SessionLocal
        from src.models.pg_optigate.equipment_classification_report_selection import EquipmentClassificationReportSelection

        db = SessionLocal()
        try:
            # テスト用医療機関のレポート選択データを削除
            deleted_selections = db.query(EquipmentClassificationReportSelection).filter(
                EquipmentClassificationReportSelection.medical_id.in_([5, 999])
            ).delete(synchronize_session=False)

            db.commit()
            print(f"🧹 DB クリーンアップ: レポート選択データ{deleted_selections}件を削除")

        except Exception as e:
            print(f"DB クリーンアップエラー: {e}")
            db.rollback()
        finally:
            db.close()

        print("✅ クリーンアップ完了")

    except Exception as e:
        print(f"❌ クリーンアップエラー: {e}")

# テスト開始前にクリーンアップ実行
cleanup_test_data()

def test_api_server_is_running():
    """APIサーバーが起動していることを確認"""
    try:
        response = requests.get(f"{BASE_URL}/equipment-classifications/5", headers=TEST_HEADERS, timeout=5)
        assert response.status_code in [200, 404]  # サーバーが応答していれば200または404
        print("✅ APIサーバー起動確認完了")
    except requests.exceptions.RequestException:
        pytest.fail("❌ APIサーバーが起動していません。startup_optiserve.shを実行してください")

def test_get_equipment_classifications():
    """機器分類一覧取得テスト"""
    medical_id = 5

    res = requests.get(f"{BASE_URL}/equipment-classifications/{medical_id}", headers=TEST_HEADERS)

    assert res.status_code == 200
    data = res.json()

    # レスポンス構造確認
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert "items" in data
    assert isinstance(data["items"], list)

    # 基本的なページネーション確認
    assert data["skip"] == 0
    assert data["limit"] == 100

    print(f"✅ 機器分類一覧取得成功: total={data['total']}, 取得件数={len(data['items'])}")

    # サンプルアイテムの構造確認（データがある場合）
    if data["items"]:
        item = data["items"][0]
        required_fields = ["classification_id", "medical_id", "classification_level", "classification_name"]
        for field in required_fields:
            assert field in item
        print(f"   サンプル分類: {item['classification_name']} (level={item['classification_level']})")

def test_get_equipment_classifications_pagination():
    """機器分類一覧ページネーションテスト"""
    medical_id = 5

    # 1ページ目
    res1 = requests.get(f"{BASE_URL}/equipment-classifications/{medical_id}?skip=0&limit=5", headers=TEST_HEADERS)
    assert res1.status_code == 200
    data1 = res1.json()

    # 2ページ目
    res2 = requests.get(f"{BASE_URL}/equipment-classifications/{medical_id}?skip=5&limit=5", headers=TEST_HEADERS)
    assert res2.status_code == 200
    data2 = res2.json()

    # ページネーション確認
    assert data1["skip"] == 0
    assert data1["limit"] == 5
    assert data2["skip"] == 5
    assert data2["limit"] == 5
    assert data1["total"] == data2["total"]  # 総件数は同じ

    print(f"✅ ページネーション確認完了: 1ページ目={len(data1['items'])}件, 2ページ目={len(data2['items'])}件")

def test_get_equipment_classifications_nonexistent_medical_id():
    """存在しない医療機関IDでのエラーテスト"""
    nonexistent_medical_id = 999

    res = requests.get(f"{BASE_URL}/equipment-classifications/{nonexistent_medical_id}", headers=TEST_HEADERS)

    assert res.status_code == 404
    assert "存在しません" in res.json().get("detail", "")
    print("✅ 存在しない医療機関IDでのエラーテスト成功")

def test_get_report_selection_empty():
    """レポート選択情報取得テスト（初期状態：空）"""
    medical_id = 5

    res = requests.get(f"{BASE_URL}/equipment-classifications/report-selection/{medical_id}", headers=TEST_HEADERS)

    assert res.status_code == 200
    data = res.json()

    # レスポンス構造確認
    assert "medical_id" in data
    assert "max_count" in data
    assert "selections" in data
    assert data["medical_id"] == medical_id
    assert isinstance(data["max_count"], int)
    assert isinstance(data["selections"], list)
    assert len(data["selections"]) == 0  # 初期状態は空

    print(f"✅ レポート選択情報取得成功（初期状態）: max_count={data['max_count']}, 選択数={len(data['selections'])}")

def test_create_report_selection():
    """レポート選択情報登録テスト"""
    medical_id = 5

    # まず機器分類一覧から登録用のIDを取得
    classifications_res = requests.get(f"{BASE_URL}/equipment-classifications/{medical_id}?limit=10", headers=TEST_HEADERS)
    assert classifications_res.status_code == 200
    classifications = classifications_res.json()["items"]

    if len(classifications) < 3:
        pytest.skip("テスト用機器分類データが不足しています")

    # 3件の機器分類を選択
    selected_ids = [item["classification_id"] for item in classifications[:3]]

    # レポート選択情報を登録
    request_data = {
        "classification_ids": selected_ids
    }

    res = requests.post(
        f"{BASE_URL}/equipment-classifications/report-selection/{medical_id}",
        json=request_data,
        headers=TEST_HEADERS
    )

    assert res.status_code == 200
    data = res.json()

    # レスポンス確認
    assert data["medical_id"] == medical_id
    assert data["created_count"] == 3
    assert len(data["selections"]) == 3

    # rank順序確認
    for i, selection in enumerate(data["selections"], 1):
        assert selection["rank"] == i
        assert selection["classification_id"] == selected_ids[i-1]
        assert "classification_name" in selection

    print(f"✅ レポート選択情報登録成功: 登録数={data['created_count']}")
    for selection in data["selections"]:
        print(f"   rank={selection['rank']}: {selection['classification_name']} (ID={selection['classification_id']})")

def test_get_report_selection_after_create():
    """レポート選択情報登録後の取得テスト"""
    medical_id = 5

    res = requests.get(f"{BASE_URL}/equipment-classifications/report-selection/{medical_id}", headers=TEST_HEADERS)

    assert res.status_code == 200
    data = res.json()

    # 登録後なので選択情報が存在するはず
    assert data["medical_id"] == medical_id
    assert len(data["selections"]) > 0

    # rank順序確認
    for i, selection in enumerate(data["selections"], 1):
        assert selection["rank"] == i
        assert isinstance(selection["classification_id"], int)
        assert isinstance(selection["classification_name"], str)

    print(f"✅ レポート選択情報取得成功（登録後）: 選択数={len(data['selections'])}")
    print(f"   選択情報:")
    for selection in data["selections"]:
        print(f"     - rank={selection['rank']}: {selection['classification_name']} (ID={selection['classification_id']})")

def test_update_report_selection():
    """レポート選択情報更新テスト（上書き登録）"""
    medical_id = 5

    # 機器分類一覧から異なるIDを取得
    classifications_res = requests.get(f"{BASE_URL}/equipment-classifications/{medical_id}?limit=10", headers=TEST_HEADERS)
    assert classifications_res.status_code == 200
    classifications = classifications_res.json()["items"]

    if len(classifications) < 5:
        pytest.skip("テスト用機器分類データが不足しています")

    # 異なる5件の機器分類を選択（後半から選択）
    selected_ids = [item["classification_id"] for item in classifications[-5:]]

    # レポート選択情報を更新登録
    request_data = {
        "classification_ids": selected_ids
    }

    res = requests.post(
        f"{BASE_URL}/equipment-classifications/report-selection/{medical_id}",
        json=request_data,
        headers=TEST_HEADERS
    )

    assert res.status_code == 200
    data = res.json()

    # 更新確認
    assert data["medical_id"] == medical_id
    assert data["created_count"] == 5
    assert len(data["selections"]) == 5

    print(f"✅ レポート選択情報更新成功: 更新数={data['created_count']}")

def test_create_report_selection_invalid_classification_ids():
    """無効な機器分類IDでの登録エラーテスト"""
    medical_id = 5
    invalid_classification_ids = [99999, 99998, 99997]  # 存在しないID

    request_data = {
        "classification_ids": invalid_classification_ids
    }

    res = requests.post(
        f"{BASE_URL}/equipment-classifications/report-selection/{medical_id}",
        json=request_data,
        headers=TEST_HEADERS
    )

    assert res.status_code == 400
    assert "存在しません" in res.json().get("detail", "")
    print("✅ 無効な機器分類IDでの登録エラーテスト成功")

def test_create_report_selection_duplicate_ids():
    """重複した機器分類IDでの登録エラーテスト"""
    medical_id = 5

    # 機器分類一覧から1件取得
    classifications_res = requests.get(f"{BASE_URL}/equipment-classifications/{medical_id}?limit=1", headers=TEST_HEADERS)
    assert classifications_res.status_code == 200
    classifications = classifications_res.json()["items"]

    if not classifications:
        pytest.skip("テスト用機器分類データが不足しています")

    # 同じIDを重複指定
    classification_id = classifications[0]["classification_id"]
    duplicate_ids = [classification_id, classification_id, classification_id]

    request_data = {
        "classification_ids": duplicate_ids
    }

    res = requests.post(
        f"{BASE_URL}/equipment-classifications/report-selection/{medical_id}",
        json=request_data,
        headers=TEST_HEADERS
    )

    assert res.status_code == 422  # Pydanticバリデーションエラー
    print("✅ 重複した機器分類IDでの登録エラーテスト成功")

def test_delete_report_selection():
    """レポート選択情報削除テスト"""
    medical_id = 5

    res = requests.delete(f"{BASE_URL}/equipment-classifications/report-selection/{medical_id}", headers=TEST_HEADERS)

    assert res.status_code == 200
    data = res.json()

    # レスポンス確認
    assert data["medical_id"] == medical_id
    assert isinstance(data["deleted_count"], int)

    print(f"✅ レポート選択情報削除成功: 削除数={data['deleted_count']}")

    # 削除後に取得して空になっていることを確認
    get_res = requests.get(f"{BASE_URL}/equipment-classifications/report-selection/{medical_id}", headers=TEST_HEADERS)
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert len(get_data["selections"]) == 0
    print("✅ 削除後の確認完了: 選択情報が空になりました")

def test_report_selection_nonexistent_medical_id():
    """存在しない医療機関IDでのレポート選択エラーテスト"""
    nonexistent_medical_id = 999

    # 取得
    get_res = requests.get(f"{BASE_URL}/equipment-classifications/report-selection/{nonexistent_medical_id}", headers=TEST_HEADERS)
    assert get_res.status_code == 404

    # 登録
    request_data = {"classification_ids": [1, 2, 3]}
    post_res = requests.post(
        f"{BASE_URL}/equipment-classifications/report-selection/{nonexistent_medical_id}",
        json=request_data,
        headers=TEST_HEADERS
    )
    assert post_res.status_code == 404

    # 削除
    delete_res = requests.delete(f"{BASE_URL}/equipment-classifications/report-selection/{nonexistent_medical_id}", headers=TEST_HEADERS)
    assert delete_res.status_code == 404

    print("✅ 存在しない医療機関IDでのレポート選択エラーテスト成功")

if __name__ == "__main__":
    print("機器分類・レポート選択APIテストを実行します...")
    print("前提: APIサーバーがlocalhost:8000で起動していること")
    print("前提: 機器分類データが登録されていること（create_equipment_classification.py実行済み）")
