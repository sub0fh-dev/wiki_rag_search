import streamlit as st
from openai import OpenAI
from elasticsearch import Elasticsearch

# ===============================
# 🔧 초기 설정
# ===============================
st.set_page_config(
    page_title="WikiRAG 🇰🇷",
    page_icon="🌏",
    layout="centered"
)

# OpenAI 클라이언트
client = OpenAI(api_key=st.secrets["api_key"])

# Elasticsearch 클라우드 연결
ELASTIC_CLOUD_ID = st.secrets["elastic_cloud_key"]
ELASTIC_API_KEY = st.secrets["elastic_api_key"]

# Elasticsearch 클라이언트 생성
es = Elasticsearch(
    cloud_id=ELASTIC_CLOUD_ID,
    api_key=ELASTIC_API_KEY
)

# ===============================
# 🎨 Streamlit UI
# ===============================
st.markdown("<h1 style='text-align:center;'>🌏 위키 기반 한글 AI Q&A</h1>", unsafe_allow_html=True)
st.caption("**Semantic Search + RAG + OpenAI** — 영문 위키피디아를 기반으로 한국어로 답변합니다 🧠")

st.markdown("---")

with st.form("query_form"):
    question = st.text_input(
        "❓ 질문을 입력하세요 (한글/영문 모두 가능)",
        placeholder="예: 대서양은 몇 번째로 큰 바다인가?"
    )
    submitted = st.form_submit_button("🚀 검색 및 답변 생성")

# ===============================
# 🧠 검색 및 RAG 로직
# ===============================
if submitted and question:
    with st.spinner("🤖 Kevin AI가 검색 중입니다... 잠시만 기다려주세요!"):
        # 1️⃣ 질문 임베딩 생성
        embedding = client.e
