import streamlit as st
import pandas as pd

st.set_page_config(page_title="機器分類候補メンテナンス", layout="centered")

# 選択機器分類データ
data_select_equipment_classification = [
    {"順位": 1, "機器分類ID": 3, "機器分類名": "内視鏡システム", "台数": 49},
    {"順位": 2, "機器分類ID": 9, "機器分類名": "パルスオキシメータ", "台数": 6},
    {"順位": 3, "機器分類ID": 8, "機器分類名": "電動式骨手術器械", "台数": 10},
    {"順位": 4, "機器分類ID": 1, "機器分類名": "除細動器", "台数": 62},
    {"順位": 5, "機器分類ID": 2, "機器分類名": "超音波診断装置", "台数": 51}
]

# 機器分類一覧（未選択）
data_unselected_equipment_classification = [
    {"機器分類ID": 4, "機器分類名": "人工呼吸器", "台数": 33},
    {"機器分類ID": 5, "機器分類名": "手術台", "台数": 14},
    {"機器分類ID": 6, "機器分類名": "分娩監視装置", "台数": 11},
    {"機器分類ID": 7, "機器分類名": "手術用顕微鏡", "台数": 11},
    {"機器分類ID": 10, "機器分類名": "輸液ポンプ", "台数": 9},
    {"機器分類ID": 11, "機器分類名": "心電計", "台数": 8},
    {"機器分類ID": 12, "機器分類名": "患者監視装置", "台数": 7},
    {"機器分類ID": 13, "機器分類名": "人工心肺装置", "台数": 6},
    {"機器分類ID": 14, "機器分類名": "内視鏡洗浄消毒器", "台数": 5},
    {"機器分類ID": 15, "機器分類名": "X線撮影装置", "台数": 5},
    {"機器分類ID": 16, "機器分類名": "手術灯", "台数": 4}
]

# タイトル
st.title("機器分類候補メンテナンス")

# レベル選択
level = st.selectbox("表示する分類レベル：", ["1（大）", "2（中）", "3（小）"], index=0)

# チェックボックス（デフォルト選択）
is_select_default = st.checkbox("保有台数の多い順に出力する", value=True)

# 選択機器分類一覧
st.subheader("選択機器分類（出力対象）")
df_selected = pd.DataFrame(data_select_equipment_classification)
df_displayed = df_selected[["機器分類ID", "機器分類名", "台数"]]
df_displayed.index = df_displayed.index + 1  # インデックスを1から始める
st.table(df_displayed)

# 操作ボタン（横並び）
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.button("選択")
with col2:
    st.button("↑ 順位を上げる")
with col3:
    st.button("↓ 順位を下げる")
with col4:
    st.button("選択解除")

# 機器分類一覧
st.subheader("機器分類一覧（未選択）")
df_unselected = pd.DataFrame(data_unselected_equipment_classification)
df_unselected = df_unselected[["機器分類ID", "機器分類名", "台数"]]
df_unselected.index = df_unselected.index + 1  # インデックスを1から始める
st.dataframe(df_unselected, height=300)

# 登録ボタン（横並び）
col5, col6, col7 = st.columns(3)
with col5:
    st.button("登録")
with col6:
    st.button("最初に戻す")
with col7:
    st.button("閉じる")
