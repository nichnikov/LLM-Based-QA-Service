# agents/search_agent.py

import asyncio
import re
from typing import List

from agents.base_agent import BaseAgent
from agents.ai_base import LLMGenerator
from services.retriever import AsyncPostRequest
from core.data_types import PromtsChain, Parameters, AgentMemory
from agents.search_agent_units import AnalysisUnit, VotingUnit, AnswerGenerator, MemoryManager


class SearchAgent(BaseAgent):
    """
    Агент-оркестратор. Координирует процесс поиска, анализа и генерации ответа.
    Делегирует конкретные задачи специализированным классам (юнитам).
    """
    def __init__(self,
                 prompts: PromtsChain,
                 parameters: Parameters,
                 memory: AgentMemory,
                 ai_client: LLMGenerator,
                 retriever: AsyncPostRequest,
                 analysis_unit: AnalysisUnit,
                 voting_unit: VotingUnit,
                 answer_generator: AnswerGenerator,
                 memory_manager: MemoryManager,
                 voting_unit_is: bool = False,
                 queries_generate: bool = False):
        super().__init__(prompts, parameters, memory, ai_client)
        self.retriever = retriever
        self.analysis_unit = analysis_unit
        self.voting_unit = voting_unit
        self.answer_generator = answer_generator
        self.memory_manager = memory_manager
        self.voting_unit_is = voting_unit_is
        self.queries_generate = queries_generate

    def _clear_memory(self):
        """Очищает память агента для нового цикла обработки."""
        self.memory = AgentMemory() # Создаем новый чистый экземпляр

    async def _generate_and_search_queries(self, initial_query: str) -> List[dict]:
        """
        Генерирует дополнительные поисковые запросы (если включено) и выполняет поиск.
        """
        search_tasks = []
        if self.queries_generate:
            prompt_query = self.prompts.query_generation.format(initial_query)
            generated_queries_text = self.ai_client(
                prompt_query,
                model=self.parameters.ai_model_queries_generate,
                temperature=1.0,
                max_tokens=3000
            )
            queries = [initial_query] + generated_queries_text.split("\n")
        else:
            queries = [initial_query]

        # Запускаем поиск для каждого запроса асинхронно
        for q in queries:
            clean_query = re.sub(r"Вопрос\d+:", "", q).strip()
            if clean_query:
                self.memory.temp_queries.append(clean_query)
                task = self.retriever(
                    query=clean_query,
                    alias=self.memory.alias,
                    endpoint=self.parameters.retrieval_endpoint,
                    headers={"Authorization": "Bearer token123"},
                    timeout=15
                )
                search_tasks.append(task)
        
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Собираем всех кандидатов
        for res in results:
            if isinstance(res, dict) and "ranking_dicts" in res:
                self.memory.searching_candidates.extend(res["ranking_dicts"])

    async def action_pipeline(self, query: str, alias: str = "bss.vip") -> str:
        """
        Основной конвейер, координирующий работу агента.
        1. Очищает память.
        2. Ищет кандидатов.
        3. Создает аналитическую записку.
        4. Проводит голосование (если включено).
        5. Генерирует ответ.
        6. Сохраняет результаты.
        """
        self._clear_memory()
        self.memory.query = query
        self.memory.alias = alias
        
        await self._generate_and_search_queries(query)

        if not self.memory.searching_candidates:
            return self.memory.fail_answer

        # Шаг 1: Анализ
        analysis_note, best_fragments = self.analysis_unit.generate(query, self.memory.searching_candidates)
        self.memory.analysis_note = analysis_note
        self.memory.best_fragments = best_fragments

        # Шаг 2: Голосование
        answer_is_relevant = True
        if self.voting_unit_is:
            answer_is_relevant = self.voting_unit.vote(query, analysis_note, best_fragments)

        # Шаг 3: Генерация ответа
        if answer_is_relevant:
            answer = self.answer_generator.generate(query, analysis_note, best_fragments, self.voting_unit_is)
        else:
            answer = self.memory.fail_answer
            
        self.memory.answer = answer
        
        # Шаг 4: Сохранение
        self.memory_manager.save(self.memory.model_dump(), model_answer_generator=self.parameters.ai_model_answer_generator)
        
        return answer