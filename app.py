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

client = OpenAI(api_key=st.secrets["api_key"])

ELASTIC_CLOUD_ID = st.secrets["elastic_cloud_key"]
ELASTIC_API_KEY = st.secrets["elastic_api_key"]

es = Elasticsearch(
    cloud_id=ELASTIC_CLOUD_ID,
    api_key=ELASTIC_API_KEY
)

# ===============================
# 🎨 UI 구성
# ===============================
st.markdown("<h1 style='text-align:center;'>🌏 위키 기반 한글 AI Q&A</h1>", unsafe_allow_html=True)
st.caption("**Semantic Search + RAG + OpenAI** — 영문 위키피디아를 기반으로 한국어로 답변합니다 🧠")

st.markdown("---")

with st.form("query_form"):
    question = st.text_input("❓ 질문을 입력하세요 (한글/영문 모두 가능)", placeholder="예: 대서양은 몇 번째로 큰 바다인가?")
    submitted = st.form_submit_button("🚀 검색 및 답변 생성")

# ===============================
# 🧠 처리 로직
# ===============================
if submitted and question:
    with st.spinner("🤖 Kevin AI가 검색 중입니다... 잠시만 기다려주세요!"):
        
        # 1️⃣ 질문 임베딩
        embedding = client.embeddings.create(
            model="text-embedding-3-large",
            input=[question]
        ).data[0].embedding

        # 2️⃣ Elasticsearch 시맨틱 검색
        response = es.search(
            index="wikipedia_vector_index",
            knn={
                "field": "content_vector",
                "query_vector": embedding,
                "k": 5,
                "num_candidates": 50
            }
        )

        hits = response["hits"]["hits"]
        contexts = "\n\n".join([hit["_source"]["text"] for hit in hits])

        # 3️⃣ GPT 기반 RAG 답변 생성
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 영문 위키 문서를 활용해 한국어로 짧고 정확하게 답변하는 AI야. 모르면 '잘 모르겠습니다.'라고 답변해."},
                {"role": "user", "content": f"문맥:\n{contexts}\n\n질문: {question}\n\n3문장 이내로 한국어로 답변해줘."}
            ]
        )

        answer = completion.choices[0].message.content

        # ===============================
        # 💬 결과 표시
        # ===============================
        st.markdown("---")
        st.markdown("### 🧠 AI의 답변")
        st.success(answer)

        st.markdown("### 📚 참고 문서")
        for hit in hits:
            title = hit["_source"]["title"]
            url = hit["_source"]["url"]
            score = hit["_score"]
            st.markdown(f"• **[{title}]({url})** — 점수: `{score:.2f}`")

        st.markdown("---")
        st.caption("⚙️ Powered by OpenAI GPT-4o + Elasticsearch Semantic Search")
