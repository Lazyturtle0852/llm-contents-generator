import streamlit as st
import requests
import json


st.set_page_config(page_title="Gemini Grounding Demo", page_icon="🔎")
st.title("🔎 Grounding powered by Gemini")


# --- APIキーの設定 ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]

except FileNotFoundError:
    # ローカル環境などで .streamlit/secrets.toml がない場合のエラーハンドリング
    st.error("APIキーが見つかりません。.streamlit/secrets.toml を設定してください。")
    st.stop()


# --- Streamlit UI ---
prompt = st.text_input(
    "質問を入力してください:", "2025年の自民党総裁選挙で勝利したのは誰ですか？"
)


if st.button("生成する"):
    if not prompt:
        st.warning("質問を入力してください。")

    else:
        with st.spinner("Google検索を参照して回答を生成中..."):
            # モデルのエンドポイントURL

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}"

            # APIに送信するデータ（ペイロード）

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
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

    if not grounding_supports:
        st.warning("根拠情報(groundingSupports)がレスポンスに含まれていませんでした。")
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
                        # grounding_chunksリストから該当するソース情報を取得
                        source_chunk = grounding_chunks[gci]
                        title = source_chunk.get("web", {}).get("title", "タイトル不明")
                        uri = source_chunk.get("web", {}).get("uri", "#")
                        # アイコンを付けて分かりやすく表示
                        st.markdown(f"🔗 **{title}** - [ソースへ]({uri})")
