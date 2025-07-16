# core/config.py

import logging

# Настройка базовой конфигурации логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (INFO и выше)
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S', # Формат времени
)

# Создание и настройка корневого логгера
logger = logging.getLogger()
logger.setLevel(logging.INFO)