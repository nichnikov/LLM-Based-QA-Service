# agents/ai_base.py

from abc import ABC, abstractmethod
import logging
from openai import OpenAI, APIError  # Более конкретный импорт ошибки

logger = logging.getLogger(__name__)

class LLMClient(ABC):
    """
    Абстрактный базовый класс для клиентов, взаимодействующих с API языковых моделей.
    """

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Генерирует ответ от LLM на основе предоставленного промпта.

        :param prompt: Строка запроса для модели.
        :param kwargs: Дополнительные параметры для запроса (model, temperature и т.д.).
        :return: Ответ модели в виде строки.
        """
        pass

    def __call__(self, prompt: str, **kwargs) -> str:
        """
        Позволяет использовать объект класса как функцию для генерации текста.

        :param prompt: Строка запроса для модели.
        :param kwargs: Дополнительные параметры для клиента AI.
        :return: Ответ модели в виде строки.
        """
        return self.generate(prompt, **kwargs)


class LLMGenerator(LLMClient):
    """
    Реализация клиента для работы с OpenAI-совместимым API.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.vsegpt.ru:7090/v1"):
        """
        Инициализирует клиент.

        :param api_key: API ключ для доступа к сервису.
        :param base_url: Базовый URL API.
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Отправляет запрос к API и возвращает сгенерированный текст.

        :param prompt: Строка запроса для модели.
        :param kwargs: Дополнительные параметры для запроса (model, temperature, max_tokens и т.д.).
        :return: Ответ модели в виде строки.
        :raises RuntimeError: В случае ошибки API.
        """
        messages = [{"role": "user", "content": prompt}]
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except APIError as e:
            logger.error(f"Ошибка API при обращении к LLM: {e}")
            raise RuntimeError(f"OpenAI API error: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при работе с LLM: {e}")
            raise RuntimeError(f"Unexpected error in LLM generation: {e}")