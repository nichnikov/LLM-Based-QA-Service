# tests/test_api.py

from fastapi.testclient import TestClient
from main import app, get_classifier_agent, get_search_agent
from agents.classifying_agent import ClassifierAgent
from agents.search_agent import SearchAgent
from unittest.mock import MagicMock

# --- Моки для агентов ---

# Мок для классификатора
mock_classifier_agent = MagicMock(spec=ClassifierAgent)

# Мок для поискового агента
# Для асинхронных методов нужно использовать AsyncMock или настроить __call__
async def mock_search_agent_call(query, alias):
    if "ошибка" in query:
        return "НЕТ ОТВЕТА"
    return f"Ответ на '{query}' из '{alias}'"

mock_search_agent = MagicMock(spec=SearchAgent)
# Настраиваем асинхронный вызов
mock_search_agent.side_effect = mock_search_agent_call


# --- Функции для переопределения зависимостей ---

def override_get_classifier():
    return mock_classifier_agent

def override_get_searcher():
    return mock_search_agent


# Переопределяем зависимости в приложении FastAPI
app.dependency_overrides[get_classifier_agent] = override_get_classifier
app.dependency_overrides[get_search_agent] = override_get_searcher

# Создаем тестовый клиент
client = TestClient(app)


def test_process_query_greeting():
    """Тестирует ответ на приветствие (категория 1)."""
    # Настраиваем мок, чтобы он вернул "1" (категория "Приветствие")
    mock_classifier_agent.return_value = "1"
    
    response = client.post("/expert_bot/", json={"query": "Добрый день", "alias": "bss.vip"})
    
    assert response.status_code == 200
    assert response.json() == {"answer": "Рады приветствовать вас на нашем сайте", "answer_text": "Рады приветствовать вас на нашем сайте"}

def test_process_query_search_success():
    """Тестирует успешный вызов поискового агента (категория 3)."""
    # Настраиваем мок, чтобы он вернул "3" (категория "Один бухгалтерский вопрос")
    mock_classifier_agent.return_value = "3"
    
    response = client.post("/expert_bot/", json={"query": "вопрос про НДС", "alias": "bss.test"})
    
    assert response.status_code == 200
    assert response.json()["answer"] == "Ответ на 'вопрос про НДС' из 'bss.test'"

def test_process_query_search_fail():
    """Тестирует случай, когда поисковый агент не находит ответ."""
    mock_classifier_agent.return_value = "3" # Все еще бухгалтерский вопрос
    
    response = client.post("/expert_bot/", json={"query": "вопрос, на который будет ошибка", "alias": "bss.test"})
    
    # Ожидаем ошибку 404, как определено в эндпоинте
    assert response.status_code == 404
    assert response.json() == {"detail": "No answer found"}