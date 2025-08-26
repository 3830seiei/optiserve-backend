"""test_auth.py

AuthManagerクラスの認証・認可機能のテスト

実行方法:
- startup_optiserve.shを実行してAPIサーバーを起動
- pytest tests/test_auth.py -v

前提条件:
- システム管理者ユーザー（user_id=900001）が登録済みであること
- 医療機関ユーザーが登録済みであること
- テスト用医療機関が登録済みであること
"""

import pytest
import sys
import os
from unittest.mock import Mock

# プロジェクトルートをsys.pathに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.utils.auth import AuthManager, UserInfo
from src.database import SessionLocal
from fastapi import HTTPException


@pytest.fixture(scope="function")
def db_session():
    """テスト用データベースセッション"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function") 
def mock_admin_user():
    """モックシステム管理者ユーザー"""
    user = Mock()
    user.user_id = "900001"
    user.user_name = "システム管理者"
    user.entity_type = 9
    user.entity_relation_id = 0
    return user


@pytest.fixture(scope="function")
def mock_medical_user():
    """モック医療機関ユーザー"""
    user = Mock()
    user.user_id = "100001"
    user.user_name = "医療機関ユーザー"
    user.entity_type = 1
    user.entity_relation_id = 6  # テスト用医療機関ID
    return user


@pytest.fixture(scope="function")
def mock_invalid_user():
    """モック無効ユーザー（ディーラー）"""
    user = Mock()
    user.user_id = "200001"
    user.user_name = "ディーラーユーザー"
    user.entity_type = 2
    user.entity_relation_id = 1
    return user


class TestAuthManagerUserInfo:
    """AuthManager.get_user_info()のテスト"""
    
    def test_get_user_info_admin_success(self, db_session, monkeypatch):
        """システム管理者ユーザー情報取得成功テスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "900001"
        mock_user.user_name = "システム管理者"
        mock_user.entity_type = 9
        mock_user.entity_relation_id = 0
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # テスト実行
        user_info = AuthManager.get_user_info("900001", db_session)
        
        # アサーション
        assert isinstance(user_info, UserInfo)
        assert user_info.user_id == "900001"
        assert user_info.user_name == "システム管理者"
        assert user_info.entity_type == 9
        assert user_info.entity_relation_id == 0
        assert user_info.is_admin is True
    
    def test_get_user_info_medical_success(self, db_session, monkeypatch):
        """医療機関ユーザー情報取得成功テスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "100001"
        mock_user.user_name = "医療機関ユーザー"
        mock_user.entity_type = 1
        mock_user.entity_relation_id = 6
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # テスト実行
        user_info = AuthManager.get_user_info("100001", db_session)
        
        # アサーション
        assert isinstance(user_info, UserInfo)
        assert user_info.user_id == "100001"
        assert user_info.user_name == "医療機関ユーザー"
        assert user_info.entity_type == 1
        assert user_info.entity_relation_id == 6
        assert user_info.is_admin is False
    
    def test_get_user_info_not_found(self, db_session, monkeypatch):
        """存在しないユーザーでの401エラーテスト"""
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = None
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # テスト実行・アサーション
        with pytest.raises(HTTPException) as exc_info:
            AuthManager.get_user_info("99999", db_session)
        
        assert exc_info.value.status_code == 401
        assert "ユーザーID 99999 が存在しません" in exc_info.value.detail


class TestAuthManagerAdminChecks:
    """AuthManagerの管理者権限チェックのテスト"""
    
    def test_is_admin_user_id_true(self):
        """is_admin_user_id: システム管理者IDのテスト"""
        assert AuthManager.is_admin_user_id("900001") is True  # 最小値
        assert AuthManager.is_admin_user_id("999999") is True  # 最大値
        assert AuthManager.is_admin_user_id("950000") is True  # 中間値
    
    def test_is_admin_user_id_false(self):
        """is_admin_user_id: 非システム管理者IDのテスト"""
        assert AuthManager.is_admin_user_id("900000") is False  # 境界値（下限未満）
        assert AuthManager.is_admin_user_id("1000000") is False  # 境界値（上限超過）
        assert AuthManager.is_admin_user_id("100001") is False  # 医療機関ユーザー
        assert AuthManager.is_admin_user_id("200001") is False  # ディーラーユーザー
        assert AuthManager.is_admin_user_id("1") is False  # 通常ユーザー
    
    def test_is_admin_by_user_info_true(self):
        """is_admin: entity_type=9でのテスト"""
        user_info = UserInfo(
            user_id="900001",
            user_name="システム管理者",
            entity_type=9,
            entity_relation_id=0,
            is_admin=True
        )
        assert AuthManager.is_admin(user_info) is True
    
    def test_is_admin_by_user_info_false(self):
        """is_admin: entity_type!=9でのテスト"""
        user_info = UserInfo(
            user_id="100001",
            user_name="医療機関ユーザー",
            entity_type=1,
            entity_relation_id=6,
            is_admin=False
        )
        assert AuthManager.is_admin(user_info) is False
    
    def test_require_admin_permission_success(self, db_session, monkeypatch):
        """require_admin_permission: 管理者権限チェック成功テスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "900001"
        mock_user.user_name = "システム管理者"
        mock_user.entity_type = 9
        mock_user.entity_relation_id = 0
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # テスト実行（例外が発生しないことを確認）
        try:
            AuthManager.require_admin_permission("900001", db_session)
        except HTTPException:
            pytest.fail("管理者ユーザーで例外が発生しました")
    
    def test_require_admin_permission_failure(self, db_session, monkeypatch):
        """require_admin_permission: 管理者権限なしでの403エラーテスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "100001"
        mock_user.user_name = "医療機関ユーザー"
        mock_user.entity_type = 1
        mock_user.entity_relation_id = 6
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # テスト実行・アサーション
        with pytest.raises(HTTPException) as exc_info:
            AuthManager.require_admin_permission("100001", db_session)
        
        assert exc_info.value.status_code == 403
        assert "システム管理者権限が必要です" in exc_info.value.detail


class TestAuthManagerMedicalPermissions:
    """AuthManagerの医療機関権限チェックのテスト"""
    
    def test_get_user_medical_id_admin(self, db_session, monkeypatch):
        """get_user_medical_id: システム管理者の場合はNoneを返すテスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "900001"
        mock_user.user_name = "システム管理者"
        mock_user.entity_type = 9
        mock_user.entity_relation_id = 0
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # テスト実行
        medical_id = AuthManager.get_user_medical_id("900001", db_session)
        
        # アサーション
        assert medical_id is None
    
    def test_get_user_medical_id_medical_user(self, db_session, monkeypatch):
        """get_user_medical_id: 医療機関ユーザーの医療機関ID取得テスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "100001"
        mock_user.user_name = "医療機関ユーザー"
        mock_user.entity_type = 1
        mock_user.entity_relation_id = 6
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # テスト実行
        medical_id = AuthManager.get_user_medical_id("100001", db_session)
        
        # アサーション
        assert medical_id == 6
    
    def test_get_user_medical_id_invalid_entity_type(self, db_session, monkeypatch):
        """get_user_medical_id: 無効なentity_typeでの403エラーテスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "200001"
        mock_user.user_name = "ディーラーユーザー"
        mock_user.entity_type = 2
        mock_user.entity_relation_id = 1
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # テスト実行・アサーション
        with pytest.raises(HTTPException) as exc_info:
            AuthManager.get_user_medical_id("200001", db_session)
        
        assert exc_info.value.status_code == 403
        assert "医療機関ユーザーまたはシステム管理者である必要があります" in exc_info.value.detail
    
    def test_check_medical_permission_admin_access(self, db_session, monkeypatch):
        """check_medical_permission: 管理者の全医療機関アクセス可能テスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "900001"
        mock_user.user_name = "システム管理者"
        mock_user.entity_type = 9
        mock_user.entity_relation_id = 0
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # テスト実行
        result = AuthManager.check_medical_permission("900001", 6, db_session)
        
        # アサーション
        assert result is True
    
    def test_check_medical_permission_medical_user_own_facility(self, db_session, monkeypatch):
        """check_medical_permission: 医療機関ユーザーの自医療機関アクセス可能テスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "100001"
        mock_user.user_name = "医療機関ユーザー"
        mock_user.entity_type = 1
        mock_user.entity_relation_id = 6
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # テスト実行
        result = AuthManager.check_medical_permission("100001", 6, db_session)
        
        # アサーション
        assert result is True
    
    def test_check_medical_permission_medical_user_other_facility(self, db_session, monkeypatch):
        """check_medical_permission: 医療機関ユーザーの他医療機関アクセス不可テスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "100001"
        mock_user.user_name = "医療機関ユーザー"
        mock_user.entity_type = 1
        mock_user.entity_relation_id = 6
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # テスト実行
        result = AuthManager.check_medical_permission("100001", 7, db_session)  # 異なる医療機関ID
        
        # アサーション
        assert result is False
    
    def test_require_medical_permission_success(self, db_session, monkeypatch):
        """require_medical_permission: アクセス権限ありでの成功テスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "100001"
        mock_user.user_name = "医療機関ユーザー"
        mock_user.entity_type = 1
        mock_user.entity_relation_id = 6
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # テスト実行（例外が発生しないことを確認）
        try:
            AuthManager.require_medical_permission("100001", 6, db_session)
        except HTTPException:
            pytest.fail("有効な医療機関アクセスで例外が発生しました")
    
    def test_require_medical_permission_failure(self, db_session, monkeypatch):
        """require_medical_permission: アクセス権限なしでの403エラーテスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "100001"
        mock_user.user_name = "医療機関ユーザー"
        mock_user.entity_type = 1
        mock_user.entity_relation_id = 6
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # テスト実行・アサーション
        with pytest.raises(HTTPException) as exc_info:
            AuthManager.require_medical_permission("100001", 7, db_session)  # 異なる医療機関ID
        
        assert exc_info.value.status_code == 403
        assert "医療機関ID 7 への操作権限がありません" in exc_info.value.detail


class TestAuthManagerAccessibleMedicalIds:
    """AuthManager.get_accessible_medical_ids()のテスト"""
    
    def test_get_accessible_medical_ids_admin(self, db_session, monkeypatch):
        """get_accessible_medical_ids: 管理者は全医療機関アクセス可能（None返却）テスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "900001"
        mock_user.user_name = "システム管理者"
        mock_user.entity_type = 9
        mock_user.entity_relation_id = 0
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # テスト実行
        accessible_ids = AuthManager.get_accessible_medical_ids("900001", db_session)
        
        # アサーション
        assert accessible_ids is None
    
    def test_get_accessible_medical_ids_medical_user(self, db_session, monkeypatch):
        """get_accessible_medical_ids: 医療機関ユーザーは自医療機関のみテスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "100001"
        mock_user.user_name = "医療機関ユーザー"
        mock_user.entity_type = 1
        mock_user.entity_relation_id = 6
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # テスト実行
        accessible_ids = AuthManager.get_accessible_medical_ids("100001", db_session)
        
        # アサーション
        assert accessible_ids == [6]
    
    def test_get_accessible_medical_ids_invalid_user(self, db_session, monkeypatch):
        """get_accessible_medical_ids: 無効ユーザーは空リストテスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "200001"
        mock_user.user_name = "ディーラーユーザー"
        mock_user.entity_type = 2
        mock_user.entity_relation_id = 1
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # テスト実行
        accessible_ids = AuthManager.get_accessible_medical_ids("200001", db_session)
        
        # アサーション
        assert accessible_ids == []


class TestAuthManagerQueryFiltering:
    """AuthManager.filter_by_medical_permission()のテスト"""
    
    def test_filter_by_medical_permission_admin(self, db_session, monkeypatch):
        """filter_by_medical_permission: 管理者はフィルタなしテスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "900001"
        mock_user.user_name = "システム管理者"
        mock_user.entity_type = 9
        mock_user.entity_relation_id = 0
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # モッククエリを作成
        mock_query_obj = Mock()
        mock_column = Mock()
        
        # テスト実行
        result = AuthManager.filter_by_medical_permission(
            mock_query_obj, "900001", db_session, mock_column
        )
        
        # アサーション（フィルタされずに元のクエリが返されることを確認）
        assert result == mock_query_obj
    
    def test_filter_by_medical_permission_medical_user(self, db_session, monkeypatch):
        """filter_by_medical_permission: 医療機関ユーザーはフィルタ適用テスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "100001"
        mock_user.user_name = "医療機関ユーザー"
        mock_user.entity_type = 1
        mock_user.entity_relation_id = 6
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # モッククエリを作成
        mock_query_obj = Mock()
        mock_filtered_query = Mock()
        mock_query_obj.filter.return_value = mock_filtered_query
        
        mock_column = Mock()
        mock_column.in_.return_value = "filtered_condition"
        
        # テスト実行
        result = AuthManager.filter_by_medical_permission(
            mock_query_obj, "100001", db_session, mock_column
        )
        
        # アサーション
        mock_column.in_.assert_called_once_with([6])
        mock_query_obj.filter.assert_called_once_with("filtered_condition")
        assert result == mock_filtered_query
    
    def test_filter_by_medical_permission_no_access(self, db_session, monkeypatch):
        """filter_by_medical_permission: アクセス権限なしユーザーは空結果テスト"""
        # モックユーザーを設定
        mock_user = Mock()
        mock_user.user_id = "200001"
        mock_user.user_name = "ディーラーユーザー"
        mock_user.entity_type = 2
        mock_user.entity_relation_id = 1
        
        def mock_query(*_):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = mock_user
            return query_mock
        
        monkeypatch.setattr(db_session, "query", mock_query)
        
        # モッククエリを作成
        mock_query_obj = Mock()
        mock_filtered_query = Mock()
        mock_query_obj.filter.return_value = mock_filtered_query
        
        mock_column = Mock()
        
        # テスト実行
        result = AuthManager.filter_by_medical_permission(
            mock_query_obj, "200001", db_session, mock_column
        )
        
        # アサーション（False条件でフィルタされることを確認）
        mock_query_obj.filter.assert_called_once_with(False)
        assert result == mock_filtered_query


if __name__ == "__main__":
    print("AuthManager認証・認可テストを実行します...")
    print("前提: テスト用ユーザーと医療機関が登録済みであること")
    pytest.main([__file__, "-v"])