import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# ページ設定
st.set_page_config(
    page_title="ファイルアップロード",
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
    
    .upload-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 1px solid #ddd;
    }
    
    .history-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #ddd;
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
    
    .file-upload-area {
        border: 2px dashed #ccc;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
        background-color: #fafafa;
    }
    
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 10px;
        border-radius: 4px;
        margin: 10px 0;
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
st.markdown('<div class="main-header">ファイルアップロード</div>', unsafe_allow_html=True)

# サンプルアップロード履歴データ生成
@st.cache_data
def generate_upload_history():
    history = []
    for i in range(6):  # 直近6ヶ月分
        upload_date = datetime.now() - timedelta(days=30*i)
        if i < 3:  # 最近3回はアップロード済み
            status = "完了"
            files = ["○", "○", "○"]
        else:
            status = "未実施" if i == 3 else "完了"
            files = ["○", "○", "-"] if status == "未実施" else ["○", "○", "○"]
        
        history.append({
            "アップロード月": upload_date.strftime("%Y年%m月"),
            "実施日": upload_date.strftime("%Y-%m-%d") if status == "完了" else "-",
            "医療機器台帳": files[0],
            "貸出履歴": files[1],
            "故障履歴": files[2],
            "ステータス": status
        })
    
    return pd.DataFrame(history)

# データ取得
history_df = generate_upload_history()

# メイン部分を2カラムレイアウト
col1, col2 = st.columns([1, 1])

with col1:
    # アップロード部分
    st.subheader("📁 月次ファイルアップロード")
    
    st.write("**アップロード対象月**")
    upload_month = st.selectbox("", ["2025年08月", "2025年09月", "2025年10月"], key="upload_month")
    
    st.write("")
    st.write("**アップロードファイル**")
    
    # 医療機器台帳
    st.write("**1. 医療機器台帳** (file_type=1)")
    equipment_file = st.file_uploader("", type=['csv'], key="equipment_csv")
    if equipment_file:
        st.success(f"✓ {equipment_file.name} が選択されました")
    
    st.write("")
    
    # 貸出履歴
    st.write("**2. 貸出履歴** (file_type=2)")
    rental_file = st.file_uploader("", type=['csv'], key="rental_csv")
    if rental_file:
        st.success(f"✓ {rental_file.name} が選択されました")
    
    st.write("")
    
    # 故障履歴
    st.write("**3. 故障履歴** (file_type=3)")
    failure_file = st.file_uploader("", type=['csv'], key="failure_csv")
    if failure_file:
        st.success(f"✓ {failure_file.name} が選択されました")
    
    st.write("")
    
    # アップロードボタン
    upload_col1, upload_col2 = st.columns([1, 1])
    with upload_col1:
        if st.button("🚀 一括アップロード", use_container_width=True):
            if equipment_file and rental_file and failure_file:
                # アップロード処理の模擬
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(100):
                    progress_bar.progress(i + 1)
                    if i < 30:
                        status_text.text("医療機器台帳をアップロード中...")
                    elif i < 60:
                        status_text.text("貸出履歴をアップロード中...")
                    elif i < 90:
                        status_text.text("故障履歴をアップロード中...")
                    else:
                        status_text.text("処理完了中...")
                
                st.success("✅ アップロードが完了しました！\n通知メールを送信中...")
                
                # 履歴を更新（模擬）
                st.info("📧 通知送信完了: user_entity_link.notification_email_listのメンバーに送信されました")
            else:
                st.error("❌ 3つのファイルすべてを選択してください")
    
    with upload_col2:
        if st.button("🔄 ファイル選択リセット", use_container_width=True):
            st.rerun()

with col2:
    # アップロード履歴表示
    st.subheader("📊 アップロード履歴")
    
    st.write("**直近6ヶ月の実施状況**")
    
    # 履歴テーブル表示
    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )
    
    st.write("")
    st.write("**ファイル形式について**")
    st.info("""
    **CSV形式要件:**
    - 文字コード: UTF-8
    - 区切り文字: カンマ(,)
    - ヘッダー行: 必須
    
    **アップロード仕様:**
    - 同月の再アップロードは上書き保存
    - 3ファイル同時アップロード必須
    - 完了時は自動通知送信
    """)
    
    st.write("")
    st.write("**注意事項**")
    st.warning("""
    ⚠️ **重要:**
    - 毎月10日頃までの実施を推奨
    - ファイルサイズ制限: 各50MB以下
    - アップロード後のファイル修正は管理者へ連絡
    """)

