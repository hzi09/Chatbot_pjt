import pytest
from unittest.mock import patch, MagicMock
from backend.config import (
    get_openai_client,
    get_openai_key,
    QUESTION_PROMPT,
    EVALUATION_PROMPT,
    PINECONE_CONFIG,
    DB_CONFIG,
    vectorstore,
    retriever
)

class TestConfig:
    @pytest.fixture
    def mock_secrets(self):
        """Streamlit secrets 모의 객체 설정"""
        with patch('streamlit.secrets') as mock:
            mock.__getitem__.return_value = {"OPENAI_API_KEY": "test_key"}
            yield mock

    def test_get_openai_client(self, mock_secrets):
        """OpenAI 클라이언트 생성 테스트"""
        client = get_openai_client()
        assert client is not None
        assert client.model_name == "gpt-4o-mini"
        assert client.temperature == 0.9
        assert client.max_tokens == 1500

    def test_get_openai_key(self, mock_secrets):
        """OpenAI API 키 가져오기 테스트"""
        api_key = get_openai_key()
        assert api_key == "test_key"

    def test_question_prompt_template(self):
        """면접 질문 생성 프롬프트 템플릿 테스트"""
        context = "파이썬 리스트와 튜플의 차이점"
        result = QUESTION_PROMPT.format(context=context)
        assert "파이썬 면접 질문을 하나만 생성해 주세요" in result
        assert context in result

    def test_evaluation_prompt_template(self):
        """면접 평가 프롬프트 템플릿 테스트"""
        question = "파이썬의 GIL이란 무엇인가요?"
        answer = "GIL은 Global Interpreter Lock의 약자입니다."
        context = "파이썬의 GIL에 대한 설명"
        
        result = EVALUATION_PROMPT.format(
            question=question,
            answer=answer,
            context=context
        )
        assert question in result
        assert answer in result
        assert context in result
        assert "파이썬 면접관 챗봇" in result

    def test_pinecone_config(self):
        """Pinecone 설정 테스트"""
        assert "api_key" in PINECONE_CONFIG
        assert "environment" in PINECONE_CONFIG
        assert "index_name" in PINECONE_CONFIG

    def test_db_config(self):
        """데이터베이스 설정 테스트"""
        assert "host" in DB_CONFIG
        assert "database" in DB_CONFIG
        assert "user" in DB_CONFIG
        assert "password" in DB_CONFIG
        assert "port" in DB_CONFIG

    def test_vectorstore(self):
        """벡터 스토어 설정 테스트"""
        assert vectorstore is not None
        assert retriever is not None
        assert retriever.search_type == "mmr"
        assert retriever.search_kwargs["k"] == 5
        assert retriever.search_kwargs["fetch_k"] == 20
        assert retriever.search_kwargs["lambda_mult"] == 0.7 