"""password.py

パスワード関連のユーティリティ関数

Note:
    - 本モジュールは、パスワードの生成やバリデーションを行うためのユーティリティ関数を定義しています。
    - パスワードのセキュリティ要件に基づいて、強力なパスワードを生成する機能を提供します。

ChangeLog:
    v1.0.0 (2025-07-15)
    - 初版作成
"""
import random
import string
import re

def generate_temp_password(length: int = 12) -> str:
    """
    一時パスワードを生成する関数

    Args:
        length (int, optional): パスワードの長さ. Defaults to 12.

    Returns:
        str: 生成された一時パスワード
    """
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(length))

def validate_password(password: str) -> str:
    """
    AWS運用推奨レベルのパスワードバリデーション

    - 8文字以上
    - 英大文字を含む
    - 英小文字を含む
    - 数字を含む
    - 記号を含む
    """
    if len(password) < 8:
        raise ValueError("パスワードは8文字以上で入力してください。")
    if not re.search(r'[A-Z]', password):
        raise ValueError("パスワードには英大文字を1文字以上含めてください。")
    if not re.search(r'[a-z]', password):
        raise ValueError("パスワードには英小文字を1文字以上含めてください。")
    if not re.search(r'\d', password):
        raise ValueError("パスワードには数字を1文字以上含めてください。")
    if not re.search(r'[^A-Za-z0-9]', password):
        raise ValueError("パスワードには記号（特殊文字）を1文字以上含めてください。")
    return password
