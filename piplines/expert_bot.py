# piplines/expert_bot.py

import re
import asyncio
import logging
from dataclasses import dataclass
from agents.classifying_agent import ClassifierAgent
from agents.search_agent import SearchAgent

logger = logging.getLogger(__name__)

# Используем dataclass для удобной передачи зависимостей
@dataclass
class BotDependencies:
    classifier_agent: ClassifierAgent
    search_agent: SearchAgent

async def bot_pipeline(query: str, alias: str, deps: BotDependencies) -> str:
    """
    Асинхронный конвейер для обработки запроса и генерации ответа.
    Принимает все зависимости в виде объекта BotDependencies.

    :param query: Вопрос от пользователя.
    :param alias: Идентификатор источника данных.
    :param deps: Объект с зависимостями (агентами).
    :return: Сгенерированный ответ.
    """
    answ_dict = {
        1: "Рады приветствовать вас на нашем сайте", 
        2: "Рады, что смогли вам помочь",
    }

    query_type = deps.classifier_agent(query)
    # Используем безопасное извлечение числа
    query_type_match = re.search(r"\d", query_type)

    if not query_type_match:
        logger.warning(f"Классификатор не смог определить тип запроса: '{query_type}'")
        # По умолчанию считаем, что это вопрос, требующий поиска
        type_num = 3 
    else:
        type_num = int(query_type_match.group(0))

    if type_num in answ_dict:
        return answ_dict[type_num]

    # Если вопрос бухгалтерский или классификатор ошибся
    if type_num in [3, 4]:
        search_result = await deps.search_agent(query, alias)
        return search_result
    
    logger.info(f"Запрос классифицирован как 'Другое' (тип {type_num}). Поиск не будет выполнен.")
    return "Не удалось определить тип вашего запроса. Пожалуйста, переформулируйте его."