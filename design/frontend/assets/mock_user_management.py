import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# ページ設定
st.set_page_config(
    page_title="ユーザーマスタ管理",
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
    
    .status-active {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
    }
    
    .status-provisional {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
    }
    
    .status-inactive {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
    }
    
    .user-form {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #ddd;
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
st.markdown('<div class="main-header">ユーザーマスタ管理</div>', unsafe_allow_html=True)

# サンプルユーザーデータ生成
@st.cache_data
def generate_user_data():
    users = []
    
    # システム管理者ユーザー（900001-999999）
    for i in range(5):
        user_id = 900001 + i
        users.append({
            "ユーザーID": user_id,
            "ユーザー名": f"システム管理者{i+1}",
            "組織種別": "管理者権限",
            "entity_type": 9,
            "組織ID": 0,
            "組織名": "システム運営会社",
            "メールアドレス": f"admin{i+1}@system.co.jp",
            "電話番号": f"03-1234-567{i}",
            "携帯番号": f"080-1234-567{i}",
            "ステータス": "稼働中",
            "user_status": 1,
            "最終ログイン": datetime.now() - timedelta(days=random.randint(0, 7)),
            "登録日": datetime.now() - timedelta(days=random.randint(30, 180)),
            "最終更新": datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    # 医療機関ユーザー（100001-199999）
    medical_facilities = [
        "○○総合病院", "△△クリニック", "××医療センター", "◇◇病院", "☆☆診療所",
        "市立総合病院", "県立医療センター", "大学附属病院", "国立がんセンター", "こども病院"
    ]
    
    for facility_idx, facility in enumerate(medical_facilities):
        base_user_id = 100000 + facility_idx * 100
        medical_id = 100 + facility_idx
        
        # 各医療機関に2-4人のユーザー
        for user_idx in range(random.randint(2, 4)):
            user_id = base_user_id + user_idx + 1
            status_choice = random.choice(["稼働中", "仮登録", "利用停止"])
            status_code = 1 if status_choice == "稼働中" else (0 if status_choice == "仮登録" else 9)
            
            users.append({
                "ユーザーID": user_id,
                "ユーザー名": f"{facility}_担当者{user_idx+1}",
                "組織種別": "医療機関",
                "entity_type": 1,
                "組織ID": medical_id,
                "組織名": facility,
                "メールアドレス": f"user{user_id}@{facility.replace('○○', 'hospital').replace('△△', 'clinic').replace('××', 'medical')}.jp",
                "電話番号": f"0{random.randint(1,9)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                "携帯番号": f"0{random.randint(80,90)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                "ステータス": status_choice,
                "user_status": status_code,
                "最終ログイン": datetime.now() - timedelta(days=random.randint(0, 30)) if status_choice == "稼働中" else None,
                "登録日": datetime.now() - timedelta(days=random.randint(10, 90)),
                "最終更新": datetime.now() - timedelta(days=random.randint(1, 15))
            })
    
    # ディーラー・メーカーユーザー（少数）
    for entity_type, entity_name, user_range in [(2, "ディーラー", (200001, 200003)), (3, "メーカー", (300001, 300003))]:
        for user_id in range(user_range[0], user_range[1]):
            company_name = f"○○{entity_name}会社{user_id - user_range[0] + 1}"
            users.append({
                "ユーザーID": user_id,
                "ユーザー名": f"{company_name}_担当者",
                "組織種別": entity_name,
                "entity_type": entity_type,
                "組織ID": user_id - user_range[0] + 200,
                "組織名": company_name,
                "メールアドレス": f"user{user_id}@{entity_name.lower()}.co.jp",
                "電話番号": f"03-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                "携帯番号": f"080-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                "ステータス": random.choice(["稼働中", "仮登録"]),
                "user_status": random.choice([0, 1]),
                "最終ログイン": datetime.now() - timedelta(days=random.randint(5, 30)),
                "登録日": datetime.now() - timedelta(days=random.randint(20, 120)),
                "最終更新": datetime.now() - timedelta(days=random.randint(1, 20))
            })
    
    return pd.DataFrame(users)

# データ取得
user_df = generate_user_data()

# 検索・フィルタ部分
st.subheader("🔍 ユーザー検索・フィルタ")

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 2, 2, 1])

with filter_col1:
    st.write("**ユーザー名・メール**")
    search_name = st.text_input("", placeholder="部分一致検索", key="search_user")

with filter_col2:
    st.write("**組織種別**")
    entity_types = ["すべて", "医療機関", "ディーラー", "メーカー", "管理者権限"]
    entity_filter = st.selectbox("", entity_types, key="entity_filter")

with filter_col3:
    st.write("**ステータス**")
    status_filter = st.selectbox("", ["すべて", "稼働中", "仮登録", "利用停止"], key="status_filter")

with filter_col4:
    st.write("")
    search_button = st.button("🔍 検索", use_container_width=True)

# フィルタリング
filtered_df = user_df.copy()

if search_name:
    filtered_df = filtered_df[
        filtered_df["ユーザー名"].str.contains(search_name, na=False) |
        filtered_df["メールアドレス"].str.contains(search_name, na=False)
    ]

if entity_filter != "すべて":
    filtered_df = filtered_df[filtered_df["組織種別"] == entity_filter]

if status_filter != "すべて":
    filtered_df = filtered_df[filtered_df["ステータス"] == status_filter]

# メイン画面を2カラムレイアウト
col1, col2 = st.columns([2, 1])

with col1:
    # ユーザー一覧表示
    st.subheader("👥 ユーザー一覧")
    
    # 統計情報表示
    total_users = len(user_df)
    active_users = len(user_df[user_df["ステータス"] == "稼働中"])
    provisional_users = len(user_df[user_df["ステータス"] == "仮登録"])
    inactive_users = len(user_df[user_df["ステータス"] == "利用停止"])
    
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    with stats_col1:
        st.metric("総ユーザー数", f"{total_users}名")
    with stats_col2:
        st.metric("稼働中", f"{active_users}名")
    with stats_col3:
        st.metric("仮登録", f"{provisional_users}名")
    with stats_col4:
        st.metric("利用停止", f"{inactive_users}名")
    
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
    if 'selected_user_index' not in st.session_state:
        st.session_state.selected_user_index = None
    
    # テーブル表示（行クリック選択）
    if not page_df.empty:
        # 表示用のデータフレーム作成
        display_df = page_df[["ユーザーID", "ユーザー名", "組織種別", "組織名", "メールアドレス", "ステータス"]].copy()
        
        event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="user_table"
        )
        
        # 行が選択された場合
        if event['selection']['rows']:
            st.session_state.selected_user_index = event['selection']['rows'][0]
    else:
        st.info("検索条件に一致するユーザーがありません。")
    
    # 新規登録ボタン
    st.write("")
    if st.button("➕ 仮登録（新規ユーザー作成）", use_container_width=True):
        st.session_state.selected_user_index = None  # 新規登録モード
        st.session_state.new_user_mode = True
        st.rerun()

with col2:
    # ユーザー詳細・編集フォーム
    st.subheader("✏️ ユーザー詳細・編集")
    
    # 新規登録モードか既存ユーザー編集モードかを判定
    is_new_user = st.session_state.get('new_user_mode', False)
    selected_user = None
    
    if not is_new_user and st.session_state.selected_user_index is not None:
        try:
            selected_user = page_df.iloc[st.session_state.selected_user_index]
        except IndexError:
            st.session_state.selected_user_index = None
    
    if is_new_user or selected_user is not None:
        # フォーム表示
        st.markdown('<div class="user-form">', unsafe_allow_html=True)
        
        if is_new_user:
            st.write("**👤 新規ユーザー仮登録**")
            
            # 新規登録フォーム
            user_name = st.text_input("ユーザー名", key="new_user_name", help="必須項目：50文字以内")
            
            entity_types_new = ["医療機関", "ディーラー", "メーカー", "管理者権限"]
            entity_type = st.selectbox("組織種別", entity_types_new, key="new_entity_type")
            
            if entity_type != "管理者権限":
                entity_relation_id = st.number_input("組織ID", min_value=1, key="new_entity_id", help="必須項目：対象組織のID")
            else:
                entity_relation_id = 0
                st.info("管理者権限の場合、組織IDは自動的に0に設定されます。")
            
            email = st.text_input("メールアドレス", key="new_email", help="必須項目：有効なメールアドレス形式")
            
            st.write("")
            create_col1, create_col2 = st.columns([1, 1])
            
            with create_col1:
                if st.button("💾 仮登録実行", use_container_width=True):
                    if user_name and email and (entity_relation_id > 0 or entity_type == "管理者権限"):
                        st.success("✅ ユーザーを仮登録しました")
                        st.info("📧 自動生成パスワードをメール送信しました")
                        st.info("🔑 初回ログイン時にパスワード変更が必要です")
                        # リセット
                        st.session_state.new_user_mode = False
                        st.rerun()
                    else:
                        st.error("❌ 必須項目をすべて入力してください")
            
            with create_col2:
                if st.button("🔄 キャンセル", use_container_width=True):
                    st.session_state.new_user_mode = False
                    st.rerun()
        
        else:
            # 既存ユーザー編集フォーム
            st.write("**👤 ユーザー情報編集**")
            
            # 基本情報（読み取り専用）
            st.text_input("ユーザーID", value=str(selected_user["ユーザーID"]), disabled=True, key="edit_user_id")
            st.text_input("組織種別", value=selected_user["組織種別"], disabled=True, key="edit_entity_type")
            st.text_input("組織名", value=selected_user["組織名"], disabled=True, key="edit_org_name")
            
            # 編集可能項目
            user_name = st.text_input("ユーザー名", value=selected_user["ユーザー名"], key="edit_user_name")
            email = st.text_input("メールアドレス", value=selected_user["メールアドレス"], key="edit_email")
            phone_number = st.text_input("電話番号", value=selected_user["電話番号"], key="edit_phone")
            mobile_number = st.text_input("携帯番号", value=selected_user["携帯番号"], key="edit_mobile")
            
            # パスワード変更
            st.write("")
            st.write("**🔐 パスワード変更**")
            change_password = st.checkbox("パスワードを変更する", key="change_pwd_checkbox")
            
            if change_password:
                new_password = st.text_input("新しいパスワード", type="password", key="new_password",
                                           help="8文字以上、英大小文字・数字・記号を含む")
                confirm_password = st.text_input("パスワード確認", type="password", key="confirm_password")
                
                if new_password and confirm_password and new_password != confirm_password:
                    st.error("パスワードが一致しません")
            
            # ステータス管理（管理者のみ）
            current_user_is_admin = True  # 実際は認証情報から判定
            if current_user_is_admin:
                st.write("")
                st.write("**⚙️ ステータス管理（管理者のみ）**")
                
                status_options = ["稼働中", "仮登録", "利用停止"]
                current_status = selected_user["ステータス"]
                user_status = st.selectbox("ユーザーステータス", status_options,
                                         index=status_options.index(current_status) if current_status in status_options else 0,
                                         key="edit_status")
                
                # 利用停止の場合の追加項目
                if user_status == "利用停止":
                    st.write("**利用停止理由**")
                    reason_codes = ["組織退会", "担当者変更", "処理ミス", "その他"]
                    reason_code = st.selectbox("理由コード", reason_codes, key="reason_code")
                    reason_note = st.text_area("詳細理由", key="reason_note", help="255文字以内")
            
            # 最終ログイン・更新情報
            st.write("")
            st.write("**📊 利用状況**")
            last_login = selected_user["最終ログイン"]
            if last_login:
                st.info(f"**最終ログイン:** {last_login.strftime('%Y-%m-%d %H:%M')}")
            else:
                st.warning("**最終ログイン:** 未ログイン")
            
            st.info(f"""
            **登録日:** {selected_user['登録日'].strftime('%Y-%m-%d')}  
            **最終更新:** {selected_user['最終更新'].strftime('%Y-%m-%d %H:%M')}
            """)
            
            st.write("")
            # 更新ボタン
            update_col1, update_col2 = st.columns([1, 1])
            
            with update_col1:
                if st.button("💾 情報更新", use_container_width=True):
                    if user_status == "利用停止" and current_user_is_admin:
                        st.success("✅ ユーザーを利用停止に設定しました")
                        st.info(f"📝 理由: {reason_code} - {reason_note}")
                    else:
                        st.success("✅ ユーザー情報を更新しました")
                        if change_password and new_password:
                            st.info("🔐 パスワードも更新されました")
            
            with update_col2:
                if st.button("🔄 フォームリセット", use_container_width=True):
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.info("ユーザーを選択するか、仮登録ボタンをクリックしてください")
        
        st.write("")
        st.write("**操作ガイド**")
        st.info("""
        **ユーザーマスタ管理について:**
        
        👥 **権限別機能**:
        - システム管理者: 全ユーザー管理・仮登録・利用停止
        - 医療機関ユーザー: 自医療機関内ユーザーのみ編集
        
        🔐 **ユーザーステータス**:
        - 仮登録(0): 管理者が作成、初回ログイン待ち
        - 稼働中(1): 正常利用可能状態
        - 利用停止(9): アクセス不可状態
        
        **操作手順:**
        1. 検索・フィルタでユーザーを絞り込み
        2. 一覧から対象ユーザーを選択
        3. 右側フォームで情報を編集
        4. 「情報更新」で保存
        
        **新規登録:**
        - 「仮登録」ボタンで新規ユーザー作成
        - 自動生成パスワードをメール送信
        - ユーザーの初回ログインで本登録完了
        """)

