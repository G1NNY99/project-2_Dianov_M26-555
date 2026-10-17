import time
from functools import wraps


def handle_db_errors(func):
    """Обрабатывает ошибки при выполнении операций с базой данных."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Вызывает функцию и обрабатывает ожидаемые ошибки базы данных."""
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: файл данных не найден.")
        except KeyError as error:
            print(f"Ошибка: таблица или столбец {error} не найден.")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")

    return wrapper


def confirm_action(action_name):
    """Создаёт декоратор для подтверждения потенциально опасной операции.

    Args:
        action_name: Название операции в запросе подтверждения.

    Returns:
        Декоратор, разрешающий выполнение функции после ответа «y».
    """

    def decorator(func):
        """Оборачивает переданную функцию проверкой подтверждения."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            """Выполняет функцию только после подтверждения пользователем."""
            answer = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')

            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Измеряет время выполнения функции и выводит результат измерения.

    Args:
        func: Функция, время выполнения которой необходимо измерить.

    Returns:
        Обёртка, возвращающая результат исходной функции.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Выполняет функцию и выводит затраченное время."""
        start_time = time.monotonic()

        result = func(*args, **kwargs)

        elapsed_time = time.monotonic() - start_time
        print(f"Функция {func.__name__} выполнилась за {elapsed_time:.3f} секунд")

        return result

    return wrapper


def create_cacher():
    """Создаёт замыкание для кэширования результатов запросов.

    Returns:
        Функция, сохраняющая результаты вычислений по ключам.
    """
    cache = {}

    def cache_result(key, value_func):
        """Возвращает значение из кэша или вычисляет его при отсутствии."""
        if key not in cache:
            cache[key] = value_func()

        return cache[key]

    return cache_result
