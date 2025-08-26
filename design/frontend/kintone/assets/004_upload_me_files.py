import streamlit as st
import pandas as pd
from datetime import datetime

st.title("ファイルアップロード画面")

st.write("機器台帳・貸出履歴・故障履歴のファイルのアップロードを行ないます。")
st.info("毎月10日までに、最新のファイルをアップロードしてください。")

# 5月・4月・3月分の履歴
dummy_history = [
    {
        "ファイル名": "kiki_ledger_202505.xlsx",
        "種別": "機器台帳",
        "アップロード日時": "2025-05-07 09:12:40"
    },
    {
        "ファイル名": "rental_202505.csv",
        "種別": "貸出履歴",
        "アップロード日時": "2025-05-07 09:14:20"
    },
    {
        "ファイル名": "fault_202505.xlsx",
        "種別": "故障履歴",
        "アップロード日時": "2025-05-07 09:25:12"
    },
    {
        "ファイル名": "kiki_ledger_202504.xlsx",
        "種別": "機器台帳",
        "アップロード日時": "2025-04-02 10:45:12"
    },
    {
        "ファイル名": "rental_202504.csv",
        "種別": "貸出履歴",
        "アップロード日時": "2025-04-02 10:47:00"
    },
    {
        "ファイル名": "fault_202504.xlsx",
        "種別": "故障履歴",
        "アップロード日時": "2025-04-02 10:49:45"
    }
]

#if "upload_history" not in st.session_state:
st.session_state["upload_history"] = dummy_history.copy()

# ファイル種別選択とアップロード
file_type = st.selectbox(
    "アップロードするファイル種別を選択してください",
    ["機器台帳", "貸出履歴", "故障履歴"]
)

uploaded_file = st.file_uploader(
    "ExcelまたはCSVファイルを選択してください",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file is not None:
    new_entry = {
        "ファイル名": uploaded_file.name,
        "種別": file_type,
        "アップロード日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state["upload_history"] = [new_entry] + st.session_state["upload_history"][:2]
    st.success(f"{file_type}のファイル「{uploaded_file.name}」をアップロードしました。")

# 履歴の表示
st.subheader("アップロード履歴（過去2ヶ月分）")
history_df = pd.DataFrame(st.session_state["upload_history"])
history_df.index = history_df.index + 1  # インデックスを1から始める
st.table(history_df)
