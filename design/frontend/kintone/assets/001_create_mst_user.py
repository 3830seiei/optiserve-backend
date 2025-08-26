import streamlit as st
import re

# ----------------------------
# ユーティリティ関数
# ----------------------------
def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email)

# ----------------------------
# メイン画面
# ----------------------------
st.title("アカウントの仮登録")

st.markdown("SMDSの顧客をユーザーマスタに追加します。")

with st.form(key="account_form"):
    user_name = st.text_input("顧客名", max_chars=50)
    e_mail = st.text_input("メールアドレス")

    entity_type = st.selectbox("組織種別", options=["選択してください", "医療機関", "ディーラー", "メーカー"])
    entity_name = st.selectbox("組織名", options=["選択してください", "順天堂医院", "医療法人ABC", "東京ディーラー", "XYZメーカー"])

    col_btn1, col_btn2, col_empty = st.columns([1, 1, 4])  # ボタン用のカラムを作成
    with col_btn1:
        submitted = st.form_submit_button("登録")
    with col_btn2:
        cancel = st.form_submit_button("閉じる")

    # 登録処理
    if submitted:
        errors = []
        if not user_name:
            errors.append("顧客名を入力してください")
        if not e_mail or not is_valid_email(e_mail):
            errors.append("正しいメールアドレスを入力してください")
        if entity_type == "選択してください":
            errors.append("組織種別を選択してください")
        if entity_name == "選択してください":
            errors.append("組織名を選択してください")

        if errors:
            for e in errors:
                st.error(e)
        else:
            st.success("登録は正常に行なわれました。")
            # ここで本来はDB登録やAPI連携などの処理を実行
            st.json({
                "user_name": user_name,
                "e_mail": e_mail,
                "entity_type": entity_type,
                "entity_name": entity_name,
                "proc_type": 0  # 本登録待ち
            })

    elif cancel:
        st.warning("登録をキャンセルしました。")
