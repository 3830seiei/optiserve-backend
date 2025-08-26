import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# ページ設定
st.set_page_config(
    page_title="機器分析設定",
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
    
    .equipment-row {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 4px;
        margin: 5px 0;
        border: 1px solid #ddd;
    }
    
    .modified-row {
        background-color: #fff3cd;
        border-color: #ffeaa7;
    }
    
    .default-row {
        background-color: #d4edda;
        border-color: #c3e6cb;
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
st.markdown('<div class="main-header">機器分析設定</div>', unsafe_allow_html=True)

# サンプル機器データ生成
@st.cache_data
def generate_equipment_data():
    equipment_list = []
    
    # 機器分類の定義
    classifications = [
        "人工呼吸器", "輸液ポンプ", "心電図モニター", "除細動器", "電気メス",
        "血液透析装置", "麻酔器", "超音波診断装置", "X線撮影装置", "内視鏡",
        "生体情報モニター", "送液ポンプ", "手術用顕微鏡", "人工心肺装置", "血液浄化装置"
    ]
    
    override_classifications = [
        "重要機器A", "重要機器B", "一般機器", "点検対象外", "廃棄予定"
    ]
    
    for i in range(50):
        equipment_id = f"EQ{2024000 + i:06d}"
        equipment_name = f"{random.choice(['○○', '△△', '××', '◇◇'])}{random.choice(classifications)}"
        default_classification = random.choice(classifications)
        
        # 30%の確率で上書き設定あり
        has_override = random.random() < 0.3
        override_classification = random.choice(override_classifications) if has_override else ""
        
        # 分析対象設定
        default_analysis = random.choice([True, False])
        override_analysis = not default_analysis if has_override and random.random() < 0.5 else None
        
        # 変更履歴
        if has_override:
            change_date = datetime.now() - timedelta(days=random.randint(1, 90))
            change_user = random.choice(["田中", "佐藤", "鈴木", "高橋"])
            change_reason = random.choice([
                "病院独自ルールに基づく変更",
                "重要度見直しによる再分類",
                "メンテナンス方針変更",
                "運用実態に合わせた調整"
            ])
        else:
            change_date = None
            change_user = ""
            change_reason = ""
        
        equipment_list.append({
            "機器ID": equipment_id,
            "機器名": equipment_name,
            "システム標準分類": default_classification,
            "上書き分類": override_classification,
            "システム標準_分析対象": "○" if default_analysis else "×",
            "上書き_分析対象": "○" if override_analysis == True else ("×" if override_analysis == False else ""),
            "変更状況": "上書きあり" if has_override else "標準設定",
            "最終変更日": change_date.strftime("%Y-%m-%d") if change_date else "",
            "変更者": change_user,
            "変更理由": change_reason
        })
    
    return pd.DataFrame(equipment_list)

# データ取得
equipment_df = generate_equipment_data()

# 検索・フィルタ部分
st.subheader("🔍 機器検索・フィルタ")

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 2, 2, 1])

with filter_col1:
    st.write("**機器名**")
    search_name = st.text_input("", placeholder="部分一致検索", key="search_equipment")

with filter_col2:
    st.write("**変更状況**")
    status_filter = st.selectbox("", ["すべて", "上書きあり", "標準設定"], key="status_filter")

with filter_col3:
    st.write("**分析対象**")
    analysis_filter = st.selectbox("", ["すべて", "対象", "対象外"], key="analysis_filter")

with filter_col4:
    st.write("")
    search_button = st.button("🔍 検索", use_container_width=True)

# フィルタリング
filtered_df = equipment_df.copy()

if search_name:
    filtered_df = filtered_df[filtered_df["機器名"].str.contains(search_name, na=False)]

if status_filter != "すべて":
    filtered_df = filtered_df[filtered_df["変更状況"] == status_filter]

if analysis_filter == "対象":
    filtered_df = filtered_df[
        (filtered_df["上書き_分析対象"] == "○") | 
        ((filtered_df["上書き_分析対象"] == "") & (filtered_df["システム標準_分析対象"] == "○"))
    ]
elif analysis_filter == "対象外":
    filtered_df = filtered_df[
        (filtered_df["上書き_分析対象"] == "×") | 
        ((filtered_df["上書き_分析対象"] == "") & (filtered_df["システム標準_分析対象"] == "×"))
    ]

# メイン画面を2カラムレイアウト
col1, col2 = st.columns([2, 1])

with col1:
    # 機器一覧表示
    st.subheader("🔧 機器分析設定一覧")
    
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
    if 'selected_equipment_index' not in st.session_state:
        st.session_state.selected_equipment_index = None
    
    # テーブル表示（行クリック選択）
    if not page_df.empty:
        # 表示用のデータフレーム作成（簡潔表示）
        display_df = page_df[["機器ID", "機器名", "システム標準分類", "上書き分類", "変更状況"]].copy()
        
        event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="equipment_table"
        )
        
        # 行が選択された場合
        if event['selection']['rows']:
            st.session_state.selected_equipment_index = event['selection']['rows'][0]
    else:
        st.info("検索条件に一致する機器がありません。")
    
    # 一括操作ボタン
    st.write("")
    bulk_col1, bulk_col2 = st.columns([1, 1])
    
    with bulk_col1:
        if st.button("🔄 選択機器を標準に戻す", use_container_width=True):
            if st.session_state.selected_equipment_index is not None:
                st.success("✅ 選択した機器の設定を標準に戻しました")
            else:
                st.warning("⚠️ 機器を選択してください")
    
    with bulk_col2:
        if st.button("💾 設定を保存", use_container_width=True):
            st.success("✅ 設定変更を保存しました")

with col2:
    # 機器詳細・編集フォーム
    st.subheader("✏️ 機器設定詳細")
    
    # 選択された機器のデータを取得
    selected_equipment = None
    if st.session_state.selected_equipment_index is not None:
        try:
            selected_equipment = page_df.iloc[st.session_state.selected_equipment_index]
        except IndexError:
            st.session_state.selected_equipment_index = None
    
    if selected_equipment is not None:
        # 機器基本情報
        st.write("**機器基本情報**")
        st.text_input("機器ID", value=selected_equipment["機器ID"], disabled=True, key="edit_id")
        st.text_input("機器名", value=selected_equipment["機器名"], disabled=True, key="edit_name")
        
        st.write("")
        st.write("**分類設定**")
        
        # システム標準分類（参照のみ）
        st.text_input("システム標準分類", value=selected_equipment["システム標準分類"], disabled=True, key="default_class")
        
        # 見直し後の機器分類（編集可能）
        st.write("**見直し後の機器分類**")
        override_options = ["", "重要機器A", "重要機器B", "一般機器", "点検対象外", "廃棄予定"]
        current_override = selected_equipment["上書き分類"] if selected_equipment["上書き分類"] else ""
        new_classification = st.selectbox("", override_options, 
                                        index=override_options.index(current_override) if current_override in override_options else 0,
                                        key="override_class")
        
        st.write("")
        st.write("**分析対象設定**")
        
        # システム標準の分析対象
        st.write(f"システム標準: {selected_equipment['システム標準_分析対象']}")
        
        # 上書き分析対象
        analysis_options = ["標準設定を使用", "分析対象にする", "分析対象外にする"]
        current_analysis = selected_equipment["上書き_分析対象"]
        if current_analysis == "○":
            default_analysis = 1
        elif current_analysis == "×":
            default_analysis = 2
        else:
            default_analysis = 0
            
        new_analysis = st.selectbox("見直し後の設定", analysis_options, index=default_analysis, key="override_analysis")
        
        st.write("")
        st.write("**変更理由**")
        change_reason = st.text_area("", placeholder="変更理由を入力してください", key="change_reason")
        
        st.write("")
        # 更新ボタン
        if st.button("🔄 設定更新", use_container_width=True):
            if change_reason.strip():
                st.success("✅ 機器設定を更新しました")
                st.info(f"📝 変更履歴に記録: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            else:
                st.error("❌ 変更理由を入力してください")
        
        st.write("")
        st.write("**変更履歴**")
        if selected_equipment["変更状況"] == "上書きあり":
            st.info(f"""
            **最終変更:** {selected_equipment['最終変更日']}  
            **変更者:** {selected_equipment['変更者']}  
            **理由:** {selected_equipment['変更理由']}
            """)
        else:
            st.info("変更履歴なし（標準設定）")
            
    else:
        st.info("機器を選択してください")
        
        st.write("")
        st.write("**操作ガイド**")
        st.info("""
        **機器分析設定について:**
        
        🔧 **標準設定**: システムが自動設定
        📝 **見直し設定**: 病院独自ルールで変更
        📊 **差分管理**: 標準と異なる設定のみ保存
        
        **操作手順:**
        1. 左の一覧から機器を選択
        2. 分類・分析対象を設定
        3. 変更理由を入力
        4. 「設定更新」で仮変更
        5. 「🔄 標準に戻す」で標準設定に復帰（仮）
        6. 「💾 設定を保存」でAPIに送信・正式反映
        
        **⚠️ 重要: 設定を保存しないと正式に反映されません**
        """)

