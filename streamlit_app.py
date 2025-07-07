from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import ChatMessage
from langchain_openai import ChatOpenAI
import streamlit as st

import os
import nest_asyncio
from langchain.smith import RunEvalConfig, run_on_dataset

import requests
from urllib.parse import urlencode

nest_asyncio.apply()

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_TRACING_V2"] = st.secrets["LANGCHAIN_TRACING_V2"]
os.environ["LANGCHAIN_ENDPOINT"] = st.secrets["LANGCHAIN_ENDPOINT"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["LANGCHAIN_PROJECT"]

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

def get_db_data(user_question):
    base_url = "http://datalab.dscloud.me:9000/edufine"
    params = {
        'user_question': user_question
    }
      
    encoded_params = urlencode(params)
    url = f"{base_url}?{encoded_params}"
    response = requests.get(url)
      
    return response.text


#with st.sidebar:

st.set_page_config(
    page_title="K-에듀파인 업무관리 AI챗봇",
    layout="wide"
)


st.subheader(":robot_face: :blue[업무관리 AI챗봇](파일럿)")

#if "messages" not in st.session_state:
with st.chat_message("system", avatar="😄"):
    st.write("안녕하세요! 👋 아래 샘플 질문을 참고해서 궁금한 내용을 질문하세요.")

#with st.chat_message("system", avatar="❗"):
#    st.write("이 챗봇은 '실험버전'입니다.")

with st.chat_message("user"):
    st.write("수신문서를 배부하려는데 어디로 보내야 될지 모르겠는데?")

with st.chat_message("assistant"):
    st.write("수신문서를 배부할 때 담당 부서가 불명확한 경우, '담당부서확인' 기능을 사용하여 해당 부서로 확인 요청을 할 수 있습니다.")

with st.chat_message("user"):
    st.write("중단한 문서도 기록물 이관 대상인가요?")

with st.chat_message("assistant"):
    st.write("네, 중단한 문서도 기록물 이관 대상입니다. 문서 중단 처리는 문서번호가 등록되지 않지만, 완료문서와 동일하게 취급하여 기록물이관 대상이 됩니다.")


#첫 실행일 때
if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    if message["role"] in ["user", "assistant"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


if prompt := st.chat_input("궁금한 내용을 입력하세요!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    #챗봇 지시사항
    st.session_state.messages.append({"role": "system", "content": """
    # 이 챗봇(ChatBot)에 대하여
    
    ## 역할
    너는 한국교육학술정보원(KERIS)의 'K-에듀파인 업무관리 시스템' 챗봇이다. 
    
    ## '업무관리 교육자료'에 대하여
    - 너는 '2024년 기준으로 업데이트된 '업무관리 교육자료'(따라하기 메뉴얼, 교육동영상 대본)'를 시용자(질문자)의 질문에 따라 RAG(Retrieval-Augmented Generation)방식으로 조회하여 제공받는다.
    - 너에게만 '업무관리 교육자료'를 제공하고 시용자(질문자)는 볼 수 없다. 따라서 시용자(질문자)에게 '업무관리 교육자료'를 언급하지 않는다.
    
    ## '업무관리 교육자료'의 형식
    - '업무관리 교육자료'의 각각은 '출처', '출처 내 위치', '내용'으로 구성되어 있다.
    - '\n' 문자는 개행(다음줄로 이동)을 의미한다.
    - 출처에 '따라하기'가 포함되어 있으면 사용자메뉴얼 자료고, '유튜브'가 포함되어 있으면 교육용동영상 자료이다. '사용자지원서비스' 및 '에듀콜센터'가 포함되어 있으면 전국 교육청 및 학교 사용자들이 질문을 남긴 것에 대한 답변을 남긴 자료이다.
    
    ## 답변의 형식
    - 너의 답변은 읽기쉬운 형식(예 : markdown)으로 작성한다. 시용자(질문자)들은 'K-에듀파인의 업무관리 시스템' 사용법에 대해서 질문한다.
    - 시스템 사용법 문의와 관련없는 질문에 대해서는 답변하지 않는다. 정확한 답변만 작성하고 '업무관리 교육자료'에 내용이 없는 질문에 대해서는 알지 못한다고 답한다.
    - 너는 시용자(질문자)가 시스템 오류나 개선사항에 대한 질문을 할 경우 사용자지원서비스(help.klef.go.kr)에 접속하여 글을 남기면 도움을 받을 수 있다고 답변한다.
    
    ## 현재 시스템 오류 리포트 자료
    - 
    """})
    
    st.session_state.messages.append({"role": "system", "content": """
    ## 업무관리 교육자료 : 
    """ + get_db_data(prompt)})
    
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        stream_handler = StreamHandler(st.empty())
        llm = ChatOpenAI(openai_api_key=os.environ["OPENAI_API_KEY"], model="gpt-4.1-mini", temperature=0.0, streaming=True, callbacks=[stream_handler])
        response = llm.invoke(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": response.content})

        if st.session_state:
            if "messages" in st.session_state:
                if st.session_state.messages:
                    st.session_state.messages = [msg for msg in st.session_state.messages if msg.get("role") != "system"]
            
