import streamlit as st

import requests

import json


st.set_page_config(page_title="Gemini Grounding Demo", page_icon="🔎")


st.title("🔎 Gemini with Grounding (Google Search)")


# --- APIキーの設定 ---

try:
    # Streamlit Cloudでシークレットを管理する場合

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

                # --- ここからが変更・追加部分 ---

                # 1. 生成されたテキストを表示

                generated_text = response_json["candidates"][0]["content"]["parts"][0][
                    "text"
                ]

                st.markdown(generated_text)

                # 2. JSONから典拠（参照元）情報を取得して表示

                st.subheader("参照元ソース（メタデータ）")

                citation_metadata = response_json["candidates"][0].get(
                    "citationMetadata"
                )

                st.write(citation_metadata)

                if citation_metadata and citation_metadata.get("citationSources"):
                    citations = citation_metadata["citationSources"]

                    for i, source in enumerate(citations):
                        uri = source.get("uri")

                        if uri:
                            # aタグで直接リンクを表示

                            st.markdown(
                                f"{i + 1}. <a href='{uri}' target='_blank'>{uri}</a>",
                                unsafe_allow_html=True,
                            )

                else:
                    st.write("参照元ソースはAPIレスポンスに含まれていませんでした。")

            except requests.exceptions.HTTPError as http_err:
                st.error(f"HTTPエラーが発生しました: {http_err}")

                st.error(f"レスポンス内容: {response.text}")

            except Exception as e:
                st.error(f"予期せぬエラーが発生しました: {e}")

st.header("デバッグ情報")
st.write("APIレスポンスのJSON全体:")
st.json(response_json if "response_json" in locals() else {})

st.write("現在の`st.session_state`の中身:")
st.json(st.session_state)
