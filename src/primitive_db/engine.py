
import re
import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.core import create_table, delete, drop_table, insert, select, update
from primitive_db.parser import parse_condition, parse_values
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

METADATA_FILE = "db_meta.json"


def print_help():
    """Выводит справку по доступным командам."""
    print("\n***Операции с данными***")
    print("Функции:")
    print("create_table <таблица> <столбец:тип> ... - создать таблицу")
    print("list_tables - показать таблицы")
    print("drop_table <таблица> - удалить таблицу")
    print("insert into <таблица> values (<значения>) - добавить запись")
    print("select from <таблица> [where <столбец> = <значение>] - читать записи")
    print("update <таблица> set <столбец> = <значение> where <условие> - изменить")
    print("delete from <таблица> where <условие> - удалить запись")
    print("info <таблица> - информация о таблице")
    print("exit - выход")
    print("help - справка\n")


def parse_command(pattern, text):
    match = re.fullmatch(pattern, text, flags=re.IGNORECASE)
    if match is None:
        raise ValueError(f"Неверный формат команды: {text}")
    return match.groups()


def check_clause(metadata, table_name, clause):
    schema = dict(item.split(":", 1) for item in metadata[table_name])

    for column, value in clause.items():
        if column not in schema:
            raise ValueError(f'Столбец "{column}" не существует.')

        if type(value).__name__ != schema[column]:
            raise ValueError(
                f'Столбец "{column}" ожидает тип {schema[column]}.'
            )


def print_rows(metadata, table_name, rows):
    columns = [item.split(":", 1)[0] for item in metadata[table_name]]

    table = PrettyTable()
    table.field_names = columns

    for record in rows:
        table.add_row([record[column] for column in columns])

    print(table)


def run():
    """Запускает цикл интерактивных команд базы данных."""
    print_help()

    while True:
        metadata = load_metadata(METADATA_FILE)
        user_input = prompt.string(">>>Введите команду: ").strip()

        if not user_input:
            continue

        command = user_input.split(maxsplit=1)[0].lower()

        try:
            if command == "insert":
                table_name, values_text = parse_command(
                    r"insert\s+into\s+(\w+)\s+values\s*(\(.*\))",
                    user_input,
                )

                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                values = parse_values(values_text)
                rows = insert(metadata, table_name, values)

                if rows is not None:
                    save_table_data(table_name, rows)

            elif command == "select":
                table_name, where_text = parse_command(
                    r"select\s+from\s+(\w+)(?:\s+where\s+(.+))?",
                    user_input,
                )

                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                clause = parse_condition(where_text) if where_text else None

                if clause is not None:
                    check_clause(metadata, table_name, clause)

                rows = select(load_table_data(table_name), clause)
                print_rows(metadata, table_name, rows)

            elif command == "update":
                table_name, set_text, where_text = parse_command(
                    r"update\s+(\w+)\s+set\s+(.+?)\s+where\s+(.+)",
                    user_input,
                )

                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                set_clause = parse_condition(set_text)
                where_clause = parse_condition(where_text)

                check_clause(metadata, table_name, set_clause)
                check_clause(metadata, table_name, where_clause)

                if "ID" in set_clause:
                    raise ValueError("Нельзя изменять столбец ID.")

                rows = load_table_data(table_name)
                matched = select(rows, where_clause)

                if not matched:
                    print("Записи по условию не найдены.")
                    continue

                update(rows, set_clause, where_clause)
                save_table_data(table_name, rows)

                for record in matched:
                    print(
                        f'Запись с ID={record["ID"]} в таблице "{table_name}" '
                        "успешно обновлена."
                    )

            elif command == "delete":
                table_name, where_text = parse_command(
                    r"delete\s+from\s+(\w+)\s+where\s+(.+)",
                    user_input,
                )

                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                where_clause = parse_condition(where_text)
                check_clause(metadata, table_name, where_clause)

                rows = load_table_data(table_name)
                matched = select(rows, where_clause)

                if not matched:
                    print("Записи по условию не найдены.")
                    continue

                delete(rows, where_clause)
                save_table_data(table_name, rows)

                for record in matched:
                    print(
                        f'Запись с ID={record["ID"]} успешно удалена '
                        f'из таблицы "{table_name}".'
                    )

            elif command == "info":
                (table_name,) = parse_command(
                    r"info\s+(\w+)",
                    user_input,
                )

                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                print(f"Таблица: {table_name}")
                print(f'Столбцы: {", ".join(metadata[table_name])}')
                print(
                    f"Количество записей: "
                    f"{len(load_table_data(table_name))}"
                )

            else:
                args = shlex.split(user_input)
                parameters = args[1:]

                if command == "exit":
                    break

                elif command == "help":
                    print_help()

                elif command == "list_tables":
                    if parameters:
                        raise ValueError(user_input)

                    if metadata:
                        for table_name in metadata:
                            print(f"- {table_name}")
                    else:
                        print("Таблиц пока нет.")

                elif command == "create_table":
                    if len(parameters) < 2:
                        raise ValueError(user_input)

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
                        raise ValueError(user_input)

                    before = metadata.copy()

                    drop_table(metadata, parameters[0])

                    if metadata != before:
                        save_metadata(METADATA_FILE, metadata)

                else:
                    print(f"Функции {command} нет. Попробуйте снова.")

        except ValueError as error:
            message = str(error).rstrip(".")
            print(f"Некорректное значение: {message}. Попробуйте снова.")
