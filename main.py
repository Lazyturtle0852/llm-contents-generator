import streamlit as st

# 他のファイルから、中身を描画するshow関数をインポート
import edit
import generation

st.title("📝 LLMコンテンツ生成アシスタント")
st.set_page_config(page_title="LLMコンテンツ生成アシスタント", layout="wide")

# タブを作成
tab1, tab2 = st.tabs(["記事生成", "編集・調整"])

if "article_text" not in st.session_state:
    st.session_state.article_text = ""

# 各タブの中で、インポートした関数を呼び出す
with tab1:
    generation.show()

with tab2:
    edit.show()
