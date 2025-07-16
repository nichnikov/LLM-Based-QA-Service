import pytest
from core.data_types import Settings, Parameters, AgentMemory, PromtsChain, QueryRequest, AnswerResponse

def test_settings_creation(mocker):
    """
    Тестирует создание объекта Settings и загрузку переменных из .env.
    """
    # Мокаем переменные окружения, чтобы не зависеть от реального .env файла
    mocker.patch.dict('os.environ', {
        'ES_HOSTS': 'testhost',
        'ES_LOGIN': 'testlogin',
        'ES_PASSWORD': 'testpassword',
        'OPENAI_API_KEY': 'testkey'
    })
    settings = Settings()
    assert settings.openai_api_key == 'testkey'
    assert settings.es_hosts == 'testhost'

def test_parameters_instantiation():
    """Проверяет, что объект Parameters создается без ошибок."""
    try:
        Parameters()
    except Exception as e:
        pytest.fail(f"Ошибка при создании объекта Parameters: {e}")

def test_agent_memory_instantiation():
    """Проверяет, что объект AgentMemory создается без ошибок."""
    try:
        AgentMemory()
    except Exception as e:
        pytest.fail(f"Ошибка при создании объекта AgentMemory: {e}")

def test_promts_chain_instantiation():
    """Проверяет, что объект PromtsChain создается без ошибок и содержит промпты."""
    prompts = PromtsChain()
    assert "Ты опытный бухгалтер" in prompts.query_generation

def test_request_response_models():
    """Проверяет создание моделей запроса и ответа."""
    query = QueryRequest(query="test?", alias="test_alias")
    assert query.query == "test?"
    
    answer = AnswerResponse(answer="Ответ", answer_text="Текст ответа")
    assert answer.answer == "Ответ"