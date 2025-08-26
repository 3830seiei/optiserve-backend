"""
mst_userのバリデーションロジックを定義するモジュール

バリデーションチェックは簡単なチェックにとどめる。DB問合せ等はAPI側で行なうようにする。

Note:
    - FastAPIのルーティングで利用されるPydanticモデルのバリデーションを行います。
    - 各フィールドの型や制約を定義し、APIリクエストやレスポンスの整合性を保ちます。

ChangeLog:
    v1.0.0 (2025-07-14)
        - 初版作成
"""
import re

def validate_user_name(user_name: str) -> str:
    """ユーザー名のバリデーション

    Args:
        user_name (str): ユーザー名

    Returns:
        str: バリデーション済みのユーザー名

    Raises:
        ValueError: ユーザー名が空文字の場合
        ValueError: ユーザー名の長さが50文字を越える場合
    """
    if not user_name:
        raise ValueError("ユーザー名が空文字です。")
    if len(user_name) > 50:
        raise ValueError("ユーザー名は50文字を越えることはできません。")
    return user_name

def validate_entity_type(entity_type: int) -> int:
    """組織種別のバリデーション
    1: 医療機関, 2: ディーラー, 3: メーカー

    Args:
        entity_type (int): 組織種別

    Returns:
        int: バリデーション済みの組織種別

    Raises:
        ValueError: 組織種別が無効な場合
    """
    if entity_type not in [1, 2, 3]:
        raise ValueError("無効な組織種別です。")
    return entity_type

def validate_entity_relation_id(entity_relation_id: int) -> int:
    """組織IDのバリデーション

    Args:
        entity_relation_id (int): 組織ID

    Returns:
        int: バリデーション済みの組織ID

    Raises:
        ValueError: 0以下の値や負の値が指定された場合
    """
    if entity_relation_id <= 0:
        raise ValueError("組織IDは正の整数でなければなりません。")
    return entity_relation_id

def validate_phone_number(phone_number: str) -> str:
    """固定電話番号のバリデーション

    Args:
        phone_number (str): 固定電話番号

    Returns:
        str: バリデーション済みの固定電話番号

    Raises:
        ValueError: 正しい形式でない場合
    """
    # 電話番号の正規表現パターン
    # 例: 03-1234-5678, 045-678-9012 など
    # 市外局番は0から始まり、10桁または11桁の数字
    # ハイフン有無は許容（取り除いてチェック）
    number = re.sub(r'[-\s]', '', phone_number)
    # 固定電話（03, 04, 06等で始まる、10桁または11桁）
    if not re.match(r'^0\d{9,10}$', number):
        raise ValueError("正しい固定電話番号（市外局番含む10〜11桁）で入力してください。")
    return phone_number

def validate_mobile_number(phone_number: str) -> str:
    """携帯電話番号のバリデーション

    Args:
        phone_number (str): 携帯電話番号

    Returns:
        str: バリデーション済みの携帯電話番号

    Raises:
        ValueError: 正しい形式でない場合
    """
    # 携帯電話番号の正規表現パターン
    # 例: 070-1234-5678, 080-2345-6789 など
    # 070/080/090で始まり、11桁の数字
    # ハイフンやスペースは取り除いてチェック
    # 例: 070-1234-5678 -> 07012345678
    # ハイフン有無は許容
    number = re.sub(r'[-\s]', '', phone_number)
    # 携帯電話（070/080/090で始まる、11桁）
    if not re.match(r'^0[789]0\d{8}$', number):
        raise ValueError("正しい携帯電話番号（070/080/090で始まる11桁）で入力してください。")
    return phone_number

def validate_inactive_reason_code(user_status: int) -> int:
    """無効化理由コードのバリデーション

    Args:
        user_status (int): ユーザーステータス

    Returns:
        int: バリデーション済みのユーザーステータス

    Raises:
        ValueError: 無効なステータスが指定された場合
    """
    if user_status not in [1, 2, 3, 99]:
        raise ValueError("無効な無効化理由コードです。")
    return user_status

def validate_inactive_reason_note(note: str) -> str:
    """無効化理由の詳細のバリデーション

    Args:
        note (str): 無効化理由の詳細

    Returns:
        str: バリデーション済みの無効化理由の詳細

    Raises:
        ValueError: 長さが255文字を越える場合
    """
    if note and len(note) > 255:
        raise ValueError("無効化理由の詳細は255文字を越えることはできません。")
    return note
