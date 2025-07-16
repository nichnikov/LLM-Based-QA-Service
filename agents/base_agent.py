# agents/base_agent.py

from abc import ABC, abstractmethod
from core.data_types import PromtsChain, Parameters, AgentMemory
from agents.ai_base import LLMGenerator

class BaseAgent(ABC):
    """
    Абстрактный базовый класс для всех агентов в системе.

    Определяет общую структуру и обязательные методы, которые должны быть 
    реализованы в каждом конкретном агенте. Это обеспечивает единообразие
    и предсказуемость их поведения.
    """
    def __init__(self, 
                 prompts: PromtsChain, 
                 parameters: Parameters, 
                 memory: AgentMemory, 
                 ai_client: LLMGenerator):
        """
        Инициализатор базового агента.

        :param prompts: Объект с шаблонами промптов для LLM.
        :param parameters: Объект с параметрами конфигурации.
        :param memory: Объект для хранения состояния агента (память).
        :param ai_client: Клиент для взаимодействия с языковой моделью.
        """
        self.prompts = prompts
        self.parameters = parameters
        self.memory = memory  # Память конкретного агента
        self.ai_client = ai_client
    
    @abstractmethod
    def action_pipeline(self, *args, **kwargs):
        """
        Основной метод, который выполняет главную логику агента.
        
        Этот метод должен быть переопределен в каждом дочернем классе.
        Он инкапсулирует последовательность действий, ради которых создается агент.
        """
        pass

    def __call__(self, *args, **kwargs):
        """
        Позволяет вызывать экземпляр агента как функцию,
        что делает его использование более лаконичным.
        """
        return self.action_pipeline(*args, **kwargs)