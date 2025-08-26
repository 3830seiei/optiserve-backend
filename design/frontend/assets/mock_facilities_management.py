import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# ページ設定
st.set_page_config(
    page_title="医療機関マスタ　メンテナンス",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# カスタムCSS（既存モックと同様のスタイル）
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
    
    .search-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 1px solid #ddd;
    }
    
    .form-container {
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
    
    .required {
        color: red;
    }
    
    .table-container {
        border: 2px solid #333;
        border-radius: 8px;
        overflow: hidden;
        margin: 20px 0;
    }
    
    /* Streamlitの不要ラベル非表示 */
    .stTextInput > label[data-testid="stWidgetLabel"],
    .stSelectbox > label[data-testid="stWidgetLabel"] {
        display: none !important;
    }
    
    /* 2カラムレイアウトの自動生成ラベル非表示 */
    .stColumn > label[data-testid="stWidgetLabel"] {
        display: none !important;
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
st.markdown('<div class="main-header">医療機関マスタ　メンテナンス</div>', unsafe_allow_html=True)

# サンプルデータ生成
@st.cache_data
def generate_sample_data():
    facilities = []
    prefectures = ["東京都", "大阪府", "愛知県", "神奈川県", "福岡県", "北海道", "宮城県"]
    cities = {
        "東京都": ["新宿区", "渋谷区", "港区", "千代田区"],
        "大阪府": ["大阪市", "堺市", "東大阪市"],
        "愛知県": ["名古屋市", "豊田市", "岡崎市"],
        "神奈川県": ["横浜市", "川崎市", "相模原市"],
        "福岡県": ["福岡市", "北九州市", "久留米市"],
        "北海道": ["札幌市", "函館市", "旭川市"],
        "宮城県": ["仙台市", "石巻市", "大崎市"]
    }
    
    facility_types = ["総合病院", "クリニック", "医療センター", "診療所", "病院"]
    
    for i in range(22, 52):  # 30件のサンプルデータ
        pref = random.choice(prefectures)
        city = random.choice(cities[pref])
        facility_type = random.choice(facility_types)
        base_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        facilities.append({
            "医療機関ID": i,
            "医療機関名": f"○○{facility_type}",
            "都道府県": pref,
            "市区町村": city,
            "更新日時": base_date.strftime("%Y-%m-%d")
        })
    
    return pd.DataFrame(facilities)

# データ取得
df = generate_sample_data()

# 2カラムレイアウト
col1, col2 = st.columns([2, 1])

with col1:
    # 検索フォーム
    st.subheader("🔍 検索条件")
    
    search_col1, search_col2, search_col3, search_col4 = st.columns([3, 2, 2, 1])
    
    with search_col1:
        st.write("**医療機関名**")
        search_name = st.text_input("", placeholder="部分一致検索", key="search_name")
    
    with search_col2:
        st.write("**都道府県**")
        prefectures = [""] + df["都道府県"].unique().tolist()
        search_pref = st.selectbox("", prefectures, key="search_pref")
    
    with search_col3:
        st.write("**市区町村**")
        cities = [""]
        if search_pref:
            cities.extend(df[df["都道府県"] == search_pref]["市区町村"].unique().tolist())
        search_city = st.selectbox("", cities, key="search_city")
    
    with search_col4:
        st.write("")  # スペース調整
        search_button = st.button("検索", use_container_width=True)
    
    # フィルタリング
    filtered_df = df.copy()
    
    if search_name:
        filtered_df = filtered_df[filtered_df["医療機関名"].str.contains(search_name, na=False)]
    
    if search_pref:
        filtered_df = filtered_df[filtered_df["都道府県"] == search_pref]
    
    if search_city:
        filtered_df = filtered_df[filtered_df["市区町村"] == search_city]
    
    # テーブル表示
    st.subheader("📋 医療機関一覧")
    
    # ページネーション設定
    items_per_page = 10
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
    
    # テーブル表示（行クリック選択）
    if not page_df.empty:
        # セッションステートで選択行を管理
        if 'selected_row_index' not in st.session_state:
            st.session_state.selected_row_index = None
        
        # テーブル表示（イベント取得用）
        event = st.dataframe(
            page_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="facilities_table"
        )
        
        # 行が選択された場合
        if event['selection']['rows']:
            st.session_state.selected_row_index = event['selection']['rows'][0]
        
        # ページネーションボタン
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        with nav_col1:
            if current_page > 1:
                if st.button("⬅️ 前へ", use_container_width=True):
                    st.rerun()
        
        with nav_col3:
            if current_page < total_pages:
                if st.button("次へ ➡️", use_container_width=True):
                    st.rerun()
    else:
        st.info("検索条件に一致する医療機関がありません。")

with col2:
    # 入力フォーム
    st.subheader("✏️ 医療機関情報")
    
    # 選択された行のデータを取得
    selected_data = None
    if st.session_state.selected_row_index is not None:
        try:
            selected_data = page_df.iloc[st.session_state.selected_row_index]
        except IndexError:
            # ページ変更などで選択行が存在しない場合
            st.session_state.selected_row_index = None
    
    # フォーム入力
    st.write("**医療機関ID**")
    medical_id = st.text_input(
        "",
        value=str(selected_data["医療機関ID"]) if selected_data is not None else "",
        disabled=True,
        key="medical_id"
    )
    
    st.write("**医療機関名** *")
    facility_name = st.text_input(
        "",
        value=selected_data["医療機関名"] if selected_data is not None else "",
        placeholder="必須項目",
        key="facility_name"
    )
    
    st.write("**郵便番号**")
    postal_code = st.text_input(
        "",
        placeholder="123-4567",
        key="postal_code"
    )
    
    st.write("**都道府県**")
    prefecture = st.text_input(
        "",
        value=selected_data["都道府県"] if selected_data is not None else "",
        key="prefecture"
    )
    
    st.write("**市区町村**")
    city = st.text_input(
        "",
        value=selected_data["市区町村"] if selected_data is not None else "",
        key="city"
    )
    
    st.write("**住所詳細**")
    address_detail = st.text_input(
        "",
        placeholder="番地・建物名など",
        key="address_detail"
    )
    
    st.write("**電話番号**")
    phone_number = st.text_input(
        "",
        placeholder="03-1234-5678",
        key="phone_number"
    )
    
    st.write("**FAX番号**")
    fax_number = st.text_input(
        "",
        placeholder="03-1234-5679",
        key="fax_number"
    )
    
    st.write("**Email** *")
    email_address = st.text_input(
        "",
        placeholder="info@hospital.jp",
        key="email_address"
    )
    
    st.write("**ホームページURL**")
    website_url = st.text_input(
        "",
        placeholder="https://www.hospital.jp",
        key="website_url"
    )
    
    st.write("**備考**")
    notes = st.text_area(
        "",
        placeholder="その他の情報",
        key="notes"
    )
    
    # ボタン
    st.write("")  # スペース
    button_col1, button_col2 = st.columns(2)
    
    with button_col1:
        if st.button("🆕 新規登録", use_container_width=True):
            if facility_name and email_address:
                st.success("新規登録が完了しました！")
            else:
                st.error("必須項目を入力してください。")
    
    with button_col2:
        if st.button("🔄 更新", use_container_width=True):
            if selected_data is not None:
                if facility_name and email_address:
                    st.success("更新が完了しました！")
                else:
                    st.error("必須項目を入力してください。")
            else:
                st.warning("更新対象の医療機関を選択してください。")

