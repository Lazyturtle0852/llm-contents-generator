import google.generativeai as genai
import streamlit as st


genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# AIモデルを準備（最新の高速モデルを指定）
model = genai.GenerativeModel('models/gemini-pro-latest')

# AIへの質問（プロンプト）
theme = "東京の魅力"

prompt = f"""
# 命令
あなたは、最新のLLMOに精通した、優秀なコンテンツマーケターです。
指定されたテーマに基づき、生成AIが内容を正確に理解し、引用・参照したくなるような、構造化された短いブログ記事を生成してください。

# テーマ
{theme}

# 構造と要件
- 全体で400字程度の文章を生成してください。
- 必ず以下の構造に従ってください。
  - 導入: 記事の概要を簡潔に記述。
  - 見出し1: 「伝統と革新が融合する都市」のような、記事の核心を表す見出し。
  - 見出し2: 「歴史を感じる下町情緒」のような、具体的な魅力を示す小見出し。
  - まとめ: 記事全体の要点を箇条書きで2つにまとめる。
- 読者が具体的なイメージを持てるように、「浅草の仲見世通り」や「渋谷のスクランブル交差点」のような固有名詞をいくつか含めてください。
"""
print("AIに質問を送信中...")

try:
    # AIに質問を送信して、答えをもらう
    response = model.generate_content(prompt)

    # AIからの答えを表示する
    print("--- AIからの返信 ---")
    print(response.text)
    print("--------------------")

except Exception as e:
    print("エラーが発生しました。APIキーが正しいか、確認してください。")
    print(e)