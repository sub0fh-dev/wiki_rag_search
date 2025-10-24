import os
import pandas as pd
import streamlit as st
from openai import OpenAI
from elasticsearch import Elasticsearch

# ===============================
# OpenAI & Elasticsearch 설정
# ===============================
client = OpenAI(api_key=st.secrets["api_key"])

ELASTIC_CLOUD_ID = st.secrets["elastic_cloud_key"]
ELASTIC_API_KEY = st.secrets["elastic_api_key"]

es = Elasticsearch(
    cloud_id=ELASTIC_CLOUD_ID,
    api_key=ELASTIC_API_KEY
)

# 연결 테스트
try:
    es_info = es.info()
    print("Elasticsearch 연결 성공!")
except Exception as e:
    st.error("Elasticsearch 연결 실패: " + str(e))

# ===============================
# Streamlit UI
# ===============================
st.set_page_config(page_title="Kevin AI Wiki", layout="wide")

st.markdown("<h1 style='text-align:center; color: #4B0082;'>한글로 답변하는 AI</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center; color: #6A5ACD;'>영문 위키 기반 RAG (Retrieval Augmented Generation)</h3>", unsafe_allow_html=True)
st.markdown("---")

st.markdown("""
영문 Wikipedia 데이터를 활용하여 질문에 한국어로 답변합니다.  
예시 질문: 
- 대서양은 몇 번째로 큰 바다인가?
- 대한민국의 수도는?
- 이순신의 출생년도는?
- 도요타에서 가장 많이 팔리는 차는?
""")

st.markdown("""
데이터 출처:  
[Wiki Embeddings 샘플 데이터](https://cdn.openai.com/API/examples/data/vector_database_wikipedia_articles_embedded.zip)  
데이터 설명: [Weaviate Tutorial](https://weaviate.io/developers/weaviate/tutorials/wikipedia)  
데이터 건수: 25,000건
""")

st.markdown("---")

# ===============================
# 질문 입력 폼
# ===============================
with st.form("question_form"):
    question = st.text_input("질문을 입력하세요")
    submit = st.form_submit_button("질문하기")

if submit and question:
    with st.spinner("Kevin AI가 답변 준비 중..."):
        # 1️⃣ 한국어 → 영어 번역
        translated = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": "Translate the following Korean question into English: " + question
                }
            ]
        )
        english_question = translated.choices[0].message.content
        print("번역:", english_question)

        # 2️⃣ 질문 임베딩 생성
        question_embedding = client.embeddings.create(
            input=[english_question],
            model="text-embedding-ada-002"
        ).data[0].embedding

        # 3️⃣ Elasticsearch 검색
        try:
            response = es.search(
                index="wikipedia_vector_index",
                knn={
                    "field": "content_vector",
                    "query_vector": question_embedding,
                    "k": 10,
                    "num_candidates": 100
                }
            )
        except Exception as e:
            st.error("Elasticsearch 검색 실패: " + str(e))
            st.stop()

        # 4️⃣ 최상위 문서 텍스트 추출
        top_hit_summary = response['hits']['hits'][0]['_source']['text']

        # 5️⃣ GPT로 한국어 요약/답변 생성
        summary = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant for question-answering tasks. Use the retrieved context to answer concisely in Korean. If unknown, say '제가 가진 정보로는 알 수 없습니다.'"
                },
                {
                    "role": "user",
                    "content": f"Question: {english_question} Context: {top_hit_summary} Answer in Korean in maximum 3 sentences."
                }
            ]
        )

        # 6️⃣ 답변 출력
        st.markdown("### 💡 Kevin AI 답변")
        st.info(summary.choices[0].message.content)

        # 7️⃣ 검색된 문서 리스트
        st.markdown("### 🔍 관련 Wiki 문서")
        for hit in response['hits']['hits']:
            title = hit['_source']['title']
            url = hit['_source']['url']
            score = hit['_score']
            st.markdown(f"- [{title}]({url}) (Score: {score:.2f})")
