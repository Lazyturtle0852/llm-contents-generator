import streamlit as st
import google.generativeai as genai


# --- ページ設定とAPIキー設定 ---
st.set_page_config(page_title="LLMコンテンツ生成アシスタント", layout="wide")
st.title("📝 LLMコンテンツ生成アシスタント")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("models/gemini-2.5-flash-lite")

except Exception as e:
    st.error(
        "APIキーの設定に失敗しました。`.streamlit/secrets.toml`ファイルを確認してください。"
    )
    st.stop()


# --- UI（ユーザーインターフェース）の構築 ---
st.subheader("ステップ1：キーワードと概要の入力")


# --- session_stateの初期化 ---
if "keyword_count" not in st.session_state:
    st.session_state.keyword_count = 1
if "title_list" not in st.session_state:
    st.session_state.title_list = []
if "article_text" not in st.session_state:
    st.session_state.article_text = ""

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
style = st.text_area("文章のスタイル（任意）:", placeholder="（省略可）...")


# 入力されたキーワードをカンマ区切りの一つの文字列に変換
keywords_str = ", ".join(keywords_list)

# タイトル生成ボタン
if st.button("1. タイトル案を10個生成する"):
    if not keywords_str:
        st.warning("キーワードを入力してください。")
    else:
        # --- 動的なプロンプト組み立て ---
        prompt_for_titles = f"""
        # 命令
        あなたは、中堅企業向けにノーコード業務自動化ツールを提供するSaaS企業「CloudFlow Dynamics」の、非常に優秀なコンテンツマーケターです。

        # ターゲット読者
        - 中堅企業の経理、人事、営業部門のマネージャー層。
        - プログラミング知識はないが、日々の手作業や部署間の非効率な連携に強い課題を感じている。
        
        # 記事の目的
        ターゲット読者が抱えるであろう具体的な業務課題を提示し、解決策への期待感を抱かせることで、記事のクリックを促すこと。

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
        - 上記のターゲット読者が「これは自分のための記事だ！」と直感的に感じるような、具体的で課題解決志向のタイトル案を10個生成してください。
        - 専門的すぎず、しかし示唆に富んだ表現を心がけてください。
        - 必ず番号付きリスト（1., 2., 3., ...）の形式で、タイトルのみを記述してください。
        - 他の余計な文章は一切含めないでください。
        """

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
        # --- 動的なプロンプト組み立て ---
        prompt_for_article = f"""
        # あなた（AI）の役割
        あなたは、中堅企業向けにノーコード業務自動化ツールを提供する急成長SaaS企業「CloudFlow Dynamics」の、非常に優秀なコンテンツマーケターです。

        # 記事の最終ゴール
        読者が記事を読み終えた時、自分たちの会社にはびこる非効率な手作業や業務プロセスへの課題意識が最大化され、具体的な解決策として当社の製品に強い興味を持ち、資料請求や無料トライアルを検討したくなる状態を作り出すことです。

        # ターゲット読者
        中堅企業の経理、人事、営業部門のマネージャー層。プログラミングの知識はないが、日々の手作業（Excel、メールのコピペなど）や部署間の非効率な連携に課題を感じています。

        # トーン＆マナー
        専門性を感じさせつつも、難解な言葉は避け、読者に深く共感し、共に課題を解決していくパートナーのような、信頼感と説得力のあるトーンで記述してください。
        

        # タイトル
        {selected_title}
        """

        if style:
            prompt_for_article += f"""
        # 指定文章スタイル
        文章のスタイルは以下の通りにしてください。
        ---
        {style}
        """

        if summary:
            prompt_for_article += f"""
        # 参考概要
        以下の概要も、記事の内容を膨らませる上で強く参考にしてください。
        ---
        {summary}
        """

        prompt_for_article += f"""
        # 構造と要件
        - 全体で{wordcount}字程度の、読み応えのある文章を生成してください。
        - 必ず以下の構造に従ってください。
          - 導入: ターゲット読者が日常的に体験しているであろう、具体的な「あるある」な課題や非効率な業務風景を描写し、深く共感を得る。
          - 課題の深掘り: なぜその非効率が生まれるのか、その根本原因（例：情報のサイロ化、属人化など）を分かりやすく解説する。
          - 解決の方向性: テクノロジーを活用して「業務の仕組み化・自動化」を目指すべきである、という大きな方針を示す。
          - 結論（自社製品への誘導）: 記事のまとめとして、その「業務の仕組み化・自動化」を、プログラミング知識なしで実現できる具体的な解決策として、当社のノーコードツール『FlowSpark』を自然な形で紹介する。読者が次のアクション（資料請求、無料トライアル）を取りたくなるような、希望に満ちた締めくくりをしてください。
        - 「手作業」「自動化」「ワークフロー」「DX」といったキーワードを適切に含めてください。
        -  余計な文章（例：「承知しました」）などは一切含めないでください
        """

        with st.spinner("AIが記事を執筆中です..."):
            try:
                response = model.generate_content(prompt_for_article)
                st.session_state["article_text"] = response.text
                st.rerun()
            except Exception as e:
                st.error("記事の生成中にエラーが発生しました。")
                st.exception(e)

if "article_text" in st.session_state:
    st.subheader("ステップ3：記事の編集・調整・コピー")

    # 画面を左右2つのカラムに分割
    col1, col2 = st.columns(2)

    with col1:
        st.write("**編集エリア（Markdown記法）**")
        edited_text = st.text_area(
            "ここで自由に編集できます:",
            value=st.session_state["article_text"],
            height=600,
            label_visibility="collapsed",
        )

    with col2:
        st.write("**リアルタイムプレビュー**")
        # 編集エリアのテキスト(edited_text)を、リアルタイムでMarkdownとして表示
        st.markdown(edited_text)

    st.write("---")

    # --- AIによる自動調整機能 ---
    st.subheader("AIによる自動調整")
    rewrite_instruction = st.text_input(
        "調整の指示を入力してください（例：もっとフレンドリーな口調にして、絵文字も使って）"
    )

    if st.button("AIで調整する"):
        if not rewrite_instruction:
            st.warning("調整の指示を入力してください。")
        else:
            with st.spinner("AIが記事を調整中です..."):
                rewrite_prompt = f"""
                # 命令
                あなたは、非常に優秀なプロの編集者です。
                以下の「元の文章」を、「編集指示」に従って、より質の高い文章に修正・再構成してください。
                元の文章の良い点は活かしつつ、指示に忠実に従ってください。
                なお、余計な文章は一切含めないこと。

                # 元の文章
                ---
                {edited_text} 
                ---

                # 編集指示
                ---
                {rewrite_instruction}
                ---

                # 修正後の文章
                """

                try:
                    response = model.generate_content(rewrite_prompt)
                    st.session_state["article_text"] = response.text
                    st.session_state["text_for_editing"] = response.text
                    st.rerun()
                except Exception as e:
                    st.error("記事の調整中にエラーが発生しました。")
                    st.exception(e)

    # コピー用コードブロック(冗長なのでコメントアウト中)
    # st.write("📋 下の枠からワンクリックでコピーできます：")
    # st.code(st.session_state["article_text"], language=None)


st.divider()
st.header("デバッグ情報")
st.write("現在の`st.session_state`の中身:")
st.json(st.session_state)
