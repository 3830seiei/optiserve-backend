"""routers/user_entity_links.py

ユーザー組織連携関連のAPIエンドポイント定義

Note:
    - 本モジュールは、ユーザーと組織（医療機関・ディーラー・メーカー）の連携情報の管理APIを定義しています。
    - 現在はentity_type=1（医療機関）のみサポートしています。
    - 連携情報の削除機能は意図的に提供されていません。
    - FastAPIを使用しており、SQLAlchemy ORMを介してPostgreSQLデータベースと連携します。
    - 各エンドポイントは、Pydanticモデルを使用してリクエストとレスポンスのバリデーションを行います。

ChangeLog:
    v1.0.0 (2025-08-07)
    - 初版作成
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List
import json
from ..database import SessionLocal
from src.models.pg_optigate.user_entity_link import UserEntityLink
from src.models.pg_optigate.mst_medical_facility import MstMedicalFacility
from src.schemas.user_entity_link import UserEntityLink as UserEntityLinkSchema, UserEntityLinkCreate
from ..utils.auth import AuthManager
from smds_core.logger import Logger

router = APIRouter(
    prefix="/api/v1/user-entity-links",
    tags=["user-entity-links"],
)

# シングルトンロガーの取得
logger = Logger()

def convert_email_list_for_db(email_list_str: str) -> list:
    """notification_email_listを文字列からDB用リスト形式に変換"""
    if isinstance(email_list_str, str):
        # 文字列の場合、リスト形式に変換
        if email_list_str.startswith('[') and email_list_str.endswith(']'):
            # すでにJSON文字列の場合
            try:
                json.loads(email_list_str)  # バリデーション
                return json.loads(email_list_str)
            except json.JSONDecodeError:
                # JSON形式でない場合は単一メールアドレスとしてリスト化
                return [email_list_str]
        else:
            # 単一メールアドレスの場合はリスト化
            return [email_list_str]
    return email_list_str  # 既にリストの場合はそのまま

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[UserEntityLinkSchema])
def read_user_entity_links(
    skip: int = 0, 
    limit: int = 100, 
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)):
    """
    Read User Entity Links

    [Japanese]
    ユーザーと組織の連携情報一覧取得

    - 全てのユーザー組織連携情報を取得します
    - skipとlimitパラメータでページネーション可能です
    - 1〜100件までの範囲で取得件数を指定できます

    例:
    - /user-entity-links ← 全件取得（最大100件）
    - /user-entity-links?skip=0&limit=50 ← 最初の50件
    - /user-entity-links?skip=50&limit=50 ← 次の50件

    Args:
    - skip (int, optional): スキップ件数（デフォルトは0）
    - limit (int, optional): 取得件数（デフォルトは100、最大100件）
    - db (Session, optional): SQLAlchemyのDBセッション。デフォルトは依存関係で取得

    Returns:
    - List[UserEntityLinkSchema]: ユーザー組織連携情報のリスト

    [English]
    Retrieve user entity link list

    - Retrieves all user-organization link information
    - Supports pagination with skip and limit parameters
    - Can specify the number of records to retrieve within the range of 1-100

    Examples:
    - /user-entity-links ← Retrieve all records (maximum 100 records)
    - /user-entity-links?skip=0&limit=50 ← First 50 records
    - /user-entity-links?skip=50&limit=50 ← Next 50 records

    Args:
    - skip (int, optional): Number of records to skip (default is 0)
    - limit (int, optional): Number of records to retrieve (default is 100, maximum 100 records)
    - db (Session, optional): SQLAlchemy database session, obtained via dependency injection

    Returns:
    - List[UserEntityLinkSchema]: List of user entity link information
    """
    # 医療機関アクセス権限に基づいてフィルタリング
    query = db.query(UserEntityLink)
    filtered_query = AuthManager.filter_by_medical_permission(
        query, current_user_id, db, UserEntityLink.entity_relation_id
    )
    return filtered_query.offset(skip).limit(limit).all()

@router.get("/{entity_type}/{entity_relation_id}", response_model=UserEntityLinkSchema)
def read_user_entity_link(
    entity_type: int, 
    entity_relation_id: int, 
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)):
    """
    Read User Entity Link by Composite Key

    [Japanese]
    ユーザー組織連携情報個別取得

    - 組織種別と組織IDで指定されたユーザー組織連携情報を取得します
    - 連携情報が存在しない場合は404エラーを返します

    例:
    - /user-entity-links/1/6 ← entity_type=1, entity_relation_id=6

    Args:
    - entity_type (int): 組織種別（1: 医療機関）
    - entity_relation_id (int): 組織ID
    - db (Session, optional): SQLAlchemyのDBセッション。デフォルトは依存関係で取得

    Returns:
    - UserEntityLinkSchema: ユーザー組織連携情報

    [English]
    Retrieve user entity link by composite key

    - Retrieves user-organization link information specified by entity type and relation ID
    - Returns 404 error if the link information does not exist

    Examples:
    - /user-entity-links/1/6 ← entity_type=1, entity_relation_id=6

    Args:
    - entity_type (int): Entity type (1: Medical facility)
    - entity_relation_id (int): Entity relation ID
    - db (Session, optional): SQLAlchemy database session, obtained via dependency injection

    Returns:
    - UserEntityLinkSchema: User entity link information
    """
    # 医療機関アクセス権限チェック
    AuthManager.require_medical_permission(current_user_id, entity_relation_id, db)
    
    link = db.query(UserEntityLink).filter(
        UserEntityLink.entity_type == entity_type,
        UserEntityLink.entity_relation_id == entity_relation_id
    ).first()
    if not link:
        raise HTTPException(
            status_code=404, 
            detail=f"User entity link not found: entity_type={entity_type}, entity_relation_id={entity_relation_id}"
        )
    return link

@router.post("/", response_model=UserEntityLinkSchema)
def create_user_entity_link(
    link: UserEntityLinkCreate,
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)):
    """
    Create a new user entity link

    [Japanese]
    ユーザー組織連携情報新規登録

    - 新しいユーザーと組織の連携情報を登録します（管理者権限が必要）
    - 組織種別は現在は医療機関（1）のみサポート
    - 必須フィールドのバリデーションを実行します
    - 組織IDの存在チェックを行います

    Args:
    - link (UserEntityLinkCreate): 新規登録するユーザー組織連携情報
    - db (Session, optional): SQLAlchemyのDBセッション。デフォルトは依存関係で取得

    Returns:
    - UserEntityLinkSchema: 登録されたユーザー組織連携情報

    [English]
    Create a new user entity link

    - Registers new user-organization link information (requires admin privileges)
    - Currently supports only medical facility (1) as organization type
    - Performs validation for required fields
    - Verifies the existence of organization ID

    Args:
    - link (UserEntityLinkCreate): User entity link information to register
    - db (Session, optional): SQLAlchemy database session, obtained via dependency injection

    Returns:
    - UserEntityLinkSchema: Registered user entity link information
    """
    try:
        # 管理者権限チェック
        AuthManager.require_admin_permission(current_user_id, db)
        
        logger.info(f"ユーザー組織連携作成開始: {link.entity_name}")
        
        # リクエストデータのログ出力
        link_data = link.model_dump()
        logger.debug(f"リクエストデータ: {link_data}")
        
        # entity_typeのチェック（1のみ許可）
        if link.entity_type != 1:
            raise HTTPException(
                status_code=400,
                detail="組織種別（entity_type）は1のみサポートしています（医療機関タイプ）"
            )

        # 必須フィールドのチェック
        if not link.entity_name or link.entity_name.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="組織名（entity_name）は必須です"
            )

        if not link.notification_email_list or link.notification_email_list.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="通知メールリスト（notification_email_list）は必須です"
            )

        if link.count_reportout_classification is None:
            raise HTTPException(
                status_code=400,
                detail="レポート公開分類数（count_reportout_classification）は必須です"
            )

        if link.analiris_classification_level is None:
            raise HTTPException(
                status_code=400,
                detail="分析レポート分類レベル（analiris_classification_level）は必須です"
            )

        # analiris_classification_levelの値チェック（1-3のみ有効）
        if link.analiris_classification_level not in [1, 2, 3]:
            raise HTTPException(
                status_code=400,
                detail="分析レポート分類レベル（analiris_classification_level）は1-3の値のみ有効です"
            )

        # entity_relation_idのチェック（医療機関マスタに存在するかチェック）
        medical_facility = db.query(MstMedicalFacility).filter(
            MstMedicalFacility.medical_id == link.entity_relation_id
        ).first()
        if not medical_facility:
            raise HTTPException(
                status_code=400,
                detail=f"医療機関ID（entity_relation_id） {link.entity_relation_id} は存在しません"
            )

        # DBオブジェクト作成
        logger.debug("DBオブジェクト作成開始")
        link_data = link.model_dump()
        
        # notification_email_listをDB用形式に変換
        link_data['notification_email_list'] = convert_email_list_for_db(link_data['notification_email_list'])
        
        now = datetime.now()
        db_link = UserEntityLink(**link_data)
        db_link.reg_user_id = current_user_id
        db_link.regdate = now
        db_link.update_user_id = current_user_id
        db_link.lastupdate = now
        logger.debug("DBオブジェクト作成完了")
        
        # DB保存処理
        logger.debug("DB保存処理開始")
        db.add(db_link)
        db.commit()
        logger.debug("DB保存処理完了")
        
        db.refresh(db_link)
        logger.info(f"ユーザー組織連携作成完了: entity_type={db_link.entity_type}, entity_relation_id={db_link.entity_relation_id}")
        
        return db_link
        
    except HTTPException:
        # HTTPExceptionはそのまま再発生
        raise
    except Exception as e:
        logger.error(f"ユーザー組織連携作成エラー: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/{entity_type}/{entity_relation_id}", response_model=UserEntityLinkSchema)
def update_user_entity_link(
    entity_type: int,
    entity_relation_id: int,
    link: UserEntityLinkCreate,
    current_user_id: str = Header(..., alias="X-User-Id", description="ログインユーザーのuser_id"),
    db: Session = Depends(get_db)):
    """
    Update an existing user entity link

    [Japanese]
    既存ユーザー組織連携情報更新

    - 組織種別と組織IDで指定されたユーザー組織連携情報を更新します
    - 組織種別は現在は医療機関（1）のみサポート
    - 必須フィールドのバリデーションを実行します
    - 組織IDの存在チェックを行います
    - 連携情報が存在しない場合は404エラーを返します

    例:
    - PUT /user-entity-links/1/6 ← entity_type=1, entity_relation_id=6

    Args:
    - entity_type (int): 組織種別（1: 医療機関）
    - entity_relation_id (int): 組織ID
    - link (UserEntityLinkCreate): 更新するユーザー組織連携情報
    - db (Session, optional): SQLAlchemyのDBセッション。デフォルトは依存関係で取得

    Returns:
    - UserEntityLinkSchema: 更新されたユーザー組織連携情報

    [English]
    Update an existing user entity link

    - Updates user-organization link information specified by entity type and relation ID
    - Currently supports only medical facility (1) as organization type
    - Performs validation for required fields
    - Verifies the existence of organization ID
    - Returns 404 error if the link information does not exist

    Examples:
    - PUT /user-entity-links/1/6 ← entity_type=1, entity_relation_id=6

    Args:
    - entity_type (int): Entity type (1: Medical facility)
    - entity_relation_id (int): Entity relation ID
    - link (UserEntityLinkCreate): User entity link information to update
    - db (Session, optional): SQLAlchemy database session, obtained via dependency injection

    Returns:
    - UserEntityLinkSchema: Updated user entity link information
    """
    # 医療機関アクセス権限チェック
    AuthManager.require_medical_permission(current_user_id, entity_relation_id, db)
    
    db_link = db.query(UserEntityLink).filter(
        UserEntityLink.entity_type == entity_type,
        UserEntityLink.entity_relation_id == entity_relation_id
    ).first()
    if not db_link:
        raise HTTPException(
            status_code=404, 
            detail=f"User entity link not found: entity_type={entity_type}, entity_relation_id={entity_relation_id}"
        )

    # entity_typeのチェック（1のみ許可）
    if link.entity_type != 1:
        raise HTTPException(
            status_code=400,
            detail="組織種別（entity_type）は1のみサポートしています（医療機関タイプ）"
        )

    # 必須フィールドのチェック
    if not link.entity_name or link.entity_name.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="組織名（entity_name）は必須です"
        )

    if not link.notification_email_list or link.notification_email_list.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="通知メールリスト（notification_email_list）は必須です"
        )

    if link.count_reportout_classification is None:
        raise HTTPException(
            status_code=400,
            detail="レポート公開分類数（count_reportout_classification）は必須です"
        )

    if link.analiris_classification_level is None:
        raise HTTPException(
            status_code=400,
            detail="分析レポート分類レベル（analiris_classification_level）は必須です"
        )

    # analiris_classification_levelの値チェック（1-3のみ有効）
    if link.analiris_classification_level not in [1, 2, 3]:
        raise HTTPException(
            status_code=400,
            detail="分析レポート分類レベル（analiris_classification_level）は1-3の値のみ有効です"
        )

    # entity_relation_idのチェック（医療機関マスタに存在するかチェック）
    medical_facility = db.query(MstMedicalFacility).filter(
        MstMedicalFacility.medical_id == link.entity_relation_id
    ).first()
    if not medical_facility:
        raise HTTPException(
            status_code=400,
            detail=f"医療機関ID（entity_relation_id） {link.entity_relation_id} は存在しません"
        )

    # 更新データの準備
    update_data = link.model_dump()
    # notification_email_listをDB用形式に変換
    update_data['notification_email_list'] = convert_email_list_for_db(update_data['notification_email_list'])
    
    # フィールドレベル制限: 医療機関ユーザーは特定フィールドを変更不可
    current_user_info = AuthManager.get_user_info(current_user_id, db)
    if not current_user_info.is_admin:
        # 医療機関ユーザーはcount_reportout_classificationとanaliris_classification_levelを変更不可
        restricted_fields = ['count_reportout_classification', 'analiris_classification_level']
        for field in restricted_fields:
            if field in update_data and update_data[field] != getattr(db_link, field):
                raise HTTPException(
                    status_code=403,
                    detail=f"医療機関ユーザーは{field}フィールドを変更できません（管理者権限が必要）"
                )
    
    for field, value in update_data.items():
        setattr(db_link, field, value)
    db_link.update_user_id = current_user_id
    db_link.lastupdate = datetime.now()
    db.commit()
    db.refresh(db_link)
    return db_link

# API経由での削除処理は行わないのでコメントアウト
#@router.delete("/{link_id}")
#def delete_user_entity_link(link_id: int, db: Session = Depends(get_db)):
#    """
#    ユーザーとエンティティの紐付け情報削除
#    """
#    db_link = db.query(UserEntityLink).filter(UserEntityLink.id == link_id).first()
#    if not db_link:
#        raise HTTPException(status_code=404, detail="User entity link not found")
#    db.delete(db_link)
#    db.commit()
#    return {"result": "ok"}
