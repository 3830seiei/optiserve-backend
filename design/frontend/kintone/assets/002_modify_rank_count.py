import streamlit as st

# ------------------------
# サンプル医療機関データ
# ------------------------
medical_entities = [
    {"entity_code": 1, "entity_name": "順天堂医院", "rank_count": 5},
    {"entity_code": 2, "entity_name": "医療法人ABC", "rank_count": 3},
    {"entity_code": 3, "entity_name": "国立西東京病院", "rank_count": 7},
    {"entity_code": 4, "entity_name": "東東京クリニック", "rank_count": 4},
    {"entity_code": 5, "entity_name": "赤坂メディカル", "rank_count": 6},
    {"entity_code": 6, "entity_name": "大阪第一病院", "rank_count": 2}
]

# ------------------------
# タイトルと説明
# ------------------------
st.title("レポート出力ランク数設定")
st.markdown("医療機関ごとにレポートの出力ランク数を変更できます。")

st.subheader("🔍 医療機関一覧")
# ------------------------
# 検索キー入力欄
# ------------------------
search_key = st.text_input("検索キー（医療機関名）")

# ------------------------
# 医療機関フィルタ処理（最大5件表示）
# ------------------------
if search_key:
    filtered = [e for e in medical_entities if search_key in e["entity_name"]]
else:
    filtered = medical_entities

filtered = filtered[:5]  # 最大5件に制限

if not filtered:
    st.warning("該当する医療機関が見つかりません。")
    st.stop()

# ------------------------
# 医療機関一覧 表形式表示
# ------------------------
#st.subheader("🔍 医療機関一覧（最大5件）")  # 上に移動
st.table([
    {"コード": e["entity_code"], "医療機関名": e["entity_name"], "出力ランク数": e["rank_count"]}
    for e in filtered
])

# モックなので固定の値をセット
## ------------------------
## 医療機関選択用セレクトボックス
## ------------------------
#selected_code = st.selectbox(
#    "変更対象の医療機関を選択してください",
#    [e["entity_code"] for e in filtered],
#    format_func=lambda code: next(e["entity_name"] for e in filtered if e["entity_code"] == code)
#)
selected_code = 1  # モックなので固定値を使用
selected_entity = next((e for e in filtered if e["entity_code"] == selected_code), None)

# ------------------------
# 既存情報を st.expander で枠囲み
# ------------------------
if selected_entity:
    with st.expander("🧾 既存情報", expanded=True):
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("**医療機関コード**")
        with col2:
            st.text(selected_entity["entity_code"])

        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("**医療機関名**")
        with col2:
            st.text(selected_entity["entity_name"])

        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("**出力ランク数**")
        with col2:
            st.text(selected_entity["rank_count"])

# ------------------------
# 変更後ランク数入力欄
# ------------------------
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown("**変更後ランク数**")
with col2:
    new_rank = st.number_input(
        "",
        min_value=1,
        max_value=99,
        value=selected_entity["rank_count"],
        step=1
    )

# ------------------------
# ボタン表示（右寄せ、横並び）
# ------------------------
col_spacer, col_register, col_close = st.columns([6, 1, 1])
with col_register:
    register = st.button("登録")
with col_close:
    close = st.button("閉じる")

# ------------------------
# ボタンのアクション処理
# ------------------------
if register:
    if new_rank != selected_entity["rank_count"]:
        st.success("登録は正常に行なわれました。")
        st.json({
            "status": "success",
            "message": "登録は正常に行なわれました。",
            "data": {
                "entity_code": selected_entity["entity_code"],
                "entity_name": selected_entity["entity_name"],
                "rank_count": new_rank
            }
        })
    else:
        st.info("変更後ランク数が現在と同じです。変更は行われません。")

if close:
    st.warning("画面を閉じました。（この画面では仮処理）")
