# tests/agents/test_search_agent_units.py

import pytest
from unittest.mock import MagicMock

from agents.ai_base import LLMGenerator
from agents.search_agent_units import AnalysisUnit, VotingUnit, AnswerGenerator
from core.data_types import PromtsChain, Parameters

@pytest.fixture
def mock_ai_client():
    """Фикстура для мока LLM-клиента."""
    return MagicMock(spec=LLMGenerator)

@pytest.fixture
def prompts():
    """Фикстура с промптами."""
    return PromtsChain()

@pytest.fixture
def parameters():
    """Фикстура с параметрами."""
    return Parameters()

def test_analysis_unit(mock_ai_client, prompts, parameters):
    """Тестирует юнит для создания аналитической записки."""
    # Настройка
    mock_ai_client.return_value = "Сгенерированная аналитическая записка"
    analysis_unit = AnalysisUnit(mock_ai_client, prompts, parameters)
    
    query = "Какой-то вопрос?"
    candidates = [
        {"title": "Doc 1", "link": "http://1", "best_fragments_scores": [("fragment 1", 0.9)]},
        {"title": "Doc 2", "link": "http://2", "best_fragments_scores": [("fragment 2", 0.8)]}
    ]

    # Действие
    note, fragments_str = analysis_unit.generate(query, candidates)

    # Проверка
    assert note == "Сгенерированная аналитическая записка"
    assert "Заголовок текста: Doc 1" in fragments_str
    assert "Фрагмент: fragment 1" in fragments_str
    mock_ai_client.assert_called_once() # Проверяем, что LLM была вызвана

def test_voting_unit_success(mock_ai_client, prompts, parameters):
    """Тестирует успешный исход голосования."""
    mock_ai_client.return_value = "ОБЩЕЕ МНЕНИЕ: ЕСТЬ ОТВЕТ"
    voting_unit = VotingUnit(mock_ai_client, prompts, parameters)

    result = voting_unit.vote("query", "note", "fragments")
    
    assert result is True

def test_voting_unit_failure(mock_ai_client, prompts, parameters):
    """Тестирует неуспешный исход голосования."""
    mock_ai_client.return_value = "ОБЩЕЕ МНЕНИЕ: НЕТ ОТВЕТА"
    voting_unit = VotingUnit(mock_ai_client, prompts, parameters)

    result = voting_unit.vote("query", "note", "fragments")

    assert result is False

def test_answer_generator(mock_ai_client, prompts, parameters):
    """Тестирует генератор ответов."""
    mock_ai_client.return_value = "Финальный ответ"
    answer_generator = AnswerGenerator(mock_ai_client, prompts, parameters)

    # Сценарий с включенным голосованием
    answer_with_voting = answer_generator.generate("q", "n", "f", voting_enabled=True)
    assert answer_with_voting == "Финальный ответ"
    # Проверяем, что использовался правильный промпт
    call_args, _ = mock_ai_client.call_args
    assert "Аналитическая записка:" in call_args[0]
    
    # Сценарий с выключенным голосованием
    answer_without_voting = answer_generator.generate("q", "n", "f", voting_enabled=False)
    assert answer_without_voting == "Финальный ответ"
    call_args, _ = mock_ai_client.call_args
    assert 'Если из полученной "Аналитической записки" и "Текстов материалов" нельзя ответить' in call_args[0]