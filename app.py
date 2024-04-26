import os

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain_community.callbacks import StreamlitCallbackHandler

load_dotenv()

def create_agent_chain():
    chat = ChatOpenAI(
            model_name = os.environ["OPENAI_API_MODEL"],
            temperature = os.environ["OPENAI_API_TEMPERATURE"],
            streaming = True
        )
    tools = load_tools(["ddg-search", "wikipedia"])
    return initialize_agent(tools, chat, agent=AgentType.OPENAI_FUNCTIONS)

st.title("langchain練習用のUI")

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
        agent_chain = create_agent_chain()
        response = agent_chain.invoke(prompt, callbacks=[callback])
        st.markdown(response["output"])
    st.session_state.messages.append({"role": "assistant", "content": response["output"]})
    
