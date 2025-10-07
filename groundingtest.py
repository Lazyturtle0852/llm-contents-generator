import streamlit as st
import google.generativeai as genai
from google.genai import types
import requests
import json

st.set_page_config(page_title="Gemini Grounding Demo", page_icon="🔎")

st.title("🔎 Gemini with Grounding (Google Search)")

# --- APIキーの設定（新しい方法） ---
# ここで client は使いません。
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(
        "APIキーの設定に失敗しました。`.streamlit/secrets.toml`ファイルを確認してください。"
    )
    st.exception(e)
    st.stop()

# モデル名をユーザー様が使いたい 'gemini-2.5-pro' に設定
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={st.secrets['GEMINI_API_KEY']}"

# APIに送信するデータ（ペイロード）
payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": "2025年の自民党総裁選挙で勝利したのは誰ですか？リンクも回答に含めること。"
                }
            ]
        }
    ],
    "tools": [{"googleSearch": {}}],
}

headers = {"Content-Type": "application/json"}

print("\n🔄 APIにリクエストを送信します...")
try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    response_json = response.json()
    generated_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
    print("--- 生成結果 ---")
    print(generated_text)
    print("------------------")
except requests.exceptions.HTTPError as http_err:
    print(f"🛑 HTTPエラーが発生しました: {http_err}")
    print(f"レスポンス内容: {response.text}")
except Exception as e:
    print(f"🛑 予期せぬエラーが発生しました: {e}")

st.write(generated_text)
