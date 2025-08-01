# agents/search_agent_units.py

import os
import re
import uuid
import json
import logging
import datetime
from typing import List, Dict, Any

from agents.ai_base import LLMGenerator
from core.data_types import PromtsChain, AgentMemory, Parameters

# ... (Классы AnalysisUnit, VotingUnit, AnswerGenerator остаются без изменений) ...
class AnalysisUnit:
    """
    Отвечает за создание аналитической записки на основе найденных фрагментов.
    """
    def __init__(self, ai_client: LLMGenerator, prompts: PromtsChain, parameters: Parameters):
        self.ai_client = ai_client
        self.prompts = prompts
        self.parameters = parameters

    def _prepare_fragments_string(self, searching_candidates: List[Dict[str, Any]]) -> str:
        """
        Преобразует список кандидатов в строку для промпта.
        Сортирует фрагменты по релевантности и обрезает до максимального количества.
        """
        text_candidates = []
        fragments_tuples = []
         
        for d in searching_candidates:
            fragments_tuples.extend([
                (f"Заголовок текста: {d.get('title', '')} ссылка на текст: {d.get('link', '')} Фрагмент: {tpl[0]}", tpl[1]) 
                for tpl in d.get("best_fragments_scores", [])
            ])
        
        # Сортировка всех фрагментов из всех документов по их оценке
        sorted_fragments = sorted(fragments_tuples, key=lambda x: x[1], reverse=True)
        
        # Выбор лучших фрагментов до заданного лимита
        for tpl in sorted_fragments[:self.parameters.max_texts]:
            text_candidates.append(tpl[0])

        return "\n\n".join(text_candidates)

    def generate(self, query: str, searching_candidates: List[Dict[str, Any]]) -> (str, str):
        """
        Генерирует аналитическую записку.

        :param query: Запрос пользователя.
        :param searching_candidates: Список найденных документов-кандидатов.
        :return: Кортеж (текст аналитической записки, строка с лучшими фрагментами).
        """
        best_fragments_str = self._prepare_fragments_string(searching_candidates)
        
        prompt_plan = self.prompts.validation_plan.format(query, best_fragments_str)
        
        analysis_note = self.ai_client(
            prompt_plan,
            model=self.parameters.ai_model_analisys_note, 
            temperature=0.1, 
            max_tokens=5000
        )
        return analysis_note, best_fragments_str


class VotingUnit:
    """
    Отвечает за проведение "голосования" для оценки релевантности ответа.
    """
    def __init__(self, ai_client: LLMGenerator, prompts: PromtsChain, parameters: Parameters):
        self.ai_client = ai_client
        self.prompts = prompts
        self.parameters = parameters

    def vote(self, query: str, analysis_note: str, best_fragments: str) -> bool:
        """
        Проводит голосование экспертов.

        :return: True, если ответ релевантен, иначе False.
        """
        prompt_voting = self.prompts.validation_voting.format(query, analysis_note, best_fragments)
        voting_result_text = self.ai_client(
            prompt_voting,
            model=self.parameters.ai_model_voting,
            temperature=0.2, 
            max_tokens=1000
        )
        
        # Простая логика извлечения результата из текста
        # REGEX ищет фразу "общее мнение: есть ответ" без учета регистра
        voting = re.search(r"общее\s+мнение:\s+есть\s+ответ", voting_result_text, re.IGNORECASE)
        
        return bool(voting)


class AnswerGenerator:
    """
    Отвечает за генерацию итогового ответа пользователю.
    """
    def __init__(self, ai_client: LLMGenerator, prompts: PromtsChain, parameters: Parameters):
        self.ai_client = ai_client
        self.prompts = prompts
        self.parameters = parameters

    def generate(self, query: str, analysis_note: str, best_fragments: str, voting_enabled: bool) -> str:
        """
        Генерирует финальный ответ.

        :param voting_enabled: Флаг, указывающий, используется ли отдельный узел голосования.
        """
        if voting_enabled:
            # Если голосование было, используем промпт, который сразу генерирует ответ
            prompt_template = self.prompts.answer_generation
        else:
            # Если голосования не было, промпт сам должен проверить наличие ответа
            prompt_template = self.prompts.answer_generation_with_votin

        prompt_answer = prompt_template.format(query, analysis_note, best_fragments)
        
        answer = self.ai_client(
            prompt_answer,
            model=self.parameters.ai_model_answer_generator,
            temperature=0.1,
            max_tokens=5000
        )
        return answer


class MemoryManager:
    """
    Управляет сохранением памяти агента в файл.
    Для каждого вызова метода save() генерируется уникальное имя файла.
    """
    def __init__(self, parameters: Parameters):
        """
        Инициализирует менеджер памяти.

        :param parameters: Параметры приложения, содержащие путь для сохранения.
        """
        self.memory_path = parameters.memory_path
        # Убеждаемся, что директория для сохранения существует
        if not os.path.exists(self.memory_path):
            os.makedirs(self.memory_path)

    def _sanitize_filename(self, text: str, max_length: int = 50) -> str:
        """
        Очищает текст, чтобы его можно было безопасно использовать в имени файла.

        :param text: Входной текст (например, запрос пользователя).
        :param max_length: Максимальная длина очищенного текста.
        :return: Очищенная строка.
        """
        # Удаляем недопустимые символы
        text = re.sub(r'[\\/*?:"<>|]', "", text)
        # Заменяем пробелы на подчеркивания
        text = text.replace(" ", "_")
        # Ограничиваем длину
        return text[:max_length]

    def save(self, memory_data: Dict[str, Any], **kwargs):
        """
        Сохраняет содержимое памяти в уникальный JSON-файл.

        Имя файла генерируется на основе временной метки,
        запроса пользователя и уникального идентификатора (UUID)
        для предотвращения коллизий.

        :param memory_data: Словарь с данными из AgentMemory.
        :param kwargs: Дополнительные данные для сохранения.
        """
        # Объединяем основные данные с дополнительными
        memory_data.update(kwargs)
        
        # --- Генерация уникального имени файла ---
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        query_part = self._sanitize_filename(memory_data.get("query", "no_query"))
        unique_id = uuid.uuid4().hex[:8]  # Короткий UUID для уникальности
        
        filename = f"{timestamp}_{unique_id}.json"
        
        json_path = os.path.join(self.memory_path, filename)
        
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=4, default=str)
        except Exception as e:
            logging.error(f"Не удалось сохранить файл памяти {json_path}: {e}")