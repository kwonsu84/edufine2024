from openai import OpenAI
import streamlit as st
from sentence_transformers import SentenceTransformer
from streamlit_chromadb_connection.chromadb_connection import ChromadbConnection



def get_db_data(user_question):
    configuration = {
        "client": "HttpClient",
        "host": "datalab.dscloud.me",
        "port": 8080,
    }
    
    client = st.connection(name="http_connection", type=ChromadbConnection, **configuration)

    #collection = client.get_or_create_collection("edufine2024")
    
    model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')
    
    question = "관련자료 : 대한민국 교육부와 그 예하 준정부기관인 한국교육학술정보원의 소관 하에 운영되고 있는 국가관리회계시스템. 명칭 중 Edu는 교육(Education)을, Fine은 재정(Finance)을 뜻한다. 주소는 각 시·도교육청 주소 앞에 klef.을 붙이면 된다. 해당 교육청 내부망에서만 접속할 수 있다."
    return question

#----------------------------------------------------------------------------------------------


st.set_page_config(
    page_title="K-에듀파인 업무관리 AI챗봇",
    layout="centered"
)

with st.container(border=True):
    st.subheader(":robot_face: :blue[K-에듀파인 업무관리 AI챗봇]")
    
    with st.chat_message("system", avatar="😄"):
        st.write("안녕하세요. 👋 K-에듀파인 업무관리에 대해서 궁금한 내용을 질문하세요. 관련자료(따라하기 메뉴얼, 교육동영상 등)를 기반으로 답변합니다. 시스템 오류는 사용자지원시스템을 통해 문의하셔야 됩니다.")
    
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo-0125"
    
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
            {"role": "system", "content": "너는 한국교육학술정보원의 'K-에듀파인 업무관리 시스템' 챗봇이다. '관련자료'에 기반해서만 답변한다. 질문자들은 'K-에듀파인 업무관리 시스템' 사용법에 대해서 질문한다. 너는 친절하고 정확하게 답변한다. 시스템 사용법 문의와 관련없는 사용자 질문에 대해서는 답변하지 않는다."}
            ] + st.session_state.messages + [
            {"role": "user", "content": get_db_data(prompt)}
            ]
            
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[                
                    {"role": m["role"], "content": m["content"]}
                    for m in messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})


with st.expander("2024년 따라하기 메뉴얼 다운로드"):
    st.write("2024년 업무관리 따라하기 메뉴얼을 다운로드 하세요.")
    #st.image("https://static.streamlit.io/examples/dice.jpg")
    st.page_link("http://www.google.com", label="2024년 업무관리 메뉴얼01", icon="🌎")


