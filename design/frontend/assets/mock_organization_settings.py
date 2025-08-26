import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# ページ設定
st.set_page_config(
    page_title="組織設定管理",
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
st.markdown('<div class="main-header">組織設定管理</div>', unsafe_allow_html=True)

# サンプル組織データ生成（user_entity_link準拠）
@st.cache_data
def generate_organization_data():
    organizations = []
    
    # 医療機関データ（entity_type=1）
    medical_facilities = [
        "○○総合病院", "△△クリニック", "××医療センター", "◇◇病院", "☆☆診療所",
        "市立総合病院", "県立医療センター", "大学附属病院", "国立がんセンター", "こども病院"
    ]
    
    for i, facility in enumerate(medical_facilities):
        entity_relation_id = 100 + i  # 医療機関ID
        organizations.append({
            "組織種別": "医療機関",
            "entity_type": 1,
            "組織ID": entity_relation_id,
            "組織名": facility,
            "通知先メール": f"admin@{facility.replace('○○', 'hospital').replace('△△', 'clinic')}.jp, manager@{facility.replace('××', 'medical')}.jp",
            "レポート出力数": random.randint(5, 15),
            "分析レベル": random.choice(["大分類", "中分類", "小分類"]),
            "analiris_classification_level": random.choice([1, 2, 3]),
            "最終更新": datetime.now() - timedelta(days=random.randint(1, 30)),
            "更新者": f"admin{random.randint(1,3)}",
            "郵便番号": f"{random.randint(100,999)}-{random.randint(1000,9999)}",
            "都道府県": random.choice(["東京都", "大阪府", "愛知県", "神奈川県", "埼玉県", "千葉県", "福岡県"]),
            "市区町村": random.choice(["中央区", "港区", "新宿区", "渋谷区", "豊島区", "品川区", "世田谷区"]),
            "住所１": f"{random.randint(1,5)}-{random.randint(1,20)}-{random.randint(1,30)}",
            "住所２": random.choice(["", "2階", "3F", "A棟", "メディカルビル"]),
            "電話番号": f"0{random.randint(1,9)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        })
    
    # ディーラーデータ（entity_type=2）- 将来拡張用
    dealer_companies = ["○○メディカル", "△△医療機器", "××サプライ"]
    
    for i, company in enumerate(dealer_companies):
        entity_relation_id = 200 + i  # ディーラーID
        organizations.append({
            "組織種別": "ディーラー",
            "entity_type": 2,
            "組織ID": entity_relation_id,
            "組織名": company,
            "通知先メール": f"sales@{company.replace('○○', 'medical')}.co.jp",
            "レポート出力数": random.randint(3, 8),
            "分析レベル": random.choice(["大分類", "中分類"]),
            "analiris_classification_level": random.choice([1, 2]),
            "最終更新": datetime.now() - timedelta(days=random.randint(5, 60)),
            "更新者": f"system{random.randint(1,2)}",
            "郵便番号": f"{random.randint(100,999)}-{random.randint(1000,9999)}",
            "都道府県": random.choice(["東京都", "大阪府", "愛知県", "神奈川県", "埼玉県"]),
            "市区町村": random.choice(["千代田区", "中央区", "港区", "新宿区", "文京区"]),
            "住所１": f"{random.randint(1,3)}-{random.randint(1,15)}-{random.randint(1,25)}",
            "住所２": random.choice(["", "ビジネスタワー12F", "商業ビル5階", "オフィスプラザ8F"]),
            "電話番号": f"03-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        })
    
    # メーカーデータ（entity_type=3）- 将来拡張用
    maker_companies = ["△△工業", "××製作所"]
    
    for i, company in enumerate(maker_companies):
        entity_relation_id = 300 + i  # メーカーID
        organizations.append({
            "組織種別": "メーカー",
            "entity_type": 3,
            "組織ID": entity_relation_id,
            "組織名": company,
            "通知先メール": f"support@{company.replace('△△', 'tech')}.com",
            "レポート出力数": random.randint(2, 5),
            "分析レベル": "大分類",
            "analiris_classification_level": 1,
            "最終更新": datetime.now() - timedelta(days=random.randint(10, 90)),
            "更新者": f"admin{random.randint(1,2)}",
            "郵便番号": f"{random.randint(400,999)}-{random.randint(1000,9999)}",
            "都道府県": random.choice(["愛知県", "大阪府", "兵庫県", "静岡県", "群馬県"]),
            "市区町村": random.choice(["豊田市", "名古屋市中区", "大阪市淀川区", "神戸市中央区", "浜松市"]),
            "住所１": f"{random.randint(1,10)}-{random.randint(1,50)}-{random.randint(1,100)}",
            "住所２": random.choice(["", "工場棟", "本社ビル", "技術センター", "研究所"]),
            "電話番号": f"0{random.randint(1,9)}{random.randint(1,9)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
        })
        
    return pd.DataFrame(organizations)

# データ取得
org_df = generate_organization_data()

# 検索・フィルタ部分
st.subheader("🔍 組織検索・フィルタ")

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 2, 2, 1])

with filter_col1:
    st.write("**組織名**")
    search_name = st.text_input("", placeholder="部分一致検索", key="search_org")

with filter_col2:
    st.write("**組織種別**")
    entity_types = ["すべて", "医療機関", "ディーラー", "メーカー"]
    entity_filter = st.selectbox("", entity_types, key="entity_filter")

with filter_col3:
    st.write("**分析レベル**")
    level_filter = st.selectbox("", ["すべて", "大分類", "中分類", "小分類"], key="level_filter")

with filter_col4:
    st.write("")
    search_button = st.button("🔍 検索", use_container_width=True)

# フィルタリング
filtered_df = org_df.copy()

if search_name:
    filtered_df = filtered_df[filtered_df["組織名"].str.contains(search_name, na=False)]

if entity_filter != "すべて":
    filtered_df = filtered_df[filtered_df["組織種別"] == entity_filter]

if level_filter != "すべて":
    filtered_df = filtered_df[filtered_df["分析レベル"] == level_filter]

# メイン画面を2カラムレイアウト
col1, col2 = st.columns([2, 1])

with col1:
    # 組織一覧表示
    st.subheader("🏢 組織設定一覧")
    
    # 統計情報表示
    total_orgs = len(org_df)
    medical_count = len(org_df[org_df["組織種別"] == "医療機関"])
    dealer_count = len(org_df[org_df["組織種別"] == "ディーラー"])
    maker_count = len(org_df[org_df["組織種別"] == "メーカー"])
    
    st.info(f"📊 組織統計: 全{total_orgs}組織 (医療機関: {medical_count}, ディーラー: {dealer_count}, メーカー: {maker_count})")
    
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
    if 'selected_org_index' not in st.session_state:
        st.session_state.selected_org_index = None
    
    # テーブル表示（行クリック選択）
    if not page_df.empty:
        # 表示用のデータフレーム作成
        display_df = page_df[["組織種別", "組織ID", "組織名", "分析レベル", "レポート出力数"]].copy()
        
        event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="organization_table"
        )
        
        # 行が選択された場合
        if event['selection']['rows']:
            st.session_state.selected_org_index = event['selection']['rows'][0]
    else:
        st.info("検索条件に一致する組織がありません。")

with col2:
    # 組織詳細・編集フォーム
    st.subheader("✏️ 組織設定詳細")
    
    # 選択された組織のデータを取得
    selected_org = None
    if st.session_state.selected_org_index is not None:
        try:
            selected_org = page_df.iloc[st.session_state.selected_org_index]
        except IndexError:
            st.session_state.selected_org_index = None
    
    if selected_org is not None:
        # 組織基本情報
        st.write("**組織基本情報**")
        st.text_input("組織種別", value=selected_org["組織種別"], disabled=True, key="entity_type_display")
        st.text_input("組織ID", value=str(selected_org["組織ID"]), disabled=True, key="entity_id")
        st.text_input("組織名", value=selected_org["組織名"], key="org_name")
        
        # 住所情報
        st.write("")
        st.write("**住所情報**")
        
        address_col1, address_col2 = st.columns([1, 2])
        with address_col1:
            postal_code = st.text_input("郵便番号", value=selected_org["郵便番号"], key="postal_code")
        with address_col2:
            phone_number = st.text_input("電話番号", value=selected_org["電話番号"], key="phone_number")
        
        address_col3, address_col4 = st.columns([1, 1])
        with address_col3:
            prefecture = st.text_input("都道府県", value=selected_org["都道府県"], key="prefecture")
        with address_col4:
            city = st.text_input("市区町村", value=selected_org["市区町村"], key="city")
        
        address1 = st.text_input("住所１", value=selected_org["住所１"], key="address1")
        address2 = st.text_input("住所２", value=selected_org["住所２"], key="address2", help="建物名・階数等（任意）")
        
        # 分析設定
        st.write("")
        st.write("**分析・レポート設定**")
        
        # 分析レベル設定
        analysis_levels = ["大分類", "中分類", "小分類"]
        current_level = selected_org["分析レベル"]
        analysis_level = st.selectbox("分析分類レベル", analysis_levels,
                                    index=analysis_levels.index(current_level) if current_level in analysis_levels else 2,
                                    key="analysis_level",
                                    help="レポート生成時に使用する機器分類の詳細レベル")
        
        # レポート出力数設定
        report_count = st.number_input("レポート出力分類数", 
                                     min_value=1, max_value=20, 
                                     value=int(selected_org["レポート出力数"]),
                                     key="report_count",
                                     help="レポートに含める機器分類の最大数")
        
        # 通知設定
        st.write("")
        st.write("**通知設定**")
        
        notification_email = st.text_area("通知先メールアドレス", 
                                        value=selected_org["通知先メール"], 
                                        key="notification_email",
                                        help="複数のメールアドレスはカンマ区切りで入力してください",
                                        height=100)
        
        # 更新情報
        st.write("")
        st.write("**更新履歴**")
        st.info(f"""
        **最終更新:** {selected_org['最終更新'].strftime('%Y-%m-%d %H:%M')}  
        **更新者:** {selected_org['更新者']}
        """)
        
        st.write("")
        # 更新ボタン
        if st.button("🔄 設定更新", use_container_width=True):
            if notification_email and "@" in notification_email:
                st.success("✅ 組織設定を更新しました")
                st.info(f"📝 更新履歴に記録: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            else:
                st.error("❌ 有効なメールアドレスを入力してください")
        
    else:
        st.info("組織を選択してください")
        
        st.write("")
        st.write("**操作ガイド**")
        st.info("""
        **組織設定管理について:**
        
        🏢 **複合主キー**: entity_type + entity_relation_id
        📊 **管理対象**: 医療機関・ディーラー・メーカーの設定
        📧 **通知機能**: ファイル処理完了時の自動通知
        📈 **分析設定**: レポート生成の分類レベル設定
        
        **操作手順:**
        1. 左の一覧から組織を選択
        2. 分析レベル・レポート出力数を設定
        3. 通知先メールアドレスを更新
        4. 「設定更新」で保存
        
        **重要事項:**
        - 複数メールアドレスはカンマ区切り
        - 分析レベル変更時は機器分析設定の初期化が必要
        - 現在は医療機関のみサポート
        """)

# 統計・サマリー部分
st.write("")
st.subheader("📈 組織設定統計")

stats_col1, stats_col2, stats_col3, stats_col4 = st.columns([1, 1, 1, 1])

with stats_col1:
    medical_total = len(org_df[org_df["組織種別"] == "医療機関"])
    st.metric("医療機関", f"{medical_total}組織")

with stats_col2:
    dealer_total = len(org_df[org_df["組織種別"] == "ディーラー"])
    st.metric("ディーラー", f"{dealer_total}組織")

with stats_col3:
    maker_total = len(org_df[org_df["組織種別"] == "メーカー"])
    st.metric("メーカー", f"{maker_total}組織")

with stats_col4:
    avg_report_count = int(org_df["レポート出力数"].mean())
    st.metric("平均レポート出力数", f"{avg_report_count}分類")