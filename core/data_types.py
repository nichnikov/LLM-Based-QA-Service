# core/data_types.py

"""Модуль для определения типов данных, используемых в приложении."""
import os
from typing import List
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Настройки приложения, которые загружаются из переменных окружения.
    Использует pydantic-settings для автоматической загрузки из .env файла.
    """
    es_hosts: str
    es_login: str 
    es_password: str
    openai_api_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class Parameters(BaseModel):
    """
    Параметры и константы, используемые в приложении.
    Эти значения жестко заданы в коде и не меняются через переменные окружения.
    """
    retrieval_base_url: str = "http://0.0.0.0:8000"
    retrieval_endpoint: str = "/query/"
    llm_candidates_quantity: int = 15
    es_mod_id_name: str = "mod_id"
    es_doc_id_name: str = "doc_id"
    ai_model_classifier: str = "openai/gpt-4o-mini"
    ai_model_queries_generate: str = "openai/gpt-4o-mini"
    ai_model_analisys_note: str = "openai/gpt-4o-mini"
    ai_model_voting: str = 'openai/gpt-4o-mini'
    ai_model_answer_generator: str = "qwen/qwen3-235b"
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
    """
    Структура данных для хранения состояния (памяти) поискового агента в рамках одного запроса.
    """
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
    Коллекция всех шаблонов промптов, используемых в приложении.
    """
    query_generation: str = """Ты опытный бухгалтер... (и так далее)"""
    validation_plan: str = """Ты опытный бухгалтер... (и так далее)"""
    validation_choice: str = """Тебе передали подборку текстов... (и так далее)"""
    validation_voting: str = """Собрали 3х независимых экспертов... (и так далее)"""
    answer_generation: str = """Ты Опытный бухгалтер... (и так далее)"""
    classication: str = """Классицифируй входящее сообщение: {}\n(никаких слов, кроме списка)\n1. Приветствие\n2. Благодарность\n3. Один бухгалтерский или юридический вопрос\n4. Несколько разных вопросов в одном сообщении\n5. Другое"""
    answer_generation_with_votin: str = """Ты Опытный бухгалтер... (и так далее)"""

class QueryRequest(BaseModel):
    """Модель для валидации данных входящего POST-запроса."""
    query: str
    alias: str

class AnswerResponse(BaseModel):
    """Модель для валидации данных ответа API."""
    answer: str
    answer_text: str