# agents/classifying_agent.py

import os
import sys
import re
from agents.base_agent import BaseAgent

# Добавление корневой директории проекта в sys.path для корректного импорта
# Эта практика полезна для запуска скрипта напрямую, но в проде лучше использовать
# установку пакета или запуск через uvicorn из корня проекта.
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file_path))
sys.path.append(project_root)


class ClassifierAgent(BaseAgent):
    """
    Агент для классификации входящих сообщений от пользователя.
    
    Использует LLM для определения категории запроса (например, приветствие, 
    бухгалтерский вопрос, благодарность и т.д.), что позволяет системе
    выбрать правильный конвейер для обработки.
    """
    
    def action_pipeline(self, query: str) -> str:
        """
        Выполняет классификацию запроса.

        :param query: Входящий текст от пользователя.
        :return: Строка с результатом классификации от LLM.
        """
        # Форматируем промпт, подставляя в него запрос пользователя
        prompt = self.prompts.classication.format(query)
        
        # Вызываем LLM с параметрами, специфичными для задачи классификации
        return self.ai_client(
            prompt, 
            model=self.parameters.ai_model_classifier, 
            temperature=0.5, 
            max_tokens=1000
        )

# Этот блок кода выполняется только при прямом запуске файла.
# Он полезен для быстрой проверки и демонстрации работы агента.
if __name__ == "__main__":
    # Импорты для демонстрационного запуска
    from piplines.dependencies import parameters, class_memory, ai_client, prompts

    # Создание экземпляра агента
    agent = ClassifierAgent(prompts, parameters, class_memory, ai_client)
    
    # Пример запроса
    query = """Добрый день! У работницы предприятия двое детей возраста до 18 лет. Подскажите пожалуйста с 2025года на второго ребенка предоставляется заявление на вычеты по НДФЛ? Спасибо!"""
    
    # Вызов агента
    answer = agent(query)

    print(f"Ответ классификатора: {answer}")

    # Извлечение цифровой метки из ответа
    num = re.findall(r"\d{1}", answer)
    print(f"Извлеченные числовые метки: {[int(i) for i in num]}")