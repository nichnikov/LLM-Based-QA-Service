# main.py

from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated

from piplines.expert_bot import bot_pipeline, BotDependencies
from core.data_types import QueryRequest, AnswerResponse, Settings, Parameters, PromtsChain, AgentMemory
from agents.ai_base import LLMGenerator
from services.retriever import AsyncPostRequest
from agents.search_agent import SearchAgent
from agents.classifying_agent import ClassifierAgent
from agents.search_agent_units import AnalysisUnit, VotingUnit, AnswerGenerator, MemoryManager


# --- Создание зависимостей ---

def get_settings() -> Settings:
    return Settings()

def get_parameters() -> Parameters:
    return Parameters()

def get_prompts() -> PromtsChain:
    """
    Зависимость для получения промптов.
    Загружает промпты из внешнего JSON-файла.
    """
    # Путь к файлу с промптами
    PROMPTS_FILE_PATH = "configs/prompts.json"
    return PromtsChain.from_file(PROMPTS_FILE_PATH)

# Создаем зависимости как функции, которые FastAPI сможет вызывать
def get_ai_client(settings: Annotated[Settings, Depends(get_settings)]) -> LLMGenerator:
    return LLMGenerator(api_key=settings.openai_api_key)

def get_retriever(parameters: Annotated[Parameters, Depends(get_parameters)]) -> AsyncPostRequest:
    return AsyncPostRequest(base_url=parameters.retrieval_base_url)

def get_classifier_agent(
    prompts: Annotated[PromtsChain, Depends(get_prompts)],
    parameters: Annotated[Parameters, Depends(get_parameters)],
    ai_client: Annotated[LLMGenerator, Depends(get_ai_client)],
) -> ClassifierAgent:
    # Память для классификатора обычно не требует сохранения между запросами
    return ClassifierAgent(prompts, parameters, AgentMemory(), ai_client)

def get_search_agent(
    prompts: Annotated[PromtsChain, Depends(get_prompts)],
    parameters: Annotated[Parameters, Depends(get_parameters)],
    ai_client: Annotated[LLMGenerator, Depends(get_ai_client)],
    retriever: Annotated[AsyncPostRequest, Depends(get_retriever)],
) -> SearchAgent:
    # Создание юнитов, которые будут внедрены в SearchAgent
    analysis_unit = AnalysisUnit(ai_client, prompts, parameters)
    voting_unit = VotingUnit(ai_client, prompts, parameters)
    answer_generator = AnswerGenerator(ai_client, prompts, parameters)
    memory_manager = MemoryManager(parameters)
    
    # Память для поисковика создается новая для каждого запроса внутри агента
    return SearchAgent(
        prompts=prompts,
        parameters=parameters,
        memory=AgentMemory(),
        ai_client=ai_client,
        retriever=retriever,
        analysis_unit=analysis_unit,
        voting_unit=voting_unit,
        answer_generator=answer_generator,
        memory_manager=memory_manager,
        voting_unit_is=True # Конфигурация
    )


# Создаем экземпляр FastAPI
app = FastAPI(title="LLM Chain Service")


@app.post("/expert_bot/", response_model=AnswerResponse)
async def process_query(
    request: QueryRequest,
    # FastAPI автоматически создаст и передаст зависимости
    classifier: Annotated[ClassifierAgent, Depends(get_classifier_agent)],
    searcher: Annotated[SearchAgent, Depends(get_search_agent)],
):
    """
    Основной эндпоинт для обработки запросов пользователя.
    Использует систему внедрения зависимостей FastAPI для получения агентов.
    """
    # Собираем зависимости для основного конвейера
    deps = BotDependencies(classifier_agent=classifier, search_agent=searcher)
    
    # Вызываем основной конвейер
    answer_text = await bot_pipeline(request.query, request.alias, deps)
    print(f"Ответ: {answer_text}")
        
    if not answer_text or answer_text == "НЕТ ОТВЕТА":
        raise HTTPException(status_code=404, detail="No answer found")
    
    # В модели AnswerResponse два поля, формируем соответствующий ответ
    return AnswerResponse(answer=answer_text, answer_text=answer_text)

# Запуск сервера (если файл запущен напрямую)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)