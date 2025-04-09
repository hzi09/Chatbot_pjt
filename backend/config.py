import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
# from pinecone import Pinecone, ServerlessSpec
import pinecone
from langchain_pinecone import PineconeVectorStore

# .env 파일 로드
load_dotenv()

# 데이터베이스 설정
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", st.secrets.get('postgres', {}).get('POSTGRES_HOST')),
    "port": os.getenv("POSTGRES_PORT", st.secrets.get('postgres', {}).get('POSTGRES_PORT')),
    "database": os.getenv("POSTGRES_DB", st.secrets.get('postgres', {}).get('POSTGRES_DB')),
    "user": os.getenv("POSTGRES_USER", st.secrets.get('postgres', {}).get('POSTGRES_USER')),
    "password": os.getenv("POSTGRES_PASSWORD", st.secrets.get('postgres', {}).get('POSTGRES_PASSWORD')),
    "sslmode": os.getenv("SSL_MODE", st.secrets.get('postgres', {}).get('SSL_MODE'))
}

# OpenAI 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", st.secrets.get('openai', {}).get('OPENAI_API_KEY'))

# Pinecone 설정
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", st.secrets.get('pinecone', {}).get('PINECONE_API_KEY'))
PINECONE_ENV = os.getenv("PINECONE_ENV", st.secrets.get('pinecone', {}).get('PINECONE_ENV'))
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", st.secrets.get('pinecone', {}).get('PINECONE_INDEX_NAME'))

# RAG 설정
QUESTION_PROMPT = """
다음 컨텍스트를 기반으로 면접 질문을 생성해주세요:
{context}

생성된 질문:
"""

EVALUATION_PROMPT = """
다음 질문과 답변을 평가해주세요:
질문: {question}
답변: {answer}

평가 기준:
1. 정확성: 답변이 정확한 정보를 포함하고 있는가?
2. 완성도: 답변이 충분히 상세하고 완성도가 높은가?
3. 명확성: 답변이 명확하고 이해하기 쉬운가?

평가 결과:
"""

# RAG 검색기 설정
retriever = None  # 실제 구현에서 설정

# openai 기본 모델 설정
DEFAULT_MODEL = "gpt-4o-mini"

# OpenAI API 클라이언트 설정
def get_openai_client():
    return ChatOpenAI(model= DEFAULT_MODEL, temperature=0.9, api_key=OPENAI_API_KEY,max_completion_tokens=1500)

def get_openai_key():
    return OPENAI_API_KEY

# 면접 질문 생성 프롬프트
QUESTION_PROMPT = PromptTemplate(
    template="""주어진 문서를 기반으로 파이썬 면접 질문을 하나만 생성해 주세요. 
    문서 내용: {context}
    면접 질문:""",
    input_variables=["context"]
)

# 면접 챗봇 평가 프롬프트
EVALUATION_PROMPT = PromptTemplate(
    template="""
    너는 파이썬 면접관 챗봇이야. 
    지원자가 답변을 입력하면 아래의 문서를 참조해서 평가 및 모범답안을 제시해줘
    
    참고 문서:  
    {context}
    
    질문: {question}
    답변: {answer}
    평가:
    """,
    input_variables=["question", "answer", "context"]
)

# RAG 설정
VECTOR_STORE_PATH = "my_vector_store"

# Embedding 설정
embeddings = OpenAIEmbeddings(api_key=get_openai_key())

PINECONE_CONFIG = {
    "api_key": PINECONE_API_KEY,
    "environment": PINECONE_ENV,
    "index_name": PINECONE_INDEX_NAME
}

pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)

# index 객체 생성
if PINECONE_CONFIG["index_name"] not in pc.list_indexes().names():
    raise ValueError(f"Pinecone 인덱스 '{PINECONE_CONFIG['index_name']}'가 존재하지 않습니다. 먼저 생성해 주세요.")

index = pc.Index(PINECONE_CONFIG["index_name"])

# Vector Store 생성 (LangChain용)
vectorstore = PineconeVectorStore(index, embeddings,namespace="example-namespace")
print(type(vectorstore))  # <class 'langchain_pinecone.vectorstores.Pinecone'>

# retriever로 변환
retriever = vectorstore.as_retriever(search_type = "mmr",search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.7})

QUERY="파이썬 면접 질문 하나 생성해"

# 챗봇 UI 아바타
BOT_AVATAR = 'https://github.com/user-attachments/assets/caedea67-2ccf-459d-b5d8-7a6ffcd8fc24'
USER_AVATAR = 'https://github.com/user-attachments/assets/f77abd1d-5c80-49c2-8225-13e136a6446b'

# # RAG 설정
# VECTOR_STORE_PATH = "my_vector_store"

# # Embedding 설정
# embeddings = OpenAIEmbeddings()
# vector_store = Chroma(persist_directory=VECTOR_STORE_PATH, embedding_function=embeddings)
# retriever = vector_store.as_retriever()


