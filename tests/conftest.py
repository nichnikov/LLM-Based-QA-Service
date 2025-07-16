import pytest
from unittest.mock import MagicMock
from agents.ai_base import LLMGenerator
from core.data_types import PromtsChain, Parameters, Settings

@pytest.fixture
def mock_ai_client() -> MagicMock:
    """
    Фикстура, которая создает мок (заглушку) для LLMGenerator.
    Это позволяет тестировать логику агентов, не делая реальных вызовов к API.
    """
    return MagicMock(spec=LLMGenerator)

@pytest.fixture
def prompts() -> PromtsChain:
    """Фикстура, предоставляющая экземпляр с промптами."""
    return PromtsChain()

@pytest.fixture
def parameters() -> Parameters:
    """Фикстура, предоставляющая экземпляр с параметрами приложения."""
    return Parameters()

@pytest.fixture
def settings() -> Settings:
    """Фикстура, предоставляющая экземпляр с настройками (ключами и т.д.)."""
    # Для тестов мы можем передать фиктивные значения
    return Settings(
        es_hosts="localhost",
        es_login="test",
        es_password="test",
        openai_api_key="fake_api_key"
    )