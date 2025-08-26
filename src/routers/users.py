"""routers/users.py

ユーザー関連のAPIエンドポイント定義

Note:
    - 本モジュールは、ユーザー情報の取得、登録、更新、退会などのAPIエンドポイントを定義しています。
    - ユーザーの削除は論理削除（退会）として実装されており、物理削除は行いません。
    - FastAPIを使用しており、SQLAlchemy ORMを介してPostgreSQLデータベースと連携します。
    - 各エンドポイントは、Pydanticモデルを使用してリクエストとレスポンスのバリデーションを行います。

ChangeLog:
    v1.0.0 (2025-07-15)
    - 初版作成
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from ..database import SessionLocal
from src.models.pg_optigate.mst_user import MstUser
from src.schemas.mst_user import User, UserCreate, UserUpdate, UserInactive
from src.utils.password import generate_temp_password
from ..utils.auth import AuthManager

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_next_user_id(entity_type: int, db: Session) -> str:
    """
    entity_typeに応じたuser_idを生成する
    
    採番ルール:
    - システム: 900001 - 999999
    - 医療機関: 100001 - 199999
    - ディーラー: 200001 - 299999
    - メーカー: 300001 - 399999
    
    Args:
        entity_type (int): 組織種別 (1:医療機関, 2:ディーラー, 3:メーカー, 9:システム)
        db (Session): データベースセッション
        
    Returns:
        str: 生成されたuser_id
        
    Raises:
        ValueError: 未対応のentity_typeの場合
        HTTPException: 採番範囲が上限に達した場合
    """
    # entity_typeに応じた開始値と終了値を定義
    range_map = {
        1: (100001, 199999),  # 医療機関
        2: (200001, 299999),  # ディーラー
        3: (300001, 399999),  # メーカー
        9: (900001, 999999),  # システム
    }
    
    if entity_type not in range_map:
        raise ValueError(f"未対応のentity_type: {entity_type}")
    
    start_id, end_id = range_map[entity_type]
    
    # 該当範囲内での最大user_idを取得（CASTで数値に変換して比較）
    from sqlalchemy import cast, Integer
    max_user_id_str = db.query(func.max(MstUser.user_id)).filter(
        cast(MstUser.user_id, Integer) >= start_id,
        cast(MstUser.user_id, Integer) <= end_id
    ).scalar()
    
    # 初回の場合は開始値を返す
    if max_user_id_str is None:
        return str(start_id)
    
    # 次のIDを計算
    max_user_id = int(max_user_id_str)
    next_id = max_user_id + 1
    
    # 上限チェック
    if next_id > end_id:
        entity_name = {
            1: "医療機関",
            2: "ディーラー", 
            3: "メーカー",
            9: "システム"
        }.get(entity_type, "不明")
        raise HTTPException(
            status_code=400, 
            detail=f"{entity_name}のuser_id採番範囲が上限に達しました (最大: {end_id})"
        )
    
    return str(next_id)

@router.get("/", response_model=List[User])
def read_users(
    user_name: str | None = Query(None, description="ユーザー名でフィルタリング"),
    entity_type: int | None = Query(None, description="組織種別でフィルタリング"),
    entity_relation_id: int | None = Query(None, description="組織IDでフィルタリング"),
    e_mail: str | None = Query(None, description="メールアドレスでフィルタリング"),
    phone_number: str | None = Query(None, description="電話番号でフィルタリング"),
    mobile_number: str | None = Query(None, description="携帯番号でフィルタリング"),
    user_status: int | None = Query(None, description="ユーザーステータスでフィルタリング"),
    skip: int = Query(0, ge=0, description="スキップ件数（0以上）"),
    limit: int = Query(100, ge=1, le=100, description="1〜100件で指定"),
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)
    ):
    """
    Read Users

    [Japanese]\n
    ユーザー一覧取得（複数条件を任意に組み合わせ可能）

    検索例:
    - /users?user_name=セイエイ太郎
    - /users?entity_type=1&entity_relation_id=22
    - /users?e_mail=example@example.com
    - /users ← 全件取得

    件数の調整について:
    - 001～100件 : /users?skip=0&limit=100
    - 101～200件 : /users?skip=100&limit=100
    - さらに次のリクエストは、skipとlimitを調整して行います。
    - 例えば、次の100件を取得する場合は以下のようにします。
        - /users?skip=200&limit=100

    Args:
    - user_name (str, optional): ユーザー名でフィルタリング
    - entity_type (int, optional): 組織種別でフィルタリング
    - entity_relation_id (int, optional): 組織IDでフィルタリング
    - e_mail (str, optional): メールアドレスでフィルタリング
    - phone_number (str, optional): 電話番号でフィルタリング
    - mobile_number (str, optional): 携帯番号でフィルタリング
    - user_status (int, optional): ユーザーステータスでフィルタリング
    - skip (int, optional): スキップ件数（デフォルトは0）
    - limit (int, optional): 取得件数（デフォルトは100、最大100件）
    - db (Session, optional): SQLAlchemyのDBセッション。デフォルトは依存関係で取得

    Returns:
    - List[User]: ユーザー情報のリスト

    [English]\n
    Retrieve multiple user information (can combine multiple conditions)
    Search examples:
    - /users?user_name=SeieiTaro
    - /users?entity_type=1&entity_relation_id=22
    - /users?e_mail=example@example.com
    - /users ← Retrieve all records

    Adjusting the number of records:
    - 001-100 records: /users?skip=0&limit=100
    - 101-200 records: /users?skip=100&limit=100
    - For the next request, adjust skip and limit accordingly.
    - For example, to retrieve the next 100 records, use:
        - /users?skip=200&limit=100

    Args:
    - user_name (str, optional): Filter by user name
    - entity_type (int, optional): Filter by entity type
    - entity_relation_id (int, optional): Filter by entity relation ID
    - e_mail (str, optional): Filter by email address
    - phone_number (str, optional): Filter by phone number
    - mobile_number (str, optional): Filter by mobile number
    - user_status (int, optional): Filter by user status
    - skip (int, optional): Number of records to skip (default is 0)
    - limit (int, optional): Number of records to retrieve (default is 100, maximum 100 records)
    - db (Session, optional): SQLAlchemy database session, obtained via dependency injection

    Returns:
    - List[User]: List of user information
    """
    query = db.query(MstUser)
    
    # 医療機関アクセス権限に基づいてフィルタリング
    user_info = AuthManager.get_user_info(current_user_id, db)
    if not user_info.is_admin:
        # 医療機関ユーザーは自分の医療機関のユーザーのみ閲覧可能
        if user_info.entity_type == 1:
            query = query.filter(MstUser.entity_relation_id == user_info.entity_relation_id)
        else:
            # その他のユーザーはアクセス不可
            return []
    
    if user_name:
        query = query.filter(MstUser.user_name == user_name)
    if entity_type:
        query = query.filter(MstUser.entity_type == entity_type)
    if entity_relation_id:
        query = query.filter(MstUser.entity_relation_id == entity_relation_id)
    if e_mail:
        query = query.filter(MstUser.e_mail == e_mail)
    if phone_number:
        query = query.filter(MstUser.phone_number == phone_number)
    if mobile_number:
        query = query.filter(MstUser.mobile_number == mobile_number)
    if user_status:
        query = query.filter(MstUser.user_status == user_status)
    return query.offset(skip).limit(limit).all()

@router.get("/{user_id}", response_model=User)
def read_user(
        user_id: str = Path(..., description="ユーザーID"),
        current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
        db: Session = Depends(get_db)):
    """
    Read User by ID

    [Japanese]\n
    ユーザー個別取得

    - ユーザーIDで指定されたユーザー情報を取得します
    - ユーザーが存在しない場合は404エラーを返します

    Args:
    - user_id (str): ユーザーID
    - db (Session, optional): SQLAlchemyのDBセッション。デフォルトは依存関係で取得

    Returns:
    - User: ユーザー情報

    [English]\n
    Retrieve User by ID

    - Retrieves user information specified by user ID
    - Returns 404 error if the user does not exist

    Args:
    - user_id (str): User ID
    - db (Session, optional): SQLAlchemy database session, obtained via dependency injection

    Returns:
    - User: User information
    """
    user = db.query(MstUser).filter(MstUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # アクセス権限チェック
    current_user_info = AuthManager.get_user_info(current_user_id, db)
    if not current_user_info.is_admin:
        # 医療機関ユーザーは自分の医療機関のユーザーのみアクセス可能
        if current_user_info.entity_type == 1:
            if user.entity_relation_id != current_user_info.entity_relation_id:
                raise HTTPException(status_code=403, detail="指定されたユーザーへのアクセス権限がありません")
        else:
            raise HTTPException(status_code=403, detail="指定されたユーザーへのアクセス権限がありません")
    
    return user

@router.post("/", response_model=User)
def create_user(
    user: UserCreate = Body(..., description="ユーザー情報"),
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)):
    """
    Create a new user

    [Japanese]\n
    ユーザー新規登録

    - ユーザー情報を新規登録します (管理者権限が必要)

    Args:
    - user (UserCreate): 新規登録するユーザー情報
    - db (Session, optional): SQLAlchemyのDBセッション。デフォルトは依存関係で取得

    Returns:
    - User: 登録されたユーザー情報

    [English]\n
    Create a new user

    - Registers new user information (requires admin privileges)

    Args:
    - user (UserCreate): User information to register
    - db (Session, optional): SQLAlchemy database session, obtained via dependency injection

    Returns:
    - User: Registered user information
    """
    # 管理者権限チェック
    AuthManager.require_admin_permission(current_user_id, db)
    
    now = datetime.now()
    temp_password = generate_temp_password()  # 仮のパスワード生成

    # entity_typeに応じたuser_idを生成
    next_user_id = generate_next_user_id(user.entity_type, db)
    
    db_user = MstUser(
        user_id=next_user_id,
        **user.model_dump(),
        password=temp_password,
        user_status=0,  # 新規登録時は仮登録としてユーザーステータスを0に設定
        reg_user_id=current_user_id,
        regdate=now,
        update_user_id=current_user_id,
        lastupdate=now
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int = Path(..., description="ユーザーID"),
    user: UserUpdate = Body(..., description="更新するユーザー情報"),
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)):
    """
    Update an existing user

    [Japanese]\n
    既存ユーザー情報更新

    - ユーザーIDで指定されたユーザー情報を更新します
    - 管理者が作成した基本情報に、当人が必要な情報を更新します

    Args:
    - user_id (str): ユーザーID
    - user (UserUpdate): 更新するユーザー情報
    - db (Session, optional): SQLAlchemyのDBセッション。デフォルトは依存関係で取得

    Returns:
    - User: 更新されたユーザー情報

    [English]\n
    Update an existing user

    - Updates user information specified by user ID
    - The administrator creates basic information, and the user updates necessary information

    Args:
    - user_id (str): User ID
    - user (UserUpdate): User information to update
    - db (Session, optional): SQLAlchemy database session, obtained via dependency injection

    Returns:
    - User: Updated user information
    """
    db_user = db.query(MstUser).filter(MstUser.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = user.model_dump(exclude_unset=True)  # 更新するフィールドのみを取得
    for field, value in update_data.items():  # 取得したレコードに対して更新部分を反映
        setattr(db_user, field, value)
    db_user.user_status = 1  # 更新時はユーザーステータスを1に設定
    db_user.update_user_id = current_user_id
    db_user.lastupdate = datetime.now()  # 更新日時を現在時刻に設定
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/{user_id}/inactive", response_model=User)
def inactive_user(
    user_id: int = Path(..., description="ユーザーID"),
    reason: UserInactive = Body(..., description="無効化理由"),
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)):
    """
    Inactivate a user

    [Japanese]\n
    ユーザー無効化処理

    - ユーザーIDで指定されたユーザーを無効化します
    - 無効化処理としてユーザーステータスを9に設定し、その理由を登録します
    - 無効化理由は必須項目として、reason_codeとnoteを受け取ります
    - 無効化したユーザーはログイン出来なくなり、復活も出来ません

    Args:
    - user_id (str): ユーザーID
    - reason (UserInactive): 無効化理由（reason_codeとnoteを含む）
    - db (Session, optional): SQLAlchemyのDBセッション。デフォルトは依存関係で取得

    Returns:
    - User: 無効化されたユーザー情報

    [English]\n
    Inactivate a user

    - Inactivates the user specified by user ID
    - Sets the user status to 9 for inactivation and registers the reason
    - The inactivation reason is required and includes reason_code and note
    - Inactivated users cannot log in or be reactivated

    Args:
    - user_id (str): User ID
    - reason (UserInactive): Inactivation reason (includes reason_code and note)
    - db (Session, optional): SQLAlchemy database session, obtained via dependency injection

    Returns:
    - User: Inactivated user information
    """
    # 管理者権限チェック
    AuthManager.require_admin_permission(current_user_id, db)
    
    db_user = db.query(MstUser).filter(MstUser.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.user_status = 9  # 退会処理としてユーザーステータスを9に設定
    db_user.inactive_reason_code = reason.reason_code
    db_user.inactive_reason_note = reason.note
    db_user.update_user_id = current_user_id
    db_user.lastupdate = datetime.now()  # 更新日時を現在時刻に設定
    db.commit()
    db.refresh(db_user)
    return db_user

