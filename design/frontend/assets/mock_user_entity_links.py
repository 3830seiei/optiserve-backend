import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# ページ設定
st.set_page_config(
    page_title="組織連携管理",
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
    
    .info-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #ddd;
    }
    
    .warning-card {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 10px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    .success-card {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
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
st.markdown('<div class="main-header">組織連携管理</div>', unsafe_allow_html=True)

# サンプル組織連携データ生成
@st.cache_data
def generate_user_entity_data():
    users = []
    
    # 医療機関ユーザー
    medical_facilities = [
        "○○総合病院", "△△クリニック", "××医療センター", "◇◇病院", "☆☆診療所"
    ]
    
    # システム管理者ユーザー
    for i in range(900001, 900006):  # システム管理者
        users.append({
            "ユーザーID": i,
            "ユーザー名": f"システム管理者{i-900000}",
            "組織種別": "管理者権限",
            "組織名": "システム運営会社",
            "分析レベル": "小分類",
            "レポート出力数": 10,
            "通知先メール": f"admin{i-900000}@system.com",
            "連絡先電話": "03-1234-567" + str(i-900000),
            "最終ログイン": datetime.now() - timedelta(days=random.randint(0, 7)),
            "ステータス": "アクティブ"
        })
    
    # 医療機関ユーザー
    for facility_idx, facility in enumerate(medical_facilities):
        base_user_id = 100000 + facility_idx * 1000
        for user_idx in range(3):  # 各医療機関3ユーザー
            user_id = base_user_id + user_idx + 1
            users.append({
                "ユーザーID": user_id,
                "ユーザー名": f"{facility}_担当者{user_idx+1}",
                "組織種別": "医療機関",
                "組織名": facility,
                "分析レベル": random.choice(["大分類", "中分類", "小分類"]),
                "レポート出力数": random.randint(3, 8),
                "通知先メール": f"user{user_id}@{facility.replace('○○', 'hospital').replace('△△', 'clinic').replace('××', 'medical').replace('◇◇', 'hospital').replace('☆☆', 'clinic')}.jp",
                "連絡先電話": f"0{random.randint(1,9)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                "最終ログイン": datetime.now() - timedelta(days=random.randint(0, 30)),
                "ステータス": random.choice(["アクティブ", "利用停止", "仮登録"])
            })
    
    # ディーラー・メーカーユーザー（少数）
    for i in range(2):
        dealer_id = 200000 + i + 1
        users.append({
            "ユーザーID": dealer_id,
            "ユーザー名": f"医療機器ディーラー{i+1}",
            "組織種別": "ディーラー",
            "組織名": f"○○メディカル",
            "分析レベル": "中分類",
            "レポート出力数": 5,
            "通知先メール": f"dealer{i+1}@medical-dealer.co.jp",
            "連絡先電話": f"03-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
            "最終ログイン": datetime.now() - timedelta(days=random.randint(5, 20)),
            "ステータス": "アクティブ"
        })
        
        maker_id = 300000 + i + 1
        users.append({
            "ユーザーID": maker_id,
            "ユーザー名": f"医療機器メーカー{i+1}",
            "組織種別": "メーカー",
            "組織名": f"△△工業",
            "分析レベル": "大分類",
            "レポート出力数": 3,
            "通知先メール": f"maker{i+1}@medical-maker.co.jp",
            "連絡先電話": f"06-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
            "最終ログイン": datetime.now() - timedelta(days=random.randint(10, 60)),
            "ステータス": "アクティブ"
        })
    
    return pd.DataFrame(users)

# データ取得
user_entity_df = generate_user_entity_data()

# 検索・フィルタ部分
st.subheader("🔍 ユーザー検索・フィルタ")

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 2, 2, 1])

with filter_col1:
    st.write("**ユーザー名・組織名**")
    search_name = st.text_input("", placeholder="部分一致検索", key="search_user")

with filter_col2:
    st.write("**組織種別**")
    entity_types = ["すべて", "医療機関", "ディーラー", "メーカー", "管理者権限"]
    entity_filter = st.selectbox("", entity_types, key="entity_filter")

with filter_col3:
    st.write("**ステータス**")
    status_filter = st.selectbox("", ["すべて", "アクティブ", "利用停止", "仮登録"], key="status_filter")

with filter_col4:
    st.write("")
    search_button = st.button("🔍 検索", use_container_width=True)

# フィルタリング
filtered_df = user_entity_df.copy()

if search_name:
    filtered_df = filtered_df[
        filtered_df["ユーザー名"].str.contains(search_name, na=False) |
        filtered_df["組織名"].str.contains(search_name, na=False)
    ]

if entity_filter != "すべて":
    filtered_df = filtered_df[filtered_df["組織種別"] == entity_filter]

if status_filter != "すべて":
    filtered_df = filtered_df[filtered_df["ステータス"] == status_filter]

# メイン画面を2カラムレイアウト
col1, col2 = st.columns([2, 1])

with col1:
    # ユーザー一覧表示
    st.subheader("👥 組織連携ユーザー一覧")
    
    # 統計情報表示
    total_users = len(user_entity_df)
    active_users = len(user_entity_df[user_entity_df["ステータス"] == "アクティブ"])
    medical_users = len(user_entity_df[user_entity_df["組織種別"] == "医療機関"])
    
    st.info(f"📊 ユーザー統計: 全{total_users}名 (アクティブ: {active_users}名, 医療機関: {medical_users}名)")
    
    # ページネーション設定
    items_per_page = 15
    total_items = len(filtered_df)
    total_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1
    
    # ページ選択
    page_col1, page_col2, page_col3 = st.columns([1, 2, 1])
    with page_col2:
        current_page = st.selectbox(
            f"ページ (全{total_pages}ページ、{total_items}件)",
            range(1, total_pages + 1),
            key="page_selector"
        )
    
    # 現在のページのデータを取得
    start_idx = (current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_df = filtered_df.iloc[start_idx:end_idx]
    
    # セッションステートで選択行を管理
    if 'selected_user_index' not in st.session_state:
        st.session_state.selected_user_index = None
    
    # テーブル表示（行クリック選択）
    if not page_df.empty:
        # 表示用のデータフレーム作成
        display_df = page_df[["ユーザーID", "ユーザー名", "組織種別", "組織名", "ステータス"]].copy()
        
        event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="user_entity_table"
        )
        
        # 行が選択された場合
        if event['selection']['rows']:
            st.session_state.selected_user_index = event['selection']['rows'][0]
    else:
        st.info("検索条件に一致するユーザーがありません。")
    

with col2:
    # ユーザー詳細・編集フォーム
    st.subheader("✏️ 組織連携設定詳細")
    
    # 選択されたユーザーのデータを取得
    selected_user = None
    if st.session_state.selected_user_index is not None:
        try:
            selected_user = page_df.iloc[st.session_state.selected_user_index]
        except IndexError:
            st.session_state.selected_user_index = None
    
    if selected_user is not None:
        # ユーザー基本情報
        st.write("**ユーザー基本情報**")
        st.text_input("ユーザーID", value=str(selected_user["ユーザーID"]), disabled=True, key="user_id")
        st.text_input("ユーザー名", value=selected_user["ユーザー名"], disabled=True, key="user_name")
        
        # 組織情報
        st.write("")
        st.write("**組織情報**")
        
        entity_types = ["医療機関", "ディーラー", "メーカー", "管理者権限"]
        current_entity_type = selected_user["組織種別"]
        entity_type = st.selectbox("組織種別", entity_types, 
                                 index=entity_types.index(current_entity_type) if current_entity_type in entity_types else 0,
                                 key="entity_type")
        
        organization_name = st.text_input("組織名", value=selected_user["組織名"], key="org_name")
        
        # 分析設定
        st.write("")
        st.write("**分析設定**")
        
        analysis_levels = ["大分類", "中分類", "小分類"]
        current_level = selected_user["分析レベル"]
        analysis_level = st.selectbox("分析レベル", analysis_levels,
                                    index=analysis_levels.index(current_level) if current_level in analysis_levels else 2,
                                    key="analysis_level")
        
        report_count = st.number_input("レポート出力分類数", 
                                     min_value=1, max_value=10, 
                                     value=int(selected_user["レポート出力数"]),
                                     key="report_count")
        
        # 連絡先情報
        st.write("")
        st.write("**連絡先情報**")
        
        notification_email = st.text_area("通知先メール", value=selected_user["通知先メール"], key="notification_email", 
                                         help="複数のメールアドレスはカンマ区切りで入力してください（例：user1@example.com, user2@example.com）")
        contact_phone = st.text_input("連絡先電話", value=selected_user["連絡先電話"], key="contact_phone")
        
        # ステータス
        st.write("")
        st.write("**ステータス管理**")
        
        status_options = ["アクティブ", "利用停止", "仮登録"]
        current_status = selected_user["ステータス"]
        user_status = st.selectbox("ユーザーステータス", status_options,
                                 index=status_options.index(current_status) if current_status in status_options else 0,
                                 key="user_status")
        
        # 最終ログイン情報
        last_login = selected_user["最終ログイン"]
        st.info(f"**最終ログイン:** {last_login.strftime('%Y-%m-%d %H:%M')}")
        
        st.write("")
        # 更新ボタン
        if st.button("🔄 設定更新", use_container_width=True):
            if notification_email and "@" in notification_email:
                st.success("✅ 組織連携設定を更新しました")
                st.info(f"📝 変更履歴に記録: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            else:
                st.error("❌ 有効なメールアドレスを入力してください")
        
            
    else:
        st.info("ユーザーを選択してください")
        
        st.write("")
        st.write("**操作ガイド**")
        st.info("""
        **組織連携管理について:**
        
        👥 **複合主キー**: (user_id + entity_type)
        🏢 **組織種別**: 医療機関・ディーラー・メーカー・管理者
        📊 **分析レベル**: レポート出力の分類レベル設定
        📧 **通知機能**: ファイル処理完了時の自動通知
        
        **操作手順:**
        1. 左の一覧からユーザーを選択
        2. 組織情報・分析設定を確認・編集
        3. 連絡先情報を更新
        4. 「設定更新」で保存
        
        **注意事項:**
        - メールアドレスは通知送信に必須
        - 分析レベル変更時は機器分析設定の初期化が必要
        - ステータス変更は即座に反映
        """)

# 統計・サマリー部分
st.write("")
st.subheader("📈 組織連携統計")

stats_col1, stats_col2, stats_col3, stats_col4 = st.columns([1, 1, 1, 1])

with stats_col1:
    medical_active = len(user_entity_df[(user_entity_df["組織種別"] == "医療機関") & (user_entity_df["ステータス"] == "アクティブ")])
    medical_total = len(user_entity_df[user_entity_df["組織種別"] == "医療機関"])
    st.metric("医療機関ユーザー", f"{medical_active}/{medical_total}名")

with stats_col2:
    dealer_active = len(user_entity_df[(user_entity_df["組織種別"] == "ディーラー") & (user_entity_df["ステータス"] == "アクティブ")])
    dealer_total = len(user_entity_df[user_entity_df["組織種別"] == "ディーラー"])
    st.metric("ディーラーユーザー", f"{dealer_active}/{dealer_total}名")

with stats_col3:
    maker_active = len(user_entity_df[(user_entity_df["組織種別"] == "メーカー") & (user_entity_df["ステータス"] == "アクティブ")])
    maker_total = len(user_entity_df[user_entity_df["組織種別"] == "メーカー"])
    st.metric("メーカーユーザー", f"{maker_active}/{maker_total}名")

with stats_col4:
    admin_active = len(user_entity_df[(user_entity_df["組織種別"] == "管理者権限") & (user_entity_df["ステータス"] == "アクティブ")])
    admin_total = len(user_entity_df[user_entity_df["組織種別"] == "管理者権限"])
    st.metric("管理者", f"{admin_active}/{admin_total}名")

