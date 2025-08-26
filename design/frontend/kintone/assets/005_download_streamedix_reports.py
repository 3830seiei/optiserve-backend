import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

def random_download_datetime(base_date: str) -> str:
    base = datetime.strptime(base_date, "%Y-%m-%d")
    add_days = random.randint(0, 4)
    hour = random.randint(9, 20)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    dt = base + timedelta(days=add_days, hours=hour, minutes=minute, seconds=second)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

st.title("分析レポートダウンロード画面")

customer_name = "サンプル病院"  # 仮想の顧客名

# 過去6ヶ月分のダミーデータを作成
today = datetime.now()
report_list = []
for i in range(6):
    date_pub = (today.replace(day=15) - pd.DateOffset(months=i)).to_pydatetime()
    y, m = date_pub.year, date_pub.month
    report_list.append({
        "ファイル名": f"{customer_name}向け分析レポート_{y}年{m:02d}月版.pptx",
        "公開日": date_pub.strftime("%Y-%m-%d"),
        "取得者": customer_name,
        "取得日時": ""  # 最初は空欄
    })
report_df = pd.DataFrame(report_list)

# ダウンロード履歴をセッションで管理
if "download_history" not in st.session_state:
    st.session_state["download_history"] = {}

st.write(f"毎月15日ごろに、{customer_name}向けの最新分析レポートをダウンロードできます。")

st.subheader("公開済みレポート一覧（過去6ヶ月）")

# ヘッダーを明示
header_cols = st.columns([1.2, 3.5, 2, 2, 2])
with header_cols[0]:
    st.markdown("**ダウンロード**")
with header_cols[1]:
    st.markdown("**ファイル名**")
with header_cols[2]:
    st.markdown("**公開日**")
with header_cols[3]:
    st.markdown("**取得者**")
with header_cols[4]:
    st.markdown("**取得日時**")

# 表示用データを更新
display_df = report_df.copy()
for idx, row in display_df.iterrows():
    fname = row["ファイル名"]
    if fname in st.session_state["download_history"]:
        display_df.at[idx, "取得日時"] = st.session_state["download_history"][fname]

# 行ごとに横並び表示・折り返しなし
for i, row in display_df.iterrows():
    cols = st.columns([1.2, 3.5, 2, 2, 2])
    with cols[0]:
        if st.button("取得", key=f"dl_{i}"):
            # ダウンロード日時を記録
            pub_date = row["公開日"]
            st.session_state["download_history"][row["ファイル名"]] = random_download_datetime(pub_date)
            st.success(f"{row['ファイル名']}をダウンロードしました")
            st.experimental_rerun()
    with cols[1]:
        st.write(row["ファイル名"])
    with cols[2]:
        st.write(row["公開日"])
    with cols[3]:
        if i == 0:
            st.write("—")
        else:
            st.write(row["取得者"])
    with cols[4]:
        if i == 0:
            st.write("—")
        else:
            st.write(random_download_datetime(row["公開日"]))
