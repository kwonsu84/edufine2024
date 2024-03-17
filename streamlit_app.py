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
        st.write("안녕하세요! 👋 K-에듀파인 업무관리에 대해서 궁금한 내용을 질문하세요.")

    with st.chat_message("system", avatar="❗"):
        st.write("이 챗봇은 '실험버전'입니다. 답변에 오류가 있을 수 있습니다.")
    
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
            messages = [
            {"role": "system", "content": """
            # 이 챗봇(ChatBot)에 대하여

            ## 역할
            너는 한국교육학술정보원(KERIS)의 'K-에듀파인 업무관리 시스템' 챗봇이다. 
            
            ## '업무관리 교육자료'에 대하여
            - 너는 '2024년 기준으로 업데이트된 '업무관리 교육자료'(따라하기 메뉴얼, 교육동영상 대본)'를 시용자(질문자)의 질문에 따라 RAG(Retrieval-Augmented Generation)방식으로 조회하여 제공받는다.
            - 너에게만 '업무관리 교육자료'를 제공하고 시용자(질문자)는 볼 수 없다. 따라서 시용자(질문자)에게 '업무관리 교육자료'를 언급하지 않는다.

            ## '업무관리 교육자료'의 형식
            - '업무관리 교육자료'의 각각은 '출처', '출처 내 위치', '내용'으로 구성되어 있다.
            - '\n' 문자는 한줄 뛰어져 있다는 의미다.
            - 출처에 '[따라하기]'라고 쓰여져 있으면 사용자메뉴얼 자료고, '[유튜브]'라고 쓰여져 있으면 교육용동영상 자료이다.

            ## 답변의 형식
            - 너의 답변은 읽기쉬운 형식(예 : markdown)으로 작성한다. 시용자(질문자)들은 'K-에듀파인의 업무관리 시스템' 사용법에 대해서 질문한다.
            - 시스템 사용법 문의와 관련없는 질문에 대해서는 답변하지 않는다. 정확한 답변만 작성하고 '업무관리 교육자료'에 내용이 없는 질문에 대해서는 알지 못한다고 답한다.
            - 너는 시용자(질문자)가 시스템 오류나 개선사항에 대한 질문을 할 경우 사용자지원서비스(help.klef.go.kr)에 접속하여 글을 남기면 도움을 받을 수 있다고 답변한다.
            """},
            {"role": "system", "content": "'업무관리 교육자료' : " + get_db_data(prompt)},
            {"role": "system", "content": """
            ## 현재 시스템 오류 리포트 자료
            - 

            ## 시스템 개선예정 자료
            -  
            """}
            ] + st.session_state.messages
            
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
        st.experimental_rerun()

st.caption("▫︎ 이 챗봇은 '2024년 업무관리 따라하기 메뉴얼', '업무관리 교육용동영상' 등의 데이터로 학습하였습니다.")
st.caption("▫︎ 학습데이터가 부족한 영역에 대해선 오답을 말할 수 있습니다.")
st.caption("▫︎ 현재 실험버전으로 정식으로 서비스하는 것이 아닙니다. 언제든 서비스가 종료될 수 있습니다.")
#with st.expander("관련자료"):
#    st.write("2024년 업무관리 따라하기 메뉴얼")
    #st.image("https://static.streamlit.io/examples/dice.jpg")
#    st.page_link("https://www.youtube.com/playlist?list=PLnNTGUWLwu1vNmfNT8Oq7_m-uzhquAEFZ", label="2024년 업무관리 교육동영상", icon="🌎")
#    st.page_link("https://help.klef.go.kr/keris_ui/main.do", label="K-에듀파인 사용자지원서비스", icon="🌎")

