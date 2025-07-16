import pytest
from agents.classifying_agent import ClassifierAgent
from core.data_types import PromtsChain, Parameters, AgentMemory
from agents.ai_base import LLMGenerator
from unittest.mock import MagicMock

def test_classifier_agent_action(
    mock_ai_client: MagicMock, 
    prompts: PromtsChain, 
    parameters: Parameters
):
    """
    Тестирует основную логику классифицирующего агента.
    """
    # 1. Настройка (Arrange)
    # Задаем, что должен вернуть наш мок-клиент при вызове
    expected_classification = "3. Один бухгалтерский или юридический вопрос"
    mock_ai_client.return_value = expected_classification
    
    # Создаем экземпляр агента с мок-зависимостями
    agent = ClassifierAgent(prompts, parameters, AgentMemory(), mock_ai_client)
    query = "Добрый день! У работницы предприятия двое детей..."

    # 2. Действие (Act)
    result = agent.action_pipeline(query)

    # 3. Проверка (Assert)
    # Проверяем, что результат соответствует ожиданиям
    assert result == expected_classification

    # Проверяем, что наш мок-клиент был вызван один раз
    mock_ai_client.assert_called_once()
    
    # Проверяем, что клиент был вызван с правильными аргументами
    call_args, call_kwargs = mock_ai_client.call_args
    assert query in call_args[0] # Проверяем, что запрос пользователя есть в промпте
    assert call_kwargs['model'] == parameters.ai_model_classifier
    assert call_kwargs['temperature'] == 0.5