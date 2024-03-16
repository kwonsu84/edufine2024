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
            #RAG형식으로 구현!
            messages = [
            {"role": "system", "content": "너는 한국교육학술정보원의 'K-에듀파인 업무관리 시스템' 챗봇이다. 너는 '2024년 기준으로 업데이트된 관련자료(따라하기 메뉴얼, 교육동영상 대본)'를 제공받는다. 하지만 너에게 '관련자료'는 시용자(질문자)는 볼 수 있다. 따라서 답변에 관련자료 어디를 보라는 답변은 하면 안된다."},
            {"role": "system", "content": "너의 답변은 읽기쉬운 형식(예 : markdown)으로 작성한다. 시용자(질문자)들은 'K-에듀파인의 업무관리 시스템' 사용법에 대해서 질문한다. 시스템 사용법 문의와 관련없는 질문에 대해서는 답변하지 않는다. 정확한 답변만 작성하고 관련자료에 내용이 없는 질문에 대해서는 알지 못한다고 답한다."},
            {"role": "system", "content": "너는 시용자(질문자)가 시스템 오류나 개선사항에 대한 질문을 할 경우 사용자지원서비스(help.klef.go.kr)에 접속하여 글을 남기면 도움을 받을 수 있다고 답변한다. "},
            #{"role": "system", "content": "반드시 답변의 마지막에 사용자(질문자)가 추가 내용을 확인할 수 있도록 너의 답변과 관련성 높은 관련자료들의 '출처'와 '출처 내 위치'를 포함한다. 답변 마지막에 한줄 뛰고 다음과 같은 형식으로 출력한다. '출처: <관련자료의 출처>, 위치: <관련자료의 출처 내 위치>', 만약 제공할 출처와 위치가 여러개라면 한줄씩 나열한다."},
            {"role": "system", "content": "관련자료 : " + get_db_data(prompt)}
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

st.caption("□ 이 챗봇은 '2024년 업무관리 따라하기 메뉴얼', '교육용동영상(유튜브 탑재)', '사용자지원서비스 질의/응답' 데이터로 학습하였습니다. 학습데이터가 부족한 영역에 대한 질문의 경우 잘못된 대답을 할 가능성이 있습니다.")
st.caption("□ 현재 실험버전으로 정식으로 서비스하는 것이 아닙니다.")
#with st.expander("관련자료"):
#    st.write("2024년 업무관리 따라하기 메뉴얼")
    #st.image("https://static.streamlit.io/examples/dice.jpg")
#    st.page_link("https://www.youtube.com/playlist?list=PLnNTGUWLwu1vNmfNT8Oq7_m-uzhquAEFZ", label="2024년 업무관리 교육동영상", icon="🌎")
#    st.page_link("https://help.klef.go.kr/keris_ui/main.do", label="K-에듀파인 사용자지원서비스", icon="🌎")

