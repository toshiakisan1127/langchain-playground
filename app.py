import os

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

load_dotenv()

st.title("langchain練習用のUI")

prompt = st.chat_input("なんか用か ?")
print(prompt);

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
        chat = ChatOpenAI(
            model_name = os.environ["OPENAI_API_MODEL"],
            temperature = os.environ["OPENAI_API_TEMPERATURE"]
            )
        messages = [HumanMessage(content = prompt)]
        response = chat(messages)
        st.markdown(response.content)
    st.session_state.messages.append({"role": "assistant", "content": response.content})
        