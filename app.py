import os
import pandas as pd
import streamlit as st
from openai import OpenAI
from elasticsearch import Elasticsearch

client = OpenAI(api_key=st.secrets["api_key"])

# https://www.elastic.co/search-labs/tutorials/install-elasticsearch/elastic-cloud#finding-your-cloud-id
ELASTIC_CLOUD_ID = st.secrets["elastic_cloud_key"]

# https://www.elastic.co/search-labs/tutorials/install-elasticsearch/elastic-cloud#creating-an-api-key
ELASTIC_API_KEY = st.secrets["elastic_api_key"]

es = Elasticsearch(
  cloud_id = ELASTIC_CLOUD_ID,
  api_key=ELASTIC_API_KEY
)

# Test connection to Elasticsearch
print(es.info())


st.subheader("영문 위키피디아 이용한")
st.title("한글로 답변하는 AI")
st.subheader("부제 : Semantic search and Retrieval augmented generation using Elasticsearch and OpenAI")

st.caption('''
영문 Wiki에서 답변 가능한 질문에 대해서 답변을 잘합니다. 졸은 질문 예 : 
- 대서양은 몇 번째로 큰 바다인가?
- 대한민국의 수도는?
- 이순신의 출생년도는?
- 도요타에서 가장 많이 팔리는 차는?

데이터 출처
- https://cdn.openai.com/API/examples/data/vector_database_wikipedia_articles_embedded.zip
- 데이터 설명 : https://weaviate.io/developers/weaviate/tutorials/wikipedia
- 데이터 건수 : 25,000건 (데이터의 양을 늘리면, 다양한 질문에 대한 답변 가능)

''')

with st.form("form"):
    question = st.text_input("Prompt")
    submit = st.form_submit_button("Submit")

if submit and question:
  with st.spinner("Waiting for Kevin AI..."):
      print("질문 : " + question)
      question = question.replace("\n", " ")
    
      question = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
              {
