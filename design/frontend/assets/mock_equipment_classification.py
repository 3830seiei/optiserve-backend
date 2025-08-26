import streamlit as st
import pandas as pd
from datetime import datetime
import random

# ページ設定
st.set_page_config(
    page_title="機器分類管理",
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
    
    .classification-tree {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #ddd;
    }
    
    .level-1 { margin-left: 0px; font-weight: bold; color: #2c3e50; }
    .level-2 { margin-left: 20px; color: #34495e; }
    .level-3 { margin-left: 40px; color: #7f8c8d; }
    
    .selected-item {
        background-color: #e3f2fd;
        border: 2px solid #2196f3;
    }
    
    .report-selected {
        background-color: #fff3e0;
        border: 2px solid #ff9800;
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
st.markdown('<div class="main-header">機器分類管理</div>', unsafe_allow_html=True)

# サンプル分類データ生成
@st.cache_data
def generate_classification_data():
    # 3階層の分類構造を定義
    classifications = {
        "生命維持管理装置": {
            "人工呼吸器": ["成人用人工呼吸器", "小児用人工呼吸器", "在宅用人工呼吸器"],
            "心臓ペースメーカ": ["体外式ペースメーカ", "植込み型ペースメーカ", "除細動器付きペースメーカ"],
            "人工心肺装置": ["体外循環装置", "ECMO装置", "IABP装置"]
        },
        "治療用機器": {
            "電気メス": ["単極式電気メス", "双極式電気メス", "高周波ナイフ"],
            "レーザー手術装置": ["炭酸ガスレーザー", "YAGレーザー", "半導体レーザー"],
            "血液透析装置": ["個人用透析装置", "多人数用透析装置", "携帯型透析装置"]
        },
        "診断用機器": {
            "X線撮影装置": ["一般撮影装置", "CT装置", "MRI装置"],
            "超音波診断装置": ["汎用超音波装置", "心エコー装置", "内視鏡用超音波"],
            "内視鏡": ["上部消化管内視鏡", "下部消化管内視鏡", "気管支鏡"]
        },
        "監視用機器": {
            "生体情報モニター": ["ベッドサイドモニター", "セントラルモニター", "テレメトリー"],
            "心電図": ["12誘導心電図", "ホルター心電図", "運動負荷心電図"],
            "血圧計": ["自動血圧計", "24時間血圧計", "観血血圧計"]
        }
    }
    
    # データフレーム作成
    data = []
    classification_id = 1
    
    for major, middle_dict in classifications.items():
        for middle, minor_list in middle_dict.items():
            for minor in minor_list:
                # レポート選択状況（優先順位1-5をユニークに設定）
                is_selected = False
                priority = 0
                equipment_count = random.randint(5, 50)
                
                data.append({
                    "分類ID": classification_id,
                    "大分類": major,
                    "中分類": middle,
                    "小分類": minor,
                    "機器数": equipment_count,
                    "優先順位": priority if is_selected else "",
                    "最終更新": datetime.now().strftime("%Y-%m-%d")
                })
                classification_id += 1
    
    df = pd.DataFrame(data)
    
    # 5つの分類に1-5の優先順位をユニークに設定
    selected_indices = [0, 4, 8, 15, 22]  # 適当に5つ選択
    for i, idx in enumerate(selected_indices):
        df.at[idx, "優先順位"] = i + 1
    
    return df

# データ取得
classification_df = generate_classification_data()

# 検索・フィルタ部分
st.subheader("🔍 分類検索・フィルタ")

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 2, 2, 1])

with filter_col1:
    st.write("**分類名**")
    search_name = st.text_input("", placeholder="分類名で検索", key="search_classification")

with filter_col2:
    st.write("**大分類**")
    major_categories = ["すべて"] + list(classification_df["大分類"].unique())
    major_filter = st.selectbox("", major_categories, key="major_filter")

with filter_col3:
    st.write("**レポート選択**")
    report_filter = st.selectbox("", ["すべて", "選択済み", "未選択"], key="report_filter")

with filter_col4:
    st.write("")
    search_button = st.button("🔍 検索", use_container_width=True)

# フィルタリング
filtered_df = classification_df.copy()

if search_name:
    filtered_df = filtered_df[
        filtered_df["大分類"].str.contains(search_name, na=False) |
        filtered_df["中分類"].str.contains(search_name, na=False) |
        filtered_df["小分類"].str.contains(search_name, na=False)
    ]

if major_filter != "すべて":
    filtered_df = filtered_df[filtered_df["大分類"] == major_filter]

if report_filter == "選択済み":
    filtered_df = filtered_df[filtered_df["優先順位"] != ""]
elif report_filter == "未選択":
    filtered_df = filtered_df[filtered_df["優先順位"] == ""]

# メイン画面を2カラムレイアウト
col1, col2 = st.columns([2, 1])

with col1:
    # 分類一覧表示
    st.subheader("📂 機器分類一覧")
    
    # レポート分類レベルと選択状況表示
    st.info("📊 レポートでは小分類を利用します")
    
    selected_count = len(classification_df[classification_df["優先順位"] != ""])
    max_selections = 5
    
    st.info(f"📊 レポート出力選択状況: {selected_count}/{max_selections}件選択中")
    
    # ページネーション設定
    items_per_page = 20
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
    if 'selected_classification_index' not in st.session_state:
        st.session_state.selected_classification_index = None
    
    # テーブル表示（行クリック選択）
    if not page_df.empty:
        # 表示用のデータフレーム作成
        display_df = page_df[["分類ID", "大分類", "中分類", "小分類", "機器数", "優先順位"]].copy()
        
        event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="classification_table"
        )
        
        # 行が選択された場合
        if event['selection']['rows']:
            st.session_state.selected_classification_index = event['selection']['rows'][0]
    else:
        st.info("検索条件に一致する分類がありません。")
    
    # レポート選択管理
    st.write("")
    st.write("**レポート出力対象分類**")
    
    # 現在選択されている分類の表示
    selected_for_report = classification_df[classification_df["優先順位"] != ""].sort_values("優先順位")
    
    if not selected_for_report.empty:
        for _, row in selected_for_report.iterrows():
            st.write(f"{int(row['優先順位'])}. {row['大分類']} > {row['中分類']} > {row['小分類']} ({row['機器数']}台)")
    else:
        st.info("レポート出力対象の分類が選択されていません。")
    
    st.write("")
    
    # 一括操作ボタン
    reset_col, save_col = st.columns([1, 1])
    
    with reset_col:
        if st.button("🔄 選択リセット", use_container_width=True):
            st.warning("⚠️ 全てのレポート出力選択を解除しますか？")
    
    with save_col:
        if st.button("💾 設定保存", use_container_width=True):
            st.success("✅ レポート選択設定を保存しました")

with col2:
    # 分類詳細・編集フォーム
    st.subheader("✏️ 分類詳細・レポート設定")
    
    # 選択された分類のデータを取得
    selected_classification = None
    if st.session_state.selected_classification_index is not None:
        try:
            selected_classification = page_df.iloc[st.session_state.selected_classification_index]
        except IndexError:
            st.session_state.selected_classification_index = None
    
    if selected_classification is not None:
        # 分類基本情報
        st.write("**分類基本情報**")
        st.text_input("分類ID", value=str(selected_classification["分類ID"]), disabled=True, key="class_id")
        st.text_input("大分類", value=selected_classification["大分類"], disabled=True, key="major_class")
        st.text_input("中分類", value=selected_classification["中分類"], disabled=True, key="middle_class")
        st.text_input("小分類", value=selected_classification["小分類"], disabled=True, key="minor_class")
        st.text_input("機器数", value=f"{selected_classification['機器数']}台", disabled=True, key="equipment_count")
        
        st.write("")
        st.write("**レポート出力設定**")
        
        # 現在の選択状況
        current_selected = selected_classification["優先順位"] != ""
        current_priority = int(selected_classification["優先順位"]) if selected_classification["優先順位"] != "" else 0
        
        # レポート出力選択
        report_selected = st.checkbox("レポート出力対象に含める", value=current_selected, key="report_checkbox")
        
        # 優先順位設定（選択時のみ）
        if report_selected:
            st.write("**優先順位**")
            priority = st.selectbox("", list(range(1, 6)), index=current_priority-1 if current_priority > 0 else 0, key="priority_select")
            
            st.info(f"""
            **選択中の分類:**
            {selected_classification['大分類']} > {selected_classification['中分類']} > {selected_classification['小分類']}
            
            **優先順位:** {priority}
            **機器数:** {selected_classification['機器数']}台
            """)
        else:
            priority = 0
        
        st.write("")
        # 更新ボタン
        if st.button("🔄 設定更新", use_container_width=True):
            # 選択数制限チェック
            current_selected_count = len(classification_df[classification_df["レポート選択"] == "●"])
            
            if report_selected and not current_selected:
                # 新規選択の場合
                if current_selected_count >= max_selections:
                    st.error(f"❌ レポート出力対象は最大{max_selections}件までです。他の分類を解除してください。")
                else:
                    st.success("✅ レポート出力対象に追加しました")
            elif not report_selected and current_selected:
                # 選択解除の場合
                st.success("✅ レポート出力対象から除外しました")
            elif report_selected and current_selected:
                # 優先順位変更の場合
                st.success(f"✅ 優先順位を{priority}に変更しました")
            else:
                st.info("変更はありません")
        
            
    else:
        st.info("分類を選択してください")
        
        st.write("")
        st.write("**操作ガイド**")
        st.info("""
        **機器分類管理について:**
        
        📂 **3階層構造**: 大分類 > 中分類 > 小分類
        📊 **レポート選択**: 最大5件まで選択可能
        🔢 **優先順位**: 1-5でユニーク（重複不可）
        
        **操作手順:**
        1. 左の一覧から分類を選択
        2. レポート出力対象にチェック
        3. 優先順位を設定（1-5）
        4. 「設定更新」で仮変更
        5. 「💾 設定保存」で正式反映
        
        **制限事項:**
        - レポート出力は最大5分類まで
        - 優先順位はユニーク（既存順位を選択すると既存は下に下がる）
        - 設定保存まで仮変更状態
        """)


