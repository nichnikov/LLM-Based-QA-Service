# utils/utils.py

import functools
import multiprocessing.pool

def build_document_link(alias: str, module_id: str, document_id: str, alias_to_site: dict) -> str:
    """
    Собирает URL-адрес документа на основе его идентификаторов и алиаса сайта.

    :param alias: Алиас сайта (например, 'bss.vip').
    :param module_id: ID модуля документа.
    :param document_id: ID документа.
    :param alias_to_site: Словарь для сопоставления алиаса с полным адресом сайта.
    :return: Полная ссылка на документ.
    """
    site_address = alias_to_site.get(alias, "")
    if not site_address:
        return "" # Возвращаем пустую строку, если алиас не найден
        
    link = f"{site_address}?#/document/{module_id}/{document_id}/"
    return link

def chunks(lst: list, n: int):
    """
    Разделяет список на части (чанки) заданного размера.

    :param lst: Входной список.
    :param n: Размер одного чанка.
    :yield: Последовательность чанков.
    """
    for i in range(0, len(lst), n):
        yield lst[i: i + n]

def timeout(max_timeout):
    """
    Декоратор для ограничения времени выполнения функции.
    Внимание: Этот декоратор использует ThreadPool и может быть не самым 
    эффективным решением в асинхронном коде. В asyncio лучше использовать
    `asyncio.wait_for`.
    """
    def timeout_decorator(item):
        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            try:
                return async_result.get(max_timeout)
            except multiprocessing.TimeoutError:
                raise TimeoutError(f"Выполнение функции превысило таймаут в {max_timeout} секунд.")
        return func_wrapper
    return timeout_decorator