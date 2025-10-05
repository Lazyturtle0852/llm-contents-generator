import streamlit as st
import google.generativeai as genai

# --- ページ設定とAPIキー設定 ---
# (ここは変更なし)
st.set_page_config(page_title="LLMコンテンツ生成アシスタント", layout="wide")
st.title("📝 LLMコンテンツ生成アシスタント")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(
        "APIキーの設定に失敗しました。`.streamlit/secrets.toml`ファイルを確認してください。"
    )
    st.stop()

# --- UI（ユーザーインターフェース）の構築 ---
st.subheader("ステップ1：キーワードと概要の入力")

# session_stateにキーワードの数がなければ、初期値として1を設定
if "keyword_count" not in st.session_state:
    st.session_state["keyword_count"] = 1

# キーワード入力欄を、現在の数だけ動的に生成
keywords_list = []
for i in range(st.session_state["keyword_count"]):
    # st.text_inputにユニークな`key`を与えることが重要
    keyword = st.text_input(f"キーワード {i + 1}", key=f"keyword_{i}")
    if keyword:
        keywords_list.append(keyword)

# 2列のレイアウトを作成
col1, col2 = st.columns(2)

with col1:
    # 「キーワード追加」ボタン
    if st.button("＋ キーワードを追加"):
        st.session_state["keyword_count"] += 1
        st.rerun()  # ページを即座に再実行して入力欄を増やす

with col2:
    # 「キーワードを減らす」ボタン
    if st.session_state["keyword_count"] > 1:
        if st.button("－ キーワードを減らす"):
            st.session_state["keyword_count"] -= 1
            st.rerun()  # ページを即座に再実行

summary = st.text_area("書きたい記事の概要（任意）:", placeholder="（省略可）...")

# 入力されたキーワードをカンマ区切りの一つの文字列に変換
keywords_str = ", ".join(keywords_list)

# タイトル生成ボタン
if st.button("1. タイトル案を10個生成する"):
    if not keywords_str:
        st.warning("キーワードを入力してください。")
    else:
        model = genai.GenerativeModel("models/gemini-pro-latest")

        # --- 動的なプロンプト組み立て ---
        prompt_for_titles = f"""
        # 命令
        あなたは、最新のLLMOに精通した、優秀なコンテンツマーケターです。
        指定されたテーマに基づき、読者の興味を引き、クリックしたくなるような魅力的なブログ記事のタイトル案を10個生成してください。

        # テーマ
        {keywords_str}
        """
        if summary:
            prompt_for_titles += f"""
        # 参考概要
        以下の概要も考慮してください。
        ---
        {summary}
        """
        prompt_for_titles += """
        # 要件
        - 必ず番号付きリスト（1., 2., 3., ...）の形式で、タイトルのみを記述してください。
        - 「承知しました」などの、他の余計な文章は一切含めないでください。
        """
        # --- ここまで ---

        with st.spinner("AIがタイトル案を考案中です..."):
            try:
                response = model.generate_content(prompt_for_titles)
                titles = response.text.strip().split("\n")
                cleaned_titles = [
                    title.split(". ", 1)[1] for title in titles if ". " in title
                ]
                st.session_state["title_list"] = cleaned_titles
                st.success("タイトル案の生成が完了しました。下から1つ選んでください。")
            except Exception as e:
                st.error("タイトル生成中にエラーが発生しました。")
                st.exception(e)

# --- ステップ2：タイトル選択と記事生成 ---
if "title_list" in st.session_state and st.session_state["title_list"]:
    st.subheader("ステップ2：タイトル選択と記事生成")
    selected_title = st.radio("生成されたタイトル案:", st.session_state["title_list"])

    # 文字数設定
    wordcount = st.slider(
        "文字数を設定してください", min_value=50, max_value=5000, value=400, step=10
    )

    if st.button("2. 選択したタイトルで記事を生成する"):
        model = genai.GenerativeModel("models/gemini-pro-latest")

        # --- 動的なプロンプト組み立て ---
        prompt_for_article = f"""
        # 命令
        あなたは、最新のLLMOに精通した、優秀なコンテンツマーケターです。
        指定されたタイトルに基づき、読者に価値を提供し、生成AIが引用したくなるような、構造化されたブログ記事を生成してください。

        # タイトル
        {selected_title}
        """
        if summary:
            prompt_for_article = f"""
            # 命令
            あなたは、急成長中のSaaS企業「CloudFlow Dynamics」に所属する、最新のLLMOに精通した、非常に優秀なコンテンツマーケターです。

            # 記事の目的
            この記事の目的は、「プロジェクト管理」に課題を持つ潜在顧客（プロジェクトリーダーやマネージャー層）の共感を深く得て、最終的に自社製品への興味を自然な形で喚起することです。

            # トーン＆マナー
            専門性を感じさせつつも、難解な言葉は避け、読者に寄り添うような、信頼感と説得力のあるトーンで記述してください。

            # タイトル
            {selected_title}

            # 参考概要
            {summary if summary else "（特になし）"}

            # 構造と要件
            - 全体で{wordcount}字程度の、読み応えのある文章を生成してください。
            - 必ず以下の構造に従ってください。
            - 導入: 読者が「これは自分のことだ」と感じるような、具体的な課題や悩みを提示する。
            - 課題の深掘り: なぜその問題が起きるのか、その原因を分かりやすく解説する。
            - 解決策の提示: 課題を解決するための一般的なアプローチや考え方を示す。
            - **結論と次のステップ**: 記事のまとめとして、具体的な解決策の一つとして、架空の自社製品であるプロジェクト管理ツール『CloudFlow Dynamics』を自然な形で紹介し、読者が次のアクション（例：資料請求、無料トライアル）を取りたくなるように締めくくってください。
            - 読者がビジネスシーンを具体的にイメージできるように、「定例会議」「KPI管理」「リソース不足」のような、ビジネス用語を適切に含めてください。
            - 「承知しました」などの、他の余計な文章は一切含めないでください。

"""

        with st.spinner("AIが記事を執筆中です..."):
            try:
                response = model.generate_content(prompt_for_article)
                st.subheader("生成された記事 📝")
                st.markdown(response.text)
                st.success("記事の生成が完了しました。")
            except Exception as e:
                st.error("記事の生成中にエラーが発生しました。")
                st.exception(e)
