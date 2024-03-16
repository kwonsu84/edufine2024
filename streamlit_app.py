from openai import OpenAI
import streamlit as st
from IPython.display import display
from IPython.display import Markdown
import textwrap
import pathlib
import requests
from urllib.parse import urlencode


def get_db_data(user_question):
    base_url = "http://datalab.dscloud.me:9000"
    params = {
        'user_question': user_question
    }
      
    encoded_params = urlencode(params)
    url = f"{base_url}?{encoded_params}"
    response = requests.get(url)
      
    return response.text

#----------------------------------------------------------------------------------------------


st.set_page_config(
    page_title="K-에듀파인 업무관리 AI챗봇",
    layout="centered"
)

with st.container(border=True):
    st.subheader(":robot_face: :blue[K-에듀파인 업무관리 AI챗봇]")
    
    with st.chat_message("system", avatar="😄"):
        st.write("안녕하세요! 👋 K-에듀파인 업무관리에 대해서 궁금한 내용을 질문하세요. 관련자료를 기반으로 답변합니다. 시스템 오류는 사용자지원시스템을 통해 문의해야 됩니다.")
    
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
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
            #RAG형식으로 구현!
            messages = [
            {"role": "system", "content": "너는 한국교육학술정보원의 'K-에듀파인 업무관리 시스템' 챗봇이다. 너는 '2024년 기준으로 제작된 관련자료(따라하기 메뉴얼, 교육동영상 대본)'를 제공받는다. 하지만 '관련자료'를 시용자(질문자)는 볼 수 있다. 따라서 답변에 관련자료 어디를 보라는 답변은 하면 안된다."},
            {"role": "system", "content": "너의 답변은 읽기 쉬운 형식으로 작성한다. 질문자들은 'K-에듀파인의 업무관리 시스템' 사용법에 대해서 질문한다. 시스템 사용법 문의와 관련없는 질문에 대해서는 답변하지 않는다. 정확한 답변만 작성하고 관련자료에 내용이 없는 질문에 대해서는 알지 못한다고 답한다."},
            {"role": "system", "content": "너는 시용자(질문자)가 시스템 오류나 개선사항에 대한 질문을 할 경우 사용자지원서비스(help.klef.go.kr)에 접속하여 글을 남기면 도움을 받을 수 있다고 답변한다. 사용자지원서비스는 교육부 및 교육청 관계자만 이용할 수 있는 서비스이다."},
            #{"role": "system", "content": "반드시 답변의 마지막에 사용자(질문자)가 추가 내용을 확인할 수 있도록 너의 답변과 관련성 높은 관련자료들의 '출처'와 '출처 내 위치'를 포함한다. 답변 마지막에 한줄 뛰고 다음과 같은 형식으로 출력한다. '출처: <관련자료의 출처>, 위치: <관련자료의 출처 내 위치>', 만약 제공할 출처와 위치가 여러개라면 한줄씩 나열한다."},
            {"role": "system", "content": "관련자료 : " + get_db_data(prompt)}
            ] + st.session_state.messages
            st.experimental_rerun()
            stream = client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=[                
                    {"role": m["role"], "content": m["content"]}
                    for m in messages
                ],
                stream=True,
                temperature=0.0
            )
            
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
        

with st.expander("관련자료"):
    st.write("1. 2024년 업무관리 따라하기 메뉴얼")
    #st.image("https://static.streamlit.io/examples/dice.jpg")
    st.page_link("http://www.google.com", label="2024년 업무관리 메뉴얼01", icon="🌎")
    st.write("2. 2024년 업무관리 유튜브 교육동영상")


