""" schemas/mst_user.py

ユーザーマスタ情報の Pydantic スキーマ定義

Note:
    - 本モジュールは、FastAPIと連携して利用するためのPydanticモデル定義です。
    - PydanticはPythonの型ヒントとバリデーション機能を備えたデータモデリングライブラリです。
    - 主に以下の役割を担います。
        - APIリクエストやレスポンスの型安全性・自動バリデーション
        - 型ヒントやdescriptionを活用したAPIドキュメント（Swagger UI）の自動生成
        - SQLAlchemy等のORMモデルとの柔軟な相互変換
    - Configクラスについて (Pydanticのお作法):
        - Pydanticモデル（BaseModel継承クラス）のふるまい・変換ルール・互換性設定をまとめて指定できる“特別な内部クラス”
            - routers側のロジックのreturn時にDBモデルをそのまま返すときに、Pydanticモデルに変換するために必要
            - authのログイン時のような特例は除くとしても、基本的なAPIレスポンスはPydanticモデルを返すことが多いので、とりあえずConfigクラスを定義しておく
        - orm_mode = True -> 「SQLAlchemyモデルとPydanticモデルを簡単に変換したい時」に必須
            「SQLAlchemyなどのORM（オブジェクト・リレーショナル・マッピング）モデルのインスタンスからPydanticモデルへの自動変換を許可する」設定
            これが無いと、Pydanticは「dict（辞書型）」からしか変換できない
            これが有ると、FastAPIのレスポンスとして「SQLAlchemyのレコードインスタンス」→「Pydanticモデル」への変換が自動で行われる
            現場では「DBモデルの値をそのままPydanticで返す」場合は必ずorm_mode = Trueをつける
        - allow_population_by_field_name = True -> 「APIやDBのキー名とPython属性名が違う場合」に便利
            「エイリアス名（alias）ではなく、Pydanticモデル上の“フィールド名”でも値のセットや辞書変換ができるようにする」
            たとえば e_mail など、DBやAPIのキー名とPythonの変数名が異なる場合に有効
            これを有効にしておくと、.dict(by_alias=True)/.dict(by_alias=False) どちらも使いやすい
        - その他の設定(詳細はPydanticのドキュメントを参照):
            - json_encoders：日付やカスタム型をどう変換するか定義
            - anystr_strip_whitespace = True：文字列の前後の空白を自動で削除
            - validate_assignment = True：属性値の再代入時にもバリデーションを行う
            - extra = "forbid"：未定義フィールドを許可しない

ChangeLog:
    v1.0.0 (2025-07-14)
    - 初版作成
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from src.validators.mst_user import (
    validate_user_name,
    validate_entity_type,
    validate_entity_relation_id,
    validate_phone_number,
    validate_mobile_number,
    validate_inactive_reason_code,
    validate_inactive_reason_note
)
from src.utils.password import validate_password

class UserCreate(BaseModel):
    """ユーザー新規登録用モデル"""
    user_name: str = Field(..., description="ユーザー名")
    entity_type: int = Field(..., description="組織種別")
    entity_relation_id: int = Field(..., description="組織ID")
    e_mail: EmailStr = Field(..., description="メールアドレス")  # PydanticのEmailStrを使用してメールアドレスのバリデーションを行う
    mobile_number: Optional[str] = Field(None, description="携帯番号")

    @field_validator('user_name')
    def validate_user_name(cls, v):
        return validate_user_name(v)

    @field_validator('entity_type')
    def validate_entity_type(cls, v):
        return validate_entity_type(v)

    @field_validator('entity_relation_id')
    def validate_entity_relation_id(cls, v):
        return validate_entity_relation_id(v)

    class Config:
        from_attributes = True      # 旧: orm_mode
        validate_by_name = True     # 旧: allow_population_by_field_name

class UserUpdate(BaseModel):
    """ユーザー更新用モデル"""
    user_name: Optional[str] = Field(None, description="ユーザー名")
    e_mail: Optional[EmailStr] = Field(None, description="メールアドレス")
    password: Optional[str] = Field(None, description="ハッシュ化パスワード")
    phone_number: Optional[str] = Field(None, description="電話番号")
    mobile_number: Optional[str] = Field(None, description="携帯番号")

    @field_validator('user_name')
    def validate_user_name(cls, v):
        return validate_user_name(v)

    @field_validator('password')
    def validate_password(cls, v):
        return validate_password(v)

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        return validate_phone_number(v)

    @field_validator('mobile_number')
    def validate_mobile_number(cls, v):
        return validate_mobile_number(v)

    class Config:
        from_attributes = True      # 旧: orm_mode
        validate_by_name = True     # 旧: allow_population_by_field_name

class UserInactive(BaseModel):
    """ユーザー退会用モデル"""
    reason_code: int = Field(..., description="退会理由コード")
    note: Optional[str] = Field(None, description="退会理由の詳細")

    @field_validator('reason_code')
    def validate_inactive_reason_code(cls, v):
        return validate_inactive_reason_code(v)

    @field_validator('note')
    def validate_inactive_reason_note(cls, v):
        return validate_inactive_reason_note(v)

    class Config:
        from_attributes = True      # 旧: orm_mode
        validate_by_name = True     # 旧: allow_population_by_field_name

class User(BaseModel):
    """取得/返却用モデル"""
    user_id: str = Field(..., description="ユーザーID")
    user_name: str = Field(..., description="ユーザー名")
    entity_type: int = Field(..., description="組織種別")
    entity_relation_id: int = Field(..., description="組織ID")
    password: Optional[str] = Field(None, description="ハッシュ化パスワード")
    e_mail: EmailStr = Field(..., description="メールアドレス")
    phone_number: Optional[str] = Field(None, description="電話番号")
    mobile_number: Optional[str] = Field(None, description="携帯番号")
    user_status: int = Field(..., description="ユーザーステータス")
    inactive_reason_code: Optional[int] = Field(None, description="退会理由コード")
    inactive_reason_note: Optional[str] = Field(None, description="退会理由の詳細")
    regdate: datetime = Field(..., description="登録日時")
    lastupdate: datetime = Field(..., description="最終更新日時")

    class Config:
        from_attributes = True      # 旧: orm_mode
        validate_by_name = True     # 旧: allow_population_by_field_name
