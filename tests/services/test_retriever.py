# tests/services/test_retriever.py

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from services.retriever import AsyncPostRequest

# Помечаем все тесты в этом модуле как асинхронные
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_aiohttp_session(mocker):
    """
    Фикстура для мока aiohttp.ClientSession.
    Позволяет нам контролировать ответы от симулированного сервера.
    """
    mock_session = MagicMock()
    # Мокаем асинхронный контекстный менеджер
    mock_session.post.return_value.__aenter__.return_value = AsyncMock()
    
    # Патчим ClientSession в модуле, где он используется
    mocker.patch('aiohttp.ClientSession', return_value=mock_session)
    
    return mock_session

async def test_retriever_success(mock_aiohttp_session):
    """
    Тестирует успешный сценарий работы ретривера.
    """
    # Настраиваем мок-ответ
    mock_response = mock_aiohttp_session.post.return_value.__aenter__.return_value
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"ranking_dicts": [{"text": "some data"}]})

    retriever = AsyncPostRequest("http://fake-url.com")
    response = await retriever(query="test", alias="bss.vip", endpoint="/query/")

    assert response == {"ranking_dicts": [{"text": "some data"}]}
    # Проверяем, что POST-запрос был вызван с правильными параметрами
    mock_aiohttp_session.post.assert_called_once_with(
        "http://fake-url.com/query/",
        json={"query": "test", "alias": "bss.vip"},
        headers=None,
        timeout=AsyncMock() # aiohttp.ClientTimeout является объектом, поэтому мокаем
    )

async def test_retriever_404_error(mock_aiohttp_session):
    """
    Тестирует сценарий, когда сервер возвращает ошибку 404.
    """
    mock_response = mock_aiohttp_session.post.return_value.__aenter__.return_value
    mock_response.status = 404
    mock_response.json = AsyncMock(return_value={"detail": "Not Found"})

    retriever = AsyncPostRequest("http://fake-url.com")
    
    with pytest.raises(ValueError, match="Endpoint not found"):
        await retriever(query="test", alias="bss.vip", endpoint="/query/")