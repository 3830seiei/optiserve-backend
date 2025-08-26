"""routers/auth.py

OptiServe Login API Router

ChangeLog:
    v1.0.0 (2025-07-16)
        - Initial version
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from ..database import SessionLocal
from src.models.pg_optigate.mst_user import MstUser
from src.schemas.auth import LoginRequest, LoginResponse

# error messages
ERROR_INVALID_CREDENTIALS = "メールアドレス、またはパスワードが間違っています"

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest = Body(...,description="ログイン情報（メールアドレス、パスワード）"),
    db: Session = Depends(get_db)):
    """
    Login

    [Japanese]\n
    ログイン認証API（メールアドレスとパスワードでユーザー認証を行います）

    - メールアドレス（email）とパスワード（password）でログイン処理を実施
    - 認証成功時はユーザーID、組織種別、組織ID、状態（user_status）などを返却
    - 認証失敗時は success=False, message にエラー理由を返します
    - user_status が 0（仮登録）の場合は next_action="show_user_registration" を返し、本登録を促します
    - 本登録済みなら next_action="show_main_menu" を返します

    Args:
    - request (LoginRequest): ログインリクエスト（メールアドレスとパスワード）
    - db (Session, optional): SQLAlchemyのDBセッション。デフォルトは依存関係で取得

    Returns:
    - LoginResponse : ログイン結果（success, user_id, next_action, message など）

    [English]\n
    Login authentication API (Authenticate user by email and password)

    Note:
    - Login process is performed using email (email) and password (password)
    - On successful authentication, returns user ID, entity type, entity relation ID, and user_status
    - On authentication failure, returns success=False and an error message in message
    - If user_status is 0 (temporary registration), returns next_action="show_user_registration" to prompt for full registration
    - If fully registered, returns next_action="show_main_menu"

    Args:
    - request (LoginRequest): Login request containing email and password
    - db (Session, optional): SQLAlchemy database session, obtained via dependency injection

    Returns:
    - LoginResponse : Login result containing success, user_id, next_action, message, etc

    """
    mstuser = db.query(MstUser).filter(MstUser.e_mail == request.e_mail).first()
    if not mstuser:
        return LoginResponse(success=False, user_id=None,
                            entity_type=None, entity_relation_id=None,
                            user_status=None, next_action="none", message=ERROR_INVALID_CREDENTIALS)
    if str(mstuser.password) != request.password:  # ORMのカラムはSQL式のインスタンスなので、str()で文字列に変換
        return LoginResponse(success=False, user_id=None,
                            entity_type=None, entity_relation_id=None,
                            user_status=None, next_action="none", message=ERROR_INVALID_CREDENTIALS)

    # user_statusの状態でnext_actionを決める
    if mstuser.user_status == 0:
        next_action = "show_user_registration"  # フロントで「本登録画面」へ
        message = "仮登録状態です。本登録を完了してください。"
    elif mstuser.user_status == 9:
        # 利用停止ユーザーはログイン拒否
        return LoginResponse(success=False, user_id=None,
                            entity_type=None, entity_relation_id=None,
                            user_status=None, next_action="none", message="対象のユーザーは利用できません。")
    else:
        next_action = "show_main_menu"  # フロントで通常メニューへ
        message = "ログイン成功"

    return LoginResponse(
        success=True,
        user_id=str(mstuser.user_id),
        entity_type=int(mstuser.entity_type),
        entity_relation_id=int(mstuser.entity_relation_id),
        user_status=int(mstuser.user_status),
        next_action=next_action,
        message=message,
    )
