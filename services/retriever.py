# services/retriever.py

import aiohttp
import asyncio
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsyncPostRequest:
    """
    Класс для выполнения асинхронных POST-запросов к сервису поиска (ретриверу).
    Использует aiohttp для эффективной работы в асинхронной среде FastAPI.
    """
    def __init__(self, base_url: str = ""):
        """
        :param base_url: Базовый URL для всех запросов.
        """
        self.base_url = base_url.rstrip('/') if base_url else ""
        
    async def post(
        self,
        endpoint: str,
        query: str,
        alias: str,
        additional_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Выполняет асинхронный POST-запрос.

        :param endpoint: Конечная точка API.
        :param query: Поисковый запрос.
        :param alias: Идентификатор источника.
        :param headers: Заголовки запроса.
        :param timeout: Таймаут ожидания ответа.
        :return: Ответ сервера в виде словаря.
        :raises ValueError: Если сервер вернул ошибку клиента (например, 404).
        :raises ConnectionError: В случае сетевых проблем.
        """
        url = f"{self.base_url}{endpoint}"
        request_body = {"query": query, "alias": alias}
        if additional_data:
            request_body.update(additional_data)
        
        try:
            logger.info(f"Отправка POST-запроса на {url} с данными: {request_body}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=request_body,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    
                    response_data = await response.json()
                    
                    if response.status >= 400:
                        error_msg = f"Ошибка сервера: HTTP {response.status}\nОтвет: {response_data}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    
                    logger.info(f"Успешный ответ от {url}")
                    return response_data
                    
        except aiohttp.ClientError as e:
            error_msg = f"Сетевая ошибка: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        except Exception as e:
            error_msg = f"Неожиданная ошибка: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    async def __call__(self, **kwargs) -> Dict[str, Any]:
        """
        Магический метод, позволяющий вызывать экземпляр класса как функцию.
        Является оберткой над методом post для удобства.
        """
        return await self.post(**kwargs)