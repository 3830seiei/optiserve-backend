import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# ページ設定
st.set_page_config(
    page_title="レポートダウンロード",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
        color: #333;
        border-bottom: 2px solid #ddd;
        padding-bottom: 20px;
    }
    
    .stButton > button {
        background-color: white;
        color: black;
        border: 2px solid #333;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #f0f0f0;
    }
    
    .download-item {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #ddd;
    }
    
    .report-available {
        background-color: #d4edda;
        border-color: #c3e6cb;
    }
    
    .report-unavailable {
        background-color: #f8d7da;
        border-color: #f5c6cb;
    }
    
    /* 右上のDeployボタンを非表示 */
    .stAppDeployButton {
        display: none !important;
    }
    
    /* ヘッダーのデプロイメニューを非表示 */
    [data-testid="stDecoration"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ヘッダー
st.markdown('<div class="main-header">レポートダウンロード</div>', unsafe_allow_html=True)

# サンプルレポート履歴データ生成
@st.cache_data
def generate_report_history():
    history = []
    report_types = ["分析レポート", "故障リスト", "未実績リスト"]
    
    for i in range(6):  # 直近6ヶ月分
        report_date = datetime.now() - timedelta(days=30*i)
        year_month = report_date.strftime("%Y-%m")
        
        for j, report_type in enumerate(report_types):
            file_size = f"{random.randint(500, 2000)}KB"
            download_count = random.randint(0, 8)
        
            history.append({
                "対象年月": year_month,
                "レポート種別": report_type,
                "ファイルサイズ": file_size,
                "DL回数": download_count,
                "最終DL日": (report_date - timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d") if download_count > 0 else "-"
            })
    
    return pd.DataFrame(history)

# データ取得
report_df = generate_report_history()

# メイン部分を2カラムレイアウト
col1, col2 = st.columns([1, 1])

with col1:
    # ダウンロード部分
    st.subheader("📥 月次レポートダウンロード")
    
    st.write("**対象年月選択**")
    available_months = ["2025-08", "2025-07", "2025-06", "2025-05", "2025-04", "2025-03"]
    selected_month = st.selectbox("", available_months, key="download_month")
    
    st.write("")
    st.write(f"**{selected_month} のレポート一覧**")
    
    # レポート1: 分析レポート
    st.markdown("""
    <div class="download-item report-available">
        <h4>📊 分析レポート（PDF形式）</h4>
        <p><strong>ファイル:</strong> analysis_report.pdf | <strong>サイズ:</strong> 1,250KB</p>
        <p><strong>内容:</strong> 機器稼働状況、故障傾向、改善提案等の総合分析</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📊 分析レポートDL", use_container_width=True, key="dl_analysis"):
        st.success("✅ analysis_report.pdf をダウンロードしました")
        st.info("📧 ダウンロード記録をDBに保存しました")
    
    st.write("")
    
    # レポート2: 故障リスト
    st.markdown("""
    <div class="download-item report-available">
        <h4>🔧 故障リスト（Excel形式）</h4>
        <p><strong>ファイル:</strong> failure_list.xlsx | <strong>サイズ:</strong> 890KB</p>
        <p><strong>内容:</strong> 期間中の故障機器一覧、対応状況、修理履歴</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔧 故障リストDL", use_container_width=True, key="dl_failure"):
        st.success("✅ failure_list.xlsx をダウンロードしました")
        st.info("📧 ダウンロード記録をDBに保存しました")
    
    st.write("")
    
    # レポート3: 未実績リスト
    st.markdown("""
    <div class="download-item report-available">
        <h4>📋 未実績リスト（Excel形式）</h4>
        <p><strong>ファイル:</strong> unachieved_list.xlsx | <strong>サイズ:</strong> 650KB</p>
        <p><strong>内容:</strong> 貸出実績がない機器、点検未実施機器一覧</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📋 未実績リストDL", use_container_width=True, key="dl_unachieved"):
        st.success("✅ unachieved_list.xlsx をダウンロードしました")
        st.info("📧 ダウンロード記録をDBに保存しました")

with col2:
    # ダウンロード履歴表示
    st.subheader("📊 ダウンロード履歴")
    
    st.write("**直近6ヶ月の利用状況**")
    
    # 履歴テーブル表示
    st.dataframe(
        report_df,
        use_container_width=True,
        hide_index=True
    )
    
    st.write("")
    st.write("**利用上の注意**")
    st.warning("""
    ⚠️ **重要:**
    - レポートは月初に自動生成
    - ダウンロード回数・日時を記録
    - レポート内容に関する問い合わせは管理者まで
    """)

