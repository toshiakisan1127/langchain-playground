# langchain-playground
langChainで遊ぶだけのリポジトリ

### 起動方法

仮想環境の準備
```
. .venv/bin/activate
```

.venvファイルに以下の情報を書く
```
OPENAI_API_KEY=<APIキー>
OPENAI_API_MODEL=gpt-3.5-turbo
OPENAI_API_TEMPERATURE=0.5
```

サーバーの起動

```
streamlit run app.py --server.port 8080
```