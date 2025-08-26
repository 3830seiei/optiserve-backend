#!/usr/bin/env python3
"""
test_medical_equipment_analysis_api.py

医療機器分析設定APIの統合テスト

テスト内容：
1. 取得API（フィルタ・ページング含む）
2. 分析対象更新API
3. 分類上書き更新API 
4. デフォルト復帰API（個別・全件）
5. エラーケースのテスト
"""

import pytest
import requests
import json
import random
import string
from datetime import datetime
from typing import Dict, Any, List


# テスト設定
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1/medical-equipment-analysis-settings"
TEST_HEADERS = {"X-User-Id": "900001"}  # システム管理者のuser_id

# テスト用のダミーデータ
TEST_MEDICAL_ID = 5
TEST_USER_ID = 900001


class TestMedicalEquipmentAnalysisAPI:
    
    def setup_method(self):
        """各テストメソッドの前に実行される初期化"""
        self.base_url = f"{BASE_URL}{API_PREFIX}"
        
        # 既存の設定をクリーンアップ
        try:
            response = requests.delete(f"{self.base_url}?medical_id={TEST_MEDICAL_ID}", headers=TEST_HEADERS)
            print(f"クリーンアップ完了: {response.status_code}")
        except:
            pass

    def test_get_equipment_analysis_settings_basic(self):
        """基本的な設定一覧取得テスト"""
        print("\n=== 基本的な設定一覧取得テスト ===")
        
        response = requests.get(f"{self.base_url}?medical_id={TEST_MEDICAL_ID}", headers=TEST_HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        
        # レスポンス構造の確認
        assert "items" in data
        assert "total_count" in data
        assert "has_next" in data
        assert isinstance(data["items"], list)
        assert isinstance(data["total_count"], int)
        assert isinstance(data["has_next"], bool)
        
        print(f"✅ 総件数: {data['total_count']}件")
        print(f"✅ 次ページ有無: {data['has_next']}")
        
        if data["items"]:
            # 最初のアイテムの構造確認
            item = data["items"][0]
            required_fields = [
                "ledger_id", "medical_id", "model_number", "stock_quantity",
                "default_is_included", "effective_is_included", "has_override"
            ]
            
            for field in required_fields:
                assert field in item, f"必須フィールド '{field}' が存在しません"
            
            print(f"✅ サンプルアイテム: ledger_id={item['ledger_id']}, model='{item['model_number']}'")

    def test_get_equipment_analysis_settings_with_pagination(self):
        """ページング機能テスト"""
        print("\n=== ページング機能テスト ===")
        
        # 1ページ目を取得
        response1 = requests.get(f"{self.base_url}?medical_id={TEST_MEDICAL_ID}&skip=0&limit=5", headers=TEST_HEADERS)
        assert response1.status_code == 200
        data1 = response1.json()
        
        print(f"✅ 1ページ目: {len(data1['items'])}件取得")
        
        if data1["total_count"] > 5:
            # 2ページ目を取得
            response2 = requests.get(f"{self.base_url}?medical_id={TEST_MEDICAL_ID}&skip=5&limit=5", headers=TEST_HEADERS)
            assert response2.status_code == 200
            data2 = response2.json()
            
            print(f"✅ 2ページ目: {len(data2['items'])}件取得")
            
            # 異なるデータが取得されることを確認
            if data1["items"] and data2["items"]:
                assert data1["items"][0]["ledger_id"] != data2["items"][0]["ledger_id"]
                print("✅ ページング正常動作")

    def test_update_analysis_target_success(self):
        """分析対象フラグ更新成功テスト"""
        print("\n=== 分析対象フラグ更新成功テスト ===")
        
        # まず一覧を取得して対象を選択
        response = requests.get(f"{self.base_url}?medical_id={TEST_MEDICAL_ID}&limit=1", headers=TEST_HEADERS)
        assert response.status_code == 200
        data = response.json()
        
        if not data["items"]:
            pytest.skip("テスト対象データが存在しません")
        
        target_item = data["items"][0]
        ledger_id = target_item["ledger_id"]
        current_value = target_item["default_is_included"]
        new_value = not current_value  # 反転した値を設定
        
        print(f"✅ テスト対象: ledger_id={ledger_id}, 現在値={current_value} → 新値={new_value}")
        
        # 分析対象フラグを更新
        update_data = {
            "override_is_included": new_value,
            "note": f"テスト更新 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        response = requests.put(f"{self.base_url}/{ledger_id}/analysis-target", json=update_data, headers=TEST_HEADERS)
        
        assert response.status_code == 200
        result = response.json()
        
        # レスポンスの確認
        assert result["ledger_id"] == ledger_id
        assert result["override_is_included"] == new_value
        assert result["effective_is_included"] == new_value
        assert "updated_at" in result
        assert "message" in result
        
        print(f"✅ 更新成功: {result['message']}")
        
        # 更新後の状態を確認
        response = requests.get(f"{self.base_url}?medical_id={TEST_MEDICAL_ID}&skip=0&limit=100", headers=TEST_HEADERS)
        updated_data = response.json()
        
        # 該当アイテムを検索
        updated_item = None
        for item in updated_data["items"]:
            if item["ledger_id"] == ledger_id:
                updated_item = item
                break
        
        assert updated_item is not None
        assert updated_item["has_override"] == True
        assert updated_item["effective_is_included"] == new_value
        assert updated_item["override_is_included"] == new_value
        
        print("✅ 設定反映確認完了")

    def test_update_analysis_target_same_as_default_error(self):
        """デフォルト値と同じ値での更新エラーテスト"""
        print("\n=== デフォルト値同一エラーテスト ===")
        
        # 一覧を取得して対象を選択
        response = requests.get(f"{self.base_url}?medical_id={TEST_MEDICAL_ID}&limit=1", headers=TEST_HEADERS)
        assert response.status_code == 200
        data = response.json()
        
        if not data["items"]:
            pytest.skip("テスト対象データが存在しません")
        
        target_item = data["items"][0]
        ledger_id = target_item["ledger_id"]
        default_value = target_item["default_is_included"]
        
        print(f"✅ テスト対象: ledger_id={ledger_id}, デフォルト値={default_value}")
        
        # デフォルト値と同じ値で更新を試行
        update_data = {
            "override_is_included": default_value,
            "note": "デフォルト値と同じ値でのテスト"
        }
        
        response = requests.put(f"{self.base_url}/{ledger_id}/analysis-target", json=update_data, headers=TEST_HEADERS)
        
        assert response.status_code == 400
        error_data = response.json()
        assert "デフォルト値" in error_data["detail"]
        
        print(f"✅ 期待通りのエラー: {error_data['detail']}")

    def test_update_classification_override_success(self):
        """分類上書き更新成功テスト"""
        print("\n=== 分類上書き更新成功テスト ===")
        
        # 一覧を取得して対象を選択
        response = requests.get(f"{self.base_url}?medical_id={TEST_MEDICAL_ID}&limit=10", headers=TEST_HEADERS)
        assert response.status_code == 200
        data = response.json()
        
        if not data["items"]:
            pytest.skip("テスト対象データが存在しません")
        
        # デフォルト分類IDが異なる2つのアイテムを探す
        target_item = None
        override_classification_id = None
        
        for item in data["items"]:
            if item["default_classification_id"]:
                if target_item is None:
                    target_item = item
                elif (item["default_classification_id"] != target_item["default_classification_id"]):
                    override_classification_id = item["default_classification_id"]
                    break
        
        if target_item is None or override_classification_id is None:
            pytest.skip("分類上書きテスト用のデータが不足しています")
        
        ledger_id = target_item["ledger_id"]
        
        print(f"✅ テスト対象: ledger_id={ledger_id}")
        print(f"   元分類ID: {target_item['default_classification_id']}")
        print(f"   新分類ID: {override_classification_id}")
        
        # 分類上書きを更新
        update_data = {
            "override_classification_id": override_classification_id,
            "note": f"分類変更テスト {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        response = requests.put(f"{self.base_url}/{ledger_id}/classification", json=update_data, headers=TEST_HEADERS)
        
        assert response.status_code == 200
        result = response.json()
        
        # レスポンスの確認
        assert result["ledger_id"] == ledger_id
        assert result["override_classification_id"] == override_classification_id
        assert result["effective_classification_id"] == override_classification_id
        assert "classification_name" in result
        assert "updated_at" in result
        
        print(f"✅ 更新成功: {result['message']}")
        print(f"   新分類名: {result['classification_name']}")

    def test_restore_to_default_single(self):
        """個別デフォルト復帰テスト"""
        print("\n=== 個別デフォルト復帰テスト ===")
        
        # まず上書き設定を作成
        response = requests.get(f"{self.base_url}?medical_id={TEST_MEDICAL_ID}&limit=1", headers=TEST_HEADERS)
        assert response.status_code == 200
        data = response.json()
        
        if not data["items"]:
            pytest.skip("テスト対象データが存在しません")
        
        target_item = data["items"][0]
        ledger_id = target_item["ledger_id"]
        current_value = target_item["default_is_included"]
        new_value = not current_value
        
        # 設定を作成
        update_data = {
            "override_is_included": new_value,
            "note": "復帰テスト用の設定"
        }
        
        response = requests.put(f"{self.base_url}/{ledger_id}/analysis-target", json=update_data, headers=TEST_HEADERS)
        assert response.status_code == 200
        
        print(f"✅ テスト用設定作成完了: ledger_id={ledger_id}")
        
        # デフォルトに復帰
        response = requests.delete(f"{self.base_url}/{ledger_id}", headers=TEST_HEADERS)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["affected_count"] == 1
        assert result["ledger_ids"] == [ledger_id]
        assert "復帰" in result["message"]
        
        print(f"✅ 復帰成功: {result['message']}")
        
        # 復帰後の状態確認
        response = requests.get(f"{self.base_url}?medical_id={TEST_MEDICAL_ID}", headers=TEST_HEADERS)
        updated_data = response.json()
        
        updated_item = None
        for item in updated_data["items"]:
            if item["ledger_id"] == ledger_id:
                updated_item = item
                break
        
        assert updated_item is not None
        assert updated_item["has_override"] == False
        assert updated_item["effective_is_included"] == updated_item["default_is_included"]
        
        print("✅ デフォルト復帰確認完了")

    def test_restore_to_default_all(self):
        """全件デフォルト復帰テスト"""
        print("\n=== 全件デフォルト復帰テスト ===")
        
        # 複数の設定を作成
        response = requests.get(f"{self.base_url}?medical_id={TEST_MEDICAL_ID}&limit=3", headers=TEST_HEADERS)
        assert response.status_code == 200
        data = response.json()
        
        if len(data["items"]) < 2:
            pytest.skip("全件復帰テスト用のデータが不足しています")
        
        created_settings = []
        
        for i, item in enumerate(data["items"][:2]):
            ledger_id = item["ledger_id"]
            current_value = item["default_is_included"]
            new_value = not current_value
            
            update_data = {
                "override_is_included": new_value,
                "note": f"全件復帰テスト用設定 {i+1}"
            }
            
            response = requests.put(f"{self.base_url}/{ledger_id}/analysis-target", json=update_data, headers=TEST_HEADERS)
            assert response.status_code == 200
            created_settings.append(ledger_id)
        
        print(f"✅ テスト用設定作成完了: {len(created_settings)}件")
        
        # 全件デフォルト復帰
        response = requests.delete(f"{self.base_url}?medical_id={TEST_MEDICAL_ID}", headers=TEST_HEADERS)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["affected_count"] >= len(created_settings)
        
        print(f"✅ 全件復帰成功: {result['affected_count']}件削除")
        print(f"   メッセージ: {result['message']}")
        
        # 復帰後の状態確認
        response = requests.get(f"{self.base_url}?medical_id={TEST_MEDICAL_ID}", headers=TEST_HEADERS)
        final_data = response.json()
        
        # すべてのアイテムがデフォルト設定になっていることを確認
        for item in final_data["items"]:
            assert item["has_override"] == False
            assert item["effective_is_included"] == item["default_is_included"]
        
        print("✅ 全件デフォルト復帰確認完了")

    def test_invalid_ledger_id_error(self):
        """存在しない機器IDでのエラーテスト"""
        print("\n=== 存在しない機器IDエラーテスト ===")
        
        invalid_ledger_id = 999999
        
        update_data = {
            "override_is_included": True,
            "note": "存在しないIDテスト"
        }
        
        response = requests.put(f"{self.base_url}/{invalid_ledger_id}/analysis-target", json=update_data, headers=TEST_HEADERS)
        
        assert response.status_code == 404
        error_data = response.json()
        assert "見つかりません" in error_data["detail"]
        
        print(f"✅ 期待通りのエラー: {error_data['detail']}")

    def test_invalid_classification_id_error(self):
        """存在しない分類IDでのエラーテスト"""
        print("\n=== 存在しない分類IDエラーテスト ===")
        
        # 一覧を取得して対象を選択
        response = requests.get(f"{self.base_url}?medical_id={TEST_MEDICAL_ID}&limit=1", headers=TEST_HEADERS)
        assert response.status_code == 200
        data = response.json()
        
        if not data["items"]:
            pytest.skip("テスト対象データが存在しません")
        
        target_item = data["items"][0]
        ledger_id = target_item["ledger_id"]
        
        invalid_classification_id = 999999
        
        update_data = {
            "override_classification_id": invalid_classification_id,
            "note": "存在しない分類IDテスト"
        }
        
        response = requests.put(f"{self.base_url}/{ledger_id}/classification", json=update_data, headers=TEST_HEADERS)
        
        assert response.status_code == 400
        error_data = response.json()
        assert "存在しません" in error_data["detail"]
        
        print(f"✅ 期待通りのエラー: {error_data['detail']}")


def run_all_tests():
    """全テストを実行"""
    print("=== 医療機器分析設定API 統合テストを開始 ===\n")
    
    test_instance = TestMedicalEquipmentAnalysisAPI()
    
    tests = [
        test_instance.test_get_equipment_analysis_settings_basic,
        test_instance.test_get_equipment_analysis_settings_with_pagination,
        test_instance.test_update_analysis_target_success,
        test_instance.test_update_analysis_target_same_as_default_error,
        test_instance.test_update_classification_override_success,
        test_instance.test_restore_to_default_single,
        test_instance.test_restore_to_default_all,
        test_instance.test_invalid_ledger_id_error,
        test_instance.test_invalid_classification_id_error
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_instance.setup_method()
            test_func()
            passed += 1
            print(f"✅ {test_func.__name__}: PASS\n")
        except Exception as e:
            failed += 1
            print(f"❌ {test_func.__name__}: FAIL")
            print(f"   エラー: {str(e)}\n")
    
    print(f"\n=== テスト結果 ===")
    print(f"成功: {passed}件")
    print(f"失敗: {failed}件")
    print(f"合計: {passed + failed}件")
    
    if failed == 0:
        print("🎉 全テストが成功しました！")
    else:
        print("⚠️  一部のテストが失敗しました。")


if __name__ == "__main__":
    run_all_tests()