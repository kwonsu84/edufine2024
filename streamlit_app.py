from openai import OpenAI
import streamlit as st

st.set_page_config(
    page_title="K-에듀파인 업무관리 AI 챗봇",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None
)
st.subheader(":robot_face: K-에듀파인 업무관리")
st.caption(':grinning: _따라하기 메뉴얼을 학습하여 답변의 정확성을 높였습니다._')


with st.chat_message("assistant"):
    st.write("👋 안녕하세요. K-에듀파인 업무관리에 대해서 궁금한 내용을 모두 입력해주세요.")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo-1106"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



if prompt := st.chat_input("궁금한 내용을 입력하세요!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
