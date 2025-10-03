import streamlit as st
import google.generativeai as genai

# --- ページ設定とAPIキー設定 ---
st.set_page_config(page_title="LLMコンテンツ生成アシスタント", layout="wide")
st.title("LLMコンテンツ生成アシスタント")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("APIキーの設定に失敗しました。`.streamlit/secrets.toml`ファイルを確認してください。")
    st.stop()

# --- UI（ユーザーインターフェース）の構築 ---
st.subheader("ステップ1：キーワード入力")
keyword = st.text_input("記事のテーマとなるキーワードを入力してください", placeholder="例：港区赤坂の魅力")

# タイトル生成ボタン
if st.button("1. タイトル案を10個生成する"):
    if not keyword:
        st.warning("キーワードを入力してください。")
    else:
        model = genai.GenerativeModel('models/gemini-pro-latest')
        
        # タイトル生成用のプロンプト
        prompt = f"""
        # 命令
        あなたは、最新のLLMOに精通した、優秀なコンテンツマーケターです。
        指定されたテーマに基づき、読者の興味を引き、クリックしたくなるような魅力的なブログ記事のタイトル案を10個生成してください。

        # テーマ
        {keyword}

        # 要件
        - 必ず番号付きリスト（1., 2., 3., ...）の形式で、タイトルのみを記述してください。
        - 他の余計な文章（「承知いたしました」など）は一切含めないでください。
        """
        
        with st.spinner("AIがタイトル案を考案中です..."):
            try:
                response = model.generate_content(prompt)
                
                # AIの返答(ただのテキスト)を、改行で分割してリストに変換
                titles = response.text.strip().split("\n")
                
                # "1. タイトル" のような形式から、タイトル部分だけを抽出
                cleaned_titles = [title.split(". ", 1)[1] for title in titles if ". " in title]
                
                # session_stateにタイトルリストを保存
                st.session_state['title_list'] = cleaned_titles
                st.success("タイトル案の生成が完了しました。下から1つ選んでください。")

            except Exception as e:
                st.error("タイトル生成中にエラーが発生しました。")
                st.exception(e)

# --- ステップ2：タイトル選択と記事生成 ---
# session_stateにタイトルリストが保存されていたら、選択肢を表示
if 'title_list' in st.session_state and st.session_state['title_list']:
    st.subheader("ステップ2：タイトル選択と記事生成")
    
    selected_title = st.radio("生成されたタイトル案:", st.session_state['title_list'])
    
    if st.button("2. 選択したタイトルで記事を生成する"):
        model = genai.GenerativeModel('models/gemini-pro-latest')

        # 記事生成用のプロンプト
        prompt = f"""
        # 命令
        あなたは、最新のLLMOに精通した、優秀なコンテンツマーケターです。
        指定されたタイトルに基づき、読者に価値を提供し、生成AIが引用したくなるような、構造化されたブログ記事を生成してください。

        # タイトル
        {selected_title}

        # 構造と要件
        - 全体で400字から600字程度の文章を生成してください。
        - 他の余計な文章（「承知いたしました」など）は一切含めないでください。
        - 必ず以下の構造に従ってください。
          - 導入: 記事の概要と読者が得られるメリットを簡潔に記述。
          - 見出し1: 記事の核心を表す、魅力的な見出し。
          - 見出し2: 具体的な内容を示す、興味を引く小見出し。
          - まとめ: 記事全体の要点を箇条書きで2〜3つにまとめる。
        - 読者が具体的なイメージを持てるように、有名な固有名詞をいくつか含めてください。
        """
        
        with st.spinner("AIが記事を執筆中です..."):
            try:
                response = model.generate_content(prompt)
                st.subheader("生成された記事 📝")
                st.markdown(response.text)
                st.success("記事の生成が完了しました。")

            except Exception as e:
                st.error("記事の生成中にエラーが発生しました。")
                st.exception(e)