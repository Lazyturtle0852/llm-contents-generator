import streamlit as st
import google.generativeai as genai
import requests
import json


def show():
    if not st.session_state.article_text:
        st.info(
            "まだ記事が生成されていません。まずは「記事生成」タブで記事を生成してください。"
        )
        st.stop()
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("models/gemini-2.5-flash-lite")

    except Exception as e:
        st.error(
            "APIキーの設定に失敗しました。`.streamlit/secrets.toml`ファイルを確認してください。"
        )
        st.stop()
    try:
        api_key = st.secrets["GEMINI_API_KEY"]

    except FileNotFoundError:
        # ローカル環境などで .streamlit/secrets.toml がない場合のエラーハンドリング
        st.error(
            "APIキーが見つかりません。.streamlit/secrets.toml を設定してください。"
        )
        st.stop()

    # --- Streamlit UI ---
    grounding_prompt = f"""
    # 命令
    あなたは、非常に優秀なプロの編集者兼リサーチャーです。
    以下の「元の文章」の主張の信頼性を高めるため、**Google検索ツールを自律的に使用し、発見した客観的な統計データや事例を引用**してください。
    引用した場合は、必ず、検索で発見した実在する情報源を明記または示唆してください。例えば、「example.comによると、...」のような形で記述してください。 
    URLを創作してはいけません。
    なお、余計な文章（「承知しました」など）は一切含めないこと。

    # 元の文章
    ---
    {st.session_state["article_text"]}
    """

    if st.button("信頼性のある情報を組み込む"):
        with st.spinner("Google検索を参照して回答を生成中..."):
            # モデルのエンドポイントURL
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}"

            # APIに送信するデータ（ペイロード）
            payload = {
                "contents": [{"parts": [{"text": grounding_prompt}]}],
                "tools": [{"googleSearch": {}}],
            }

            headers = {"Content-Type": "application/json"}

            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload))

                response.raise_for_status()  # HTTPエラーがあれば例外を発生させる

                response_json = response.json()

                generated_text = response_json["candidates"][0]["content"]["parts"][0][
                    "text"
                ]

                st.markdown(generated_text)
                st.session_state["article_text"] = generated_text

            except requests.exceptions.HTTPError as http_err:
                st.error(f"HTTPエラーが発生しました: {http_err}")

                st.error(f"レスポンス内容: {response.text}")

            except Exception as e:
                st.error(f"予期せぬエラーが発生しました: {e}")

            # --- デバッグ情報 ---
            st.header("デバッグ情報")
            with st.expander("APIレスンスのJSON全体を表示"):
                st.json(response_json)

            # --- グラウンディング詳細 ---
            grounding_meta = response_json.get("candidates", [{}])[0].get(
                "groundingMetadata", {}
            )

            if grounding_meta:  # groundingMetadataが存在する場合のみ表示
                with st.expander("グラウンディング詳細（検索クエリと参照ソース）"):
                    # 検索クエリの表示
                    st.subheader("🤖 AIが実行した検索クエリ")
                    search_queries = grounding_meta.get("webSearchQueries", [])
                    if search_queries:
                        for query in search_queries:
                            st.info(query)
                    else:
                        st.write("検索クエリはありませんでした。")

                    st.markdown("---")

                    # 使用したソースの一覧表示
                    st.subheader("📚 参照したWebソース一覧")
                    grounding_chunks = grounding_meta.get("groundingChunks", [])
                    if grounding_chunks:
                        for i, chunk in enumerate(grounding_chunks):
                            title = chunk.get("web", {}).get("title", "タイトル不明")
                            uri = chunk.get("web", {}).get("uri", "#")
                            # Markdownを使い、タイトルをクリック可能なリンクにする
                            st.markdown(f"{i + 1}. **{title}** - [リンク]({uri})")
                    else:
                        st.write("参照ソースはありませんでした。")

            # --- ファクトチェック表示 ---
            st.header("ファクトチェック表示")
            st.caption("AIが生成した各文章とその根拠となったソース")

            grounding_supports = grounding_meta.get("groundingSupports", [])
            grounding_chunks = grounding_meta.get("groundingChunks", [])

            if not grounding_supports:
                st.warning(
                    "根拠情報(groundingSupports)がレスポンスに含まれていませんでした。"
                )
            else:
                # 取得した情報をループで表示
                for gs in grounding_supports:
                    # st.container(border=True) で各情報をカード化する
                    with st.container(border=True):
                        # 1. AIが生成した文章部分
                        text_segment = gs.get("segment", {}).get(
                            "text", "テキストが取得できませんでした。"
                        )
                        st.markdown(text_segment.strip())

                        st.markdown("---")  # 水平線で区切る

                        # 2. その文章の裏付けとなったソース
                        st.caption("ソース")

                        indices = gs.get("groundingChunkIndices", [])
                        if not indices:
                            st.write("この文章に対応するソースはありませんでした。")
                        else:
                            for gci in indices:
                                if gci < len(grounding_chunks):
                                    source_chunk = grounding_chunks[gci]
                                    # ...
                                else:
                                    st.warning(f"インデックス {gci} は範囲外です")
                                # grounding_chunksリストから該当するソース情報を取得
                                # st.info(f"アクセスしようとしているインデックス `gci`: `{gci}`")
                                title = source_chunk.get("web", {}).get(
                                    "title", "タイトル不明"
                                )
                                uri = source_chunk.get("web", {}).get("uri", "#")
                                # アイコンを付けて分かりやすく表示
                                st.markdown(f"🔗 **{title}** - [ソースへ]({uri})")

        # if st.button("信頼性のある情報を組み込む"):
        #     # ツール利用に適した高性能モデルを選択
        #     model_with_tool = genai.GenerativeModel(
        #         model_name="models/gemini-2.5-pro",
        #     )

        #     with st.spinner("AIがWeb検索を行い、記事の説得力を強化しています..."):
        #         rewrite_prompt = f"""
        #             # 命令
        #             あなたは、非常に優秀なプロの編集者兼リサーチャーです。
        #             以下の「元の文章」の主張の信頼性を高めるため、**Google検索ツールを自律的に使用し、発見した客観的な統計データや事例を引用**してください。
        #             引用した場合は、必ず文末などに**[出典: 〇〇](URL)**の形で、**検索で発見した実在する情報源**を明記してください。
        #             URLを創作してはいけません。

        #             # 元の文章
        #             ---
        #             {st.session_state["article_text"]}
        #             """

        #         # generate_contentの呼び出し
        #         try:
        #             grounding_tool = types.Tool(google_search=types.GoogleSearch())

        #             config = types.GenerateContentConfig(tools=[grounding_tool])

        #             response = client.models.generate_content(
        #                 model="gemini-2.5-flash",
        #                 contents="Who won the euro 2024?",
        #                 config=config,
        #             )

        #         except Exception as e:
        #             st.error("記事の調整中にエラーが発生しました。")
        #             st.exception(e)

    if "article_text" in st.session_state:
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
            if edited_text != st.session_state["article_text"]:
                st.session_state["article_text"] = edited_text

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
