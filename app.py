import os

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder

load_dotenv()

def create_agent_chain(model_name: str):
    """
    指定されたモデル名を使用してエージェントチェーンを作成し、対話エージェントを初期化する。
    
    この関数は、指定されたAIモデルを使用してOpenAI Chat APIを設定し、必要なツールとメモリをロードしてエージェントを初期化します。
    会話履歴を保持するためのメモリと、DuckDuckGo検索やWikipedia検索などのツールを組み込みます。
    
    Parameters:
        model_name (str): 使用するAIモデルの名前。
    
    Returns:
        Agent: 初期化されたエージェントチェーン。
    
    環境変数:
        OPENAI_API_TEMPERATURE: モデルの応答生成に使用する温度パラメータ。
    
    例外:
        KeyError: 必要な環境変数が設定されていない場合に発生。
    
    副作用:
        - ChatOpenAI インスタンスが作成され、指定されたモデルと温度設定で初期化される。
        - エージェントチェーンがツールとメモリ設定を含む形で初期化される。
    
    例:
        >>> agent_chain = create_agent_chain("gpt-3.5-turbo")
        >>> print(type(agent_chain))
        <class 'Agent'>
    """
    chat = ChatOpenAI(
            model_name = model_name,
            temperature = os.environ["OPENAI_API_TEMPERATURE"],
            streaming = True
        )
    
    # OpenAI Fuctions AgentのプロンプトにMemoryの会話履歴を追加するための設定
    agent_kwargs = {"extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")]}
    memory = ConversationBufferMemory(memory_key="memory", return_messages=True)
    tools = load_tools(["ddg-search", "wikipedia"])
    return initialize_agent(tools, chat, agent=AgentType.OPENAI_FUNCTIONS, agent_kwargs=agent_kwargs, memory=memory)

def switch_to_gpt4():
    """
    Streamlitアプリケーションで使用するAIモデルをGPT-4に切り替える。
    
    この関数は、環境変数からGPT-4モデル名を取得し、Streamlitのセッション状態を更新して
    モデルをGPT-4に切り替えます。会話履歴とエージェントチェーンもリセットされ、
    ユーザーに切り替えが完了したことが通知されます。
    
    環境変数:
        OPENAI_API_MODEL_GPT4: 使用するGPT-4モデルの名前を指定する環境変数。
    
    例外:
        KeyError: 環境変数 `OPENAI_API_MODEL_GPT4` が設定されていない場合に発生。
    
    副作用:
        - st.session_state.model_name が更新される。
        - st.session_state.messages が空のリストにリセットされる。
        - st.session_state.agent_chain が新しいエージェントチェーンに更新される。
        - ユーザーインターフェースにメッセージが表示される。
    
    例:
        >>> switch_to_gpt4()
        GPT4に切り替えました！
    """
    st.session_state.model_name  = os.environ["OPENAI_API_MODEL_GPT4"]
    # 会話の途中でモデルを変える仕様は面倒なので全消去
    st.session_state.messages = []
    # agent_chainも初期化することで、エージェントが持っている会話履歴も削除
    st.session_state.agent_chain = create_agent_chain(st.session_state.model_name)
    st.write('GPT4に切り替えました！')

st.title("GPT3.5と4の違いを試せるよ！")

# 始めのモデルはgpt3.5にしておく
model_name = os.environ["OPENAI_API_MODEL"]
if "model_name" not in st.session_state:
    st.session_state.model_name = model_name
    
# GPT4に切り替えるロジックをここに集約
if st.button('GPT4に切り替える'):
    switch_to_gpt4()
prompt = st.chat_input("なんか用か ?")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    # ロールごとに保存されているテキストを表示
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    # ユーザーのアイコンでpromptをマークダウンとして整形して表示
    with st.chat_message("user"):
        st.markdown(prompt)
    # AIのアイコンで固定の応答を用意してマークダウン形式で返す
    with st.chat_message("assistant"):
        callback = StreamlitCallbackHandler(st.container())
        if "agent_chain" not in st.session_state:
            st.session_state.agent_chain = create_agent_chain(st.session_state.model_name)
        response = st.session_state.agent_chain.run(prompt, callbacks=[callback])
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    
