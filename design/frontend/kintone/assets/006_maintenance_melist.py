import streamlit as st
import pandas as pd

# データ読み込み
df = pd.read_csv('./design/assets/006_sample_tbl_hospital_me_list.csv')

if 'is_used_in_analysis' not in df.columns:
    df['is_used_in_analysis'] = False

display_columns = [
    ("is_used_in_analysis", "集計対象"),
    ("grp_user", "利用部門"),
    ("me_number", "機器番号"),
    ("product_name", "製品名"),
    ("model_number", "モデル番号"),
    ("serial_number", "シリアル番号"),
    ("maker_name", "メーカー名"),
    ("date_stocked", "納入日"),
    ("date_expiration", "使用期限"),
]

st.title("機器台帳メンテナンス")
st.write("機器台帳のメンテナンスを行います。")
st.write("集計対象にする機器を選択し、登録ボタンを押してください。チェックを外すと集計対象から外れます。")
search_key = st.text_input("検索キー", "")
if search_key:
    mask = df.apply(lambda row: search_key in str(row.values), axis=1)
    filtered_df = df[mask]
else:
    filtered_df = df.copy()

page_size = 10
if "page_num" not in st.session_state:
    st.session_state.page_num = 1
total_pages = (len(filtered_df) - 1) // page_size + 1

col_btn = st.columns([2, 6, 2])
with col_btn[0]:
    if st.button("前ページ", disabled=(st.session_state.page_num == 1)):
        st.session_state.page_num -= 1
with col_btn[2]:
    if st.button("次ページ", disabled=(st.session_state.page_num == total_pages)):
        st.session_state.page_num += 1

page_num = st.session_state.page_num
start_idx = (page_num - 1) * page_size
end_idx = start_idx + page_size
page_df = filtered_df.iloc[start_idx:end_idx].copy()

st.write(f"ページ {page_num} / {total_pages}　（全{len(filtered_df)}件）")

# 編集フラグ
if "edit_flags" not in st.session_state or len(st.session_state.edit_flags) != len(page_df):
    st.session_state.edit_flags = page_df["is_used_in_analysis"].tolist()

# --- ヘッダー表示 ---
header_labels = [col[1] for col in display_columns]
st.markdown(
    "<div style='display: flex; gap:8px; font-weight:bold; background:#f4f4f4; padding:6px 0;'>"
    + "".join([f"<div style='width:110px'>{label}</div>" for label in header_labels])
    + "</div>",
    unsafe_allow_html=True
)

# --- 各行（明細） ---
for i, row in page_df.iterrows():
    cols = st.columns([1, 2, 2, 3, 2, 2, 2, 2, 2])
    cb_val = cols[0].checkbox("", value=st.session_state.edit_flags[i - start_idx], key=f"chk_{i}")
    st.session_state.edit_flags[i - start_idx] = cb_val
    for j, (col_id, _) in enumerate(display_columns[1:]):
        cols[j+1].write(row[col_id])

# ボタン群
col_btn2 = st.columns([2, 3, 2, 3])
with col_btn2[0]:
    if st.button("登録"):
        filtered_idx = page_df.index
        df.loc[filtered_idx, "is_used_in_analysis"] = st.session_state.edit_flags
        st.success("更新しました")
with col_btn2[1]:
    if st.button("変更前に戻す"):
        st.session_state.edit_flags = page_df["is_used_in_analysis"].tolist()
        st.info("変更を元に戻しました")
with col_btn2[2]:
    if st.button("閉じる"):
        st.info("画面を閉じます（デモ）")


