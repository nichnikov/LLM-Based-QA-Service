# core/data_types.py

"""Модуль для определения типов данных, используемых в приложении."""
import os
import json
from typing import List
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# ... (классы Settings, Parameters, AgentMemory остаются без изменений) ...

class Settings(BaseSettings):
    openai_api_key: str
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class Parameters(BaseModel):
    retrieval_base_url: str = "http://0.0.0.0:8000"
    retrieval_endpoint: str = "/query/"
    llm_candidates_quantity: int = 15
    ai_model_classifier: str = "openai/gpt-4o-mini"
    ai_model_queries_generate: str = "openai/gpt-4o-mini"
    ai_model_analisys_note: str = "openai/gpt-4o-mini"
    ai_model_voting: str = 'openai/gpt-4o-mini'
    ai_model_answer_generator: str = "openai/gpt-4o-mini"
    ai_temperature: float = 0.0
    ai_max_tokens: int = 3000
    max_texts: int = 30
    app_name: str = "expert_bot"
    project_host: str = "0.0.0.0"
    project_port: int = 8080
    alias_to_site: dict = {
        "bss.vip": "https://vip.1gl.ru", 
        "bss": "https://1gl.ru",
        "uss": "https://1jur.ru"
    }
    memory_path: str = os.path.join("data", "memory")

class AgentMemory(BaseModel):
    query: str = ""
    alias: str = "bss.vip"
    fail_answer: str = "НЕТ ОТВЕТА"
    searching_candidates: list[dict] = Field(default_factory=list)
    temp_queries: list[str] = Field(default_factory=list)
    analysis_note: str = ""
    voting: str = ""
    answer: str = ""
    count: int = 1
    best_fragments: str = ""


class PromtsChain(BaseModel):
    """
    Коллекция всех шаблонов промптов.
    Промпты загружаются из внешнего JSON-файла, что позволяет
    изменять их без модификации исходного кода.
    """
    query_generation: str
    validation_plan: str
    validation_choice: str
    validation_voting: str
    answer_generation: str
    classication: str
    answer_generation_with_votin: str

    @classmethod
    def from_file(cls, file_path: str | Path):
        """
        Фабричный метод для создания экземпляра класса путем загрузки данных из JSON-файла.

        :param file_path: Путь к JSON-файлу с промптами.
        :return: Экземпляр класса PromtsChain.
        :raises FileNotFoundError: Если файл не найден.
        :raises KeyError: Если в JSON отсутствуют необходимые ключи.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Файл с промптами не найден по пути: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Pydantic автоматически проверит, что все поля класса присутствуют в JSON
        return cls.model_validate(data)

class QueryRequest(BaseModel):
    query: str
    alias: str

class AnswerResponse(BaseModel):
    answer: str
    answer_text: str