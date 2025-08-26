import streamlit as st
import re
import json

st.set_page_config(page_title="アカウントの基本情報登録", layout="wide")

st.title("アカウントの基本情報登録")

# ユーザー情報入力欄
with st.form("user_info_form", clear_on_submit=False):
    st.header("【ユーザー情報】")
    user_name = st.text_input("顧客名", max_chars=50, help="50文字以内")
    e_mail = st.text_input("メールアドレス")
    phone_number = st.text_input("連絡先電話番号", help="ハイフン付き 例: 03-1234-5678")
    mobile_number = st.text_input("携帯電話番号", help="ハイフン付き 例: 090-1234-5678")

    st.header("【組織情報】")
    #entity_type = st.selectbox("組織種別", ["医療機関", "ディーラー", "メーカー", "その他"])
    entity_name = st.text_input("組織名", max_chars=50, help="50文字以内")

    st.subheader("組織住所")
    col1, col2 = st.columns([1,2])
    with col1:
        entity_address_postal_code = st.text_input("郵便番号", max_chars=8, placeholder="例: 113-8431")
        entity_address_prefecture = st.text_input("都道府県")
        entity_address_city = st.text_input("市区町村")
    with col2:
        entity_address_line1 = st.text_input("町名・番地")
        entity_address_line2 = st.text_input("建物名等", placeholder="任意")

    entity_phone_number = st.text_input("代表電話番号", help="ハイフン付き 例: 03-3813-3111")

    st.subheader("レポート配布先E-Mail")
    # 複数メールアドレス（1行1メール想定で最大10件など）
    配布先_e_mail = st.text_area(
        "配布先E-Mail（1行1アドレスで複数行可・最大10件まで）",
        height=120,
        placeholder="例:\nuser1@example.com\nuser2@example.com"
    )

    # フォーム送信
    col_btn1, col_btn2, col_empty = st.columns([1, 1, 4])  # ボタン用のカラムを作成
    with col_btn1:
        submit = st.form_submit_button("登録")
    with col_btn2:
        close = st.form_submit_button("閉じる")

    # バリデーション用関数
    def is_valid_email(email):
        pattern = r"^[A-Za-z0-9._-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}$"
        return re.match(pattern, email)

    def is_valid_phone(phone, mobile=False):
        phone = phone.replace("-", "")
        if mobile:
            return re.match(r"^(070|080|090|020)\d{8}$", phone)
        else:
            return re.match(r"^0\d{9,10}$", phone) and not re.match(r"^(070|080|090|020)", phone)

    # 登録ボタン押下時のバリデーション
    if submit:
        errors = []
        # ユーザー名長さ
        if user_name and len(user_name) > 50:
            errors.append("ユーザー名は50文字以内で入力してください")
        # メール形式
        if e_mail and not is_valid_email(e_mail):
            errors.append("メールアドレスの形式が正しくありません")
        # 電話番号
        if phone_number and not is_valid_phone(phone_number):
            errors.append("連絡先電話番号の形式が正しくありません")
        if mobile_number and not is_valid_phone(mobile_number, mobile=True):
            errors.append("携帯電話番号の形式が正しくありません")
        # 電話番号・携帯どちらか必須
        if not phone_number and not mobile_number:
            errors.append("連絡先の電話番号、もしくは携帯番号のいずれかを入力してください")
        # 組織名長さ
        if entity_name and len(entity_name) > 50:
            errors.append("組織名は50文字以内で入力してください")
        # 住所バリデーション
        addr_inputs = [
            entity_address_postal_code, entity_address_prefecture,
            entity_address_city, entity_address_line1
        ]
        if any(addr_inputs) and not all(addr_inputs):
            errors.append("住所項目が不足しています。郵便番号から町名・番地までの入力を行なってください")
        # 郵便番号書式
        if entity_address_postal_code and not re.match(r"^\d{3}-\d{4}$", entity_address_postal_code):
            errors.append("郵便番号は999-9999形式で入力してください")
        # 配布先メールアドレス最大件数
        配布先_e_mail_list = [x.strip() for x in 配布先_e_mail.splitlines() if x.strip()]
        if len(配布先_e_mail_list) > 10:
            errors.append("配布先メールアドレスの登録件数は10件までです")
        # 配布先メールアドレス形式
        for mail in 配布先_e_mail_list:
            if not is_valid_email(mail):
                errors.append(f"配布先メールアドレス「{mail}」の形式が正しくありません")
        # 組織代表電話番号
        if entity_phone_number and not is_valid_phone(entity_phone_number):
            errors.append("代表電話番号の形式が正しくありません")

        # エラー表示 or 登録確認
        if errors:
            for err in errors:
                st.error(err)
        else:
            # ダイアログ風
            if st.confirm("更新します。よろしいですか？"):
                # 疑似登録処理
                st.success("登録は正常に行なわれました。")
            else:
                st.info("登録処理を中断しました。")

    # 閉じるボタン
    if close:
        if user_name or e_mail or phone_number or mobile_number or entity_name or 配布先_e_mail:
            if st.confirm("終了して良いですか？"):
                st.experimental_rerun()
            else:
                st.info("入力を続けてください")
        else:
            st.experimental_rerun()
