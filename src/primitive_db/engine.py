import shlex

import prompt

from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata

METADATA_FILE = "db_meta.json"


def print_help():
    """Выводит справку по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> "
        "<столбец1:тип> ... - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Запускает основной цикл команд базы данных."""
    print_help()

    while True:
        metadata = load_metadata(METADATA_FILE)
        user_input = prompt.string(">>>Введите команду: ")

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0]
        parameters = args[1:]

        if command == "exit":
            break

        elif command == "help":
            print_help()

        elif command == "list_tables":
            if parameters:
                print(
                    f"Некорректное значение: {user_input}. "
                    "Попробуйте снова."
                )
            elif metadata:
                for table_name in metadata:
                    print(f"- {table_name}")
            else:
                print("Таблиц пока нет.")

        elif command == "create_table":
            if len(parameters) < 2:
                print(
                    f"Некорректное значение: {user_input}. "
                    "Попробуйте снова."
                )
                continue

            before = metadata.copy()

            create_table(
                metadata,
                parameters[0],
                parameters[1:],
            )

            if metadata != before:
                save_metadata(METADATA_FILE, metadata)

        elif command == "drop_table":
            if len(parameters) != 1:
                print(
                    f"Некорректное значение: {user_input}. "
                    "Попробуйте снова."
                )
                continue

            before = metadata.copy()

            drop_table(metadata, parameters[0])

            if metadata != before:
                save_metadata(METADATA_FILE, metadata)

        else:
            print(f"Функции {command} нет. Попробуйте снова.")