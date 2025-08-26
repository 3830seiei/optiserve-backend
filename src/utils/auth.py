"""
auth.py

認証・認可の共通機能

OptiServeの統一認証システム。
ユーザー権限の確認、医療機関アクセス権限のチェック等を提供。
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional, NamedTuple
from ..models.pg_optigate.mst_user import MstUser


class UserInfo(NamedTuple):
    """ユーザー情報"""
    user_id: str
    user_name: str
    entity_type: int
    entity_relation_id: int
    is_admin: bool


class AuthManager:
    """認証・認可管理クラス"""
    
    @staticmethod
    def get_user_info(user_id: str, db: Session) -> UserInfo:
        """
        ユーザー情報を取得
        
        Args:
            user_id: ユーザーID
            db: データベースセッション
            
        Returns:
            UserInfo: ユーザー情報
            
        Raises:
            HTTPException: ユーザーが存在しない場合
        """
        user = db.query(MstUser).filter(MstUser.user_id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail=f"ユーザーID {user_id} が存在しません"
            )
        
        is_admin = AuthManager.is_admin_user_id(user_id)
        
        return UserInfo(
            user_id=user.user_id,
            user_name=user.user_name,
            entity_type=user.entity_type,
            entity_relation_id=user.entity_relation_id,
            is_admin=is_admin
        )
    
    @staticmethod
    def is_admin_user_id(user_id: str) -> bool:
        """
        システム管理者かどうかを判定
        
        Args:
            user_id: ユーザーID
            
        Returns:
            bool: システム管理者の場合True
        """
        try:
            uid = int(user_id)
            return 900001 <= uid <= 999999
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_admin(user_info: UserInfo) -> bool:
        """
        システム管理者かどうかを判定
        
        Args:
            user_info: ユーザー情報
            
        Returns:
            bool: システム管理者の場合True
        """
        return user_info.entity_type == 9
    
    @staticmethod
    def get_user_medical_id(user_id: str, db: Session) -> Optional[int]:
        """
        ユーザーの医療機関IDを取得
        
        Args:
            user_id: ユーザーID
            db: データベースセッション
            
        Returns:
            int: 医療機関ID（医療機関ユーザーの場合）
            None: システム管理者の場合
            
        Raises:
            HTTPException: ユーザーが存在しない、または医療機関ユーザーでない場合
        """
        user_info = AuthManager.get_user_info(user_id, db)
        
        if user_info.is_admin:
            return None  # システム管理者は全医療機関にアクセス可能
        
        if user_info.entity_type == 1:
            return user_info.entity_relation_id  # 医療機関ID
        
        raise HTTPException(
            status_code=403,
            detail=f"医療機関ユーザーまたはシステム管理者である必要があります（entity_type={user_info.entity_type}）"
        )
    
    @staticmethod
    def check_medical_permission(user_id: str, target_medical_id: int, db: Session) -> bool:
        """
        医療機関データへのアクセス権限をチェック
        
        Args:
            user_id: ユーザーID
            target_medical_id: 対象の医療機関ID
            db: データベースセッション
            
        Returns:
            bool: アクセス権限がある場合True
        """
        try:
            user_info = AuthManager.get_user_info(user_id, db)
            
            # システム管理者は全医療機関にアクセス可能
            if user_info.is_admin:
                return True
            
            # 医療機関ユーザーは自分の医療機関のみアクセス可能
            if user_info.entity_type == 1:
                return user_info.entity_relation_id == target_medical_id
            
            return False
            
        except HTTPException:
            return False
    
    @staticmethod
    def require_medical_permission(user_id: str, target_medical_id: int, db: Session) -> None:
        """
        医療機関データへのアクセス権限を要求（権限がない場合は例外発生）
        
        Args:
            user_id: ユーザーID
            target_medical_id: 対象の医療機関ID
            db: データベースセッション
            
        Raises:
            HTTPException: アクセス権限がない場合
        """
        if not AuthManager.check_medical_permission(user_id, target_medical_id, db):
            raise HTTPException(
                status_code=403,
                detail=f"医療機関ID {target_medical_id} への操作権限がありません"
            )
    
    @staticmethod
    def require_admin_permission(user_id: str, db: Session) -> None:
        """
        システム管理者権限を要求（権限がない場合は例外発生）
        
        Args:
            user_id: ユーザーID
            db: データベースセッション
            
        Raises:
            HTTPException: システム管理者権限がない場合
        """
        user_info = AuthManager.get_user_info(user_id, db)
        
        if not user_info.is_admin:
            raise HTTPException(
                status_code=403,
                detail="システム管理者権限が必要です"
            )
    
    @staticmethod
    def get_accessible_medical_ids(user_id: str, db: Session) -> Optional[list[int]]:
        """
        ユーザーがアクセス可能な医療機関IDリストを取得
        
        Args:
            user_id: ユーザーID
            db: データベースセッション
            
        Returns:
            list[int]: アクセス可能な医療機関IDリスト
            None: システム管理者の場合（全医療機関にアクセス可能）
        """
        user_info = AuthManager.get_user_info(user_id, db)
        
        if user_info.is_admin:
            return None  # 全医療機関にアクセス可能
        
        if user_info.entity_type == 1:
            return [user_info.entity_relation_id]  # 自医療機関のみ
        
        return []  # アクセス権限なし
    
    @staticmethod
    def filter_by_medical_permission(
        query,
        user_id: str,
        db: Session,
        medical_id_column
    ):
        """
        ユーザーの医療機関アクセス権限に基づいてクエリをフィルタ
        
        Args:
            query: SQLAlchemyクエリオブジェクト
            user_id: ユーザーID
            db: データベースセッション
            medical_id_column: フィルタ対象のmedical_idカラム
            
        Returns:
            フィルタされたクエリオブジェクト
        """
        accessible_medical_ids = AuthManager.get_accessible_medical_ids(user_id, db)
        
        # システム管理者の場合はフィルタしない
        if accessible_medical_ids is None:
            return query
        
        # 医療機関ユーザーの場合は自医療機関のみ
        if accessible_medical_ids:
            return query.filter(medical_id_column.in_(accessible_medical_ids))
        
        # アクセス権限がない場合は空の結果
        return query.filter(False)


# 後方互換性のためのヘルパー関数
def get_user_medical_id(user_id: str, db: Session) -> Optional[int]:
    """
    後方互換性のためのヘルパー関数
    
    Args:
        user_id: ユーザーID
        db: データベースセッション
        
    Returns:
        int: 医療機関ID
    """
    return AuthManager.get_user_medical_id(user_id, db)


def get_current_user_id() -> str:
    """
    暫定的なユーザーID取得関数（本来はJWT等で実装）
    
    Returns:
        int: 現在のユーザーID
    """
    return "900001"  # 暫定値