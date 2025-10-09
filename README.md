# 📝 LLMコンテンツ生成アシスタント

## 1. プロジェクト概要 (Project Overview)
AIとの対話とWeb検索による事実補強を組み合わせ、SaaS企業がビジネス目標を達成するための、戦略的なB2Bコンテンツを高速に生成・改善する編集パートナーです。

## 2. 背景と目的 (Background and Goal)
To be updated

## 3. システムアーキテクチャ (System Architecture)
本アプリケーションは、`main.py`をエントリーポイントとし、「記事生成」と「編集・調整」の2つの主要機能を`generation.py`と`edit.py`にモジュール化しています。 タブ間のデータ連携は`st.session_state`を介して行われます。

![アーキテクチャ概要図](LLMOサービスアーキテクチャ-2025-10-08-082750.png)

## 4. 機能一覧 (Features)
本システムは、以下の主要な機能を備えています。

- **要件の事前指定**: 複数のキーワード、記事の概要、文体、おおよその文字数を事前に指定できます。
- **段階的なコンテンツ生成**:
  1.  まず、入力された要件に基づき、AIが10個のタイトル案を生成します。
  2.  ユーザーがその中からタイトルを選択すると、そのタイトルに沿った記事本文のドラフトが生成されます。
- **AIによる反復的なリライト機能**: 生成された記事に対し、ユーザーが自然言語で指示を与えることで、AIが文章を対話的に推敲・調整します。
- **Web検索による事実補強機能（グラウンディング）**: AIが自律的にWeb検索を行い、生成する記事に客観的なデータや事例を引用し、出典を明記することで、コンテンツの信頼性・説得力を向上させます。
- **リアルタイムプレビュー付き編集機能**: ユーザーは、AIが生成・調整した記事を、Markdownのリアルタイムプレビューを見ながら自由に編集できます。

## 5. 技術スタック (Tech Stack)
- **言語**: Python
- **フレームワーク**: Streamlit
- **AIモデル**: Google Gemini API (REST API経由でのGrounding機能を含む)
- **バージョン管理**: Git / GitHub
- **主要ライブラリ**: `requests`

## 6. 使い方 (Usage)
本アプリケーションをローカル環境で実行するには、以下の手順に従ってください。

1.  **リポジトリのクローン:**
    ```bash
    git clone [https://github.com/lazyturtle0852/llm-contents-generator.git](https://github.com/lazyturtle0852/llm-contents-generator.git)
    cd llm-contents-generator
    ```

2.  **仮想環境の構築と有効化:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **必要なライブラリのインストール:**
    `requirements.txt`ファイルに記載されたライブラリをインストールします。
    ```bash
    pip install -r requirements.txt
    ```

4.  **APIキーの設定:**
    `.streamlit`フォルダ内に`secrets.toml`ファイルを作成し、以下のようにご自身のGoogle Gemini APIキーを記述してください。
    ```toml
    GEMINI_API_KEY = "ここにあなたのAPIキーを貼り付け"
    ```

5.  **アプリケーションの起動:**
    ```bash
    streamlit run main.py
    ```
    起動後、Webブラウザで表示されたローカルURLにアクセスしてください。

なお、[https://llm-contents-generator.streamlit.app/](https://llm-contents-generator.streamlit.app/)からも利用可能です。