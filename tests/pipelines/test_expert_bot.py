import pytest
from unittest.mock import MagicMock, AsyncMock
from piplines.expert_bot import bot_pipeline, BotDependencies
from agents.classifying_agent import ClassifierAgent
from agents.search_agent import SearchAgent

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_bot_dependencies() -> BotDependencies:
    """Фикстура для создания мок-зависимостей для конвейера."""
    # Создаем мок для ClassifierAgent
    mock_classifier = MagicMock(spec=ClassifierAgent)
    
    # Создаем мок для SearchAgent с асинхронным __call__
    mock_searcher = AsyncMock(spec=SearchAgent)
    
    return BotDependencies(
        classifier_agent=mock_classifier,
        search_agent=mock_searcher
    )

async def test_bot_pipeline_greeting(mock_bot_dependencies: BotDependencies):
    """Тест: конвейер должен вернуть приветствие, если классификатор определил тип 1."""
    # Настройка
    mock_bot_dependencies.classifier_agent.return_value = "1. Приветствие"
    
    # Действие
    result = await bot_pipeline("Привет", "test.alias", mock_bot_dependencies)
    
    # Проверка
    assert result == "Рады приветствовать вас на нашем сайте"
    mock_bot_dependencies.classifier_agent.assert_called_once_with("Привет")
    mock_bot_dependencies.search_agent.assert_not_called() # Убеждаемся, что поисковик не вызывался

async def test_bot_pipeline_search(mock_bot_dependencies: BotDependencies):
    """Тест: конвейер должен вызвать поисковик, если классификатор определил тип 3."""
    # Настройка
    mock_bot_dependencies.classifier_agent.return_value = "3. Один бухгалтерский вопрос"
    mock_bot_dependencies.search_agent.return_value = "Ответ про НДС"
    
    # Действие
    result = await bot_pipeline("Вопрос про НДС?", "test.alias", mock_bot_dependencies)

    # Проверка
    assert result == "Ответ про НДС"
    mock_bot_dependencies.classifier_agent.assert_called_once_with("Вопрос про НДС?")
    mock_bot_dependencies.search_agent.assert_awaited_once_with("Вопрос про НДС?", "test.alias")

async def test_bot_pipeline_other_category(mock_bot_dependencies: BotDependencies):
    """Тест: конвейер обрабатывает категорию 'Другое'."""
    # Настройка
    mock_bot_dependencies.classifier_agent.return_value = "5. Другое"

    # Действие
    result = await bot_pipeline("Сколько будет 2+2?", "test.alias", mock_bot_dependencies)

    # Проверка
    assert result == "Не удалось определить тип вашего запроса. Пожалуйста, переформулируйте его."