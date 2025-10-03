import google.generativeai as genai
import streamlit as st



try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])


    print("利用可能なモデルの一覧を取得します...")
    print("-" * 20)

    for model in genai.list_models():
        # generateContent（文章生成）が可能なモデルのみをフィルタリング
        if 'generateContent' in model.supported_generation_methods:
            print(model.name)

    print("-" * 20)
    print("上記のモデル名が、あなたのAPIキーで現在利用可能なモデルです。")

except Exception as e:
    print("モデル一覧の取得中にエラーが発生しました。")
    print("APIキーが有効か、またはGoogle CloudプロジェクトでGenerative Language APIが有効になっているか確認してください。")
    print(e)