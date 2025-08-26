"""auth.py

OptiServeへのログインに関するスキーマ定義

ChangeLog:
    v1.0.0 (2025-07-14)
        - 初版作成
"""
from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    """ログインリクエスト（e-mailとパスワード）"""
    e_mail: EmailStr = Field(..., description="ログイン用メールアドレス")
    password: str = Field(..., description="パスワード")

class LoginResponse(BaseModel):
    """ログインレスポンス（成功・失敗）

    Args:
        BaseModel (_type_): _description_
    """
    success: bool
    user_id: str | None
    entity_type: int | None = Field(None, description="1: 医療機関, 2: ディーラー, 3: メーカー")
    entity_relation_id: int | None = Field(None, description="医療機関IDやディーラーIDなど")
    user_status: int | None = Field(None, description="0:仮登録, 1:本登録, 9:退会")
    next_action: str = Field(..., description="フロントでの推奨アクション"
                            "show_user_registration: 本登録画面へ, "
                            "show_main_menu: 通常メニューへ"
                            )
    message: str
