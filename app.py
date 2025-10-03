import google.generativeai as genai
import streamlit as st


st.title("LLMOコンテンツ制作アシスタント")

try:
   genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
   st.success("APIは正常に動作しています")

except Exception as e:
    st.error("APIの設定に失敗しました")
    st.stop()

# AIモデルを準備（最新の高速モデルを指定）
model = genai.GenerativeModel('models/gemini-pro-latest')

#キーワード入力待機
keyword = st.text_input("キーワードを入力してください（例：東京の魅力）", "東京の魅力")

if st.button("記事を生成する！"):
    if not keyword:
        st.warning("キーワードを入力してください。")
    else:
        model = genai.GenerativeModel('models/gemini-pro-latest')

        prompt = f"""
        # 命令
        あなたは、最新のLLMOに精通した、優秀なコンテンツマーケターです。
        指定されたテーマに基づき、生成AIが内容を正確に理解し、引用・参照したくなるような、構造化された短いブログ記事を生成してください。

        # テーマ
        {keyword}

        # 構造と要件
        - 全体で400字程度の文章を生成してください。
        - 必ず以下の構造に従ってください。
          - 導入: 記事の概要を簡潔に記述。
          - 見出し1: 記事の核心を表す、魅力的な見出し。
          - 見出し2: 具体的な内容を示す、興味を引く小見出し。
          - まとめ: 記事全体の要点を箇条書きで2〜3つにまとめる。
        - 読者が具体的なイメージを持てるように、有名な固有名詞をいくつか含めてください。
        """

        with st.spinner("AIが記事を執筆中です..."):
            try:
                response = model.generate_content(prompt)
                
                st.subheader("生成された記事")
                st.markdown(response.text)

            except Exception as e:
                st.error("記事の生成中にエラーが発生しました。")
                st.exception(e)
                