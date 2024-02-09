from openai import OpenAI
import streamlit as st


st.set_page_config(
    page_title="K-에듀파인 업무관리 AI챗봇",
    layout="centered"
)


st.subheader(":robot_face: :blue[K-에듀파인 업무관리 AI챗봇]")

with st.chat_message("assistant"):
    st.write("👋 K-에듀파인 업무관리에 대해서 궁금한 내용을 모두 입력해주세요. 따라하기 메뉴얼을 기반으로 답변을 전달합니다.")

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
        #RAG형식으로 구현!
        messages = [
        {"role": "system", "content": "당신은 챗봇입니다. 관련자료에 기반해서만 답변합니다."}
        ] + st.session_state.messages + [
        {"role": "user", "content": "관련자료 : 대한민국 교육부와 그 예하 준정부기관인 한국교육학술정보원의 소관 하에 운영되고 있는 국가관리회계시스템. 명칭 중 Edu는 교육(Education)을, Fine은 재정(Finance)을 뜻한다. 주소는 각 시·도교육청 주소 앞에 klef.을 붙이면 된다. 해당 교육청 내부망에서만 접속할 수 있다."}
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


st.write("TEST")


