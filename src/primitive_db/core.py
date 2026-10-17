from primitive_db.constants import TYPE_MAPPING, VALID_TYPES
from primitive_db.decorators import confirm_action, handle_db_errors, log_time
from primitive_db.utils import delete_table_data, load_table_data


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт таблицу с автоматически добавляемым столбцом ID:int.

    Args:
        metadata: Словарь схем существующих таблиц.
        table_name: Имя создаваемой таблицы.
        columns: Описания столбцов в формате «имя:тип».

    Returns:
        Словарь метаданных после попытки создания таблицы.
    """
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    validated_columns = ["ID:int"]
    used_names = {"ID"}

    for column in columns:
        if column.count(":") != 1:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        column_name, column_type = column.split(":", 1)

        if not column_name or column_type not in VALID_TYPES:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        if column_name == "ID" and column_type == "int":
            continue

        if column_name in used_names:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        used_names.add(column_name)
        validated_columns.append(column)

    metadata[table_name] = validated_columns

    print(
        f'Таблица "{table_name}" успешно создана со столбцами: '
        f"{', '.join(validated_columns)}"
    )

    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных и связанный файл данных.

    Args:
        metadata: Словарь схем существующих таблиц.
        table_name: Имя удаляемой таблицы.

    Returns:
        Словарь метаданных после попытки удаления таблицы.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    delete_table_data(table_name)
    del metadata[table_name]

    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Добавляет запись в таблицу с автоматическим присвоением ID."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    columns = metadata[table_name][1:]

    if len(values) != len(columns):
        print(f"Ошибка: Ожидалось {len(columns)} значений, получено {len(values)}.")
        return None

    new_record = {}

    for column, value in zip(columns, values):
        column_name, column_type = column.split(":")
        expected_type = TYPE_MAPPING[column_type]

        if type(value) is not expected_type:
            print(
                f'Ошибка: Неверный тип значения столбца "{column_name}". '
                f"Ожидался тип {column_type}."
            )
            return None

        new_record[column_name] = value

    table_data = load_table_data(table_name)

    new_id = (
        max(
            (record["ID"] for record in table_data),
            default=0,
        )
        + 1
    )

    new_record = {"ID": new_id, **new_record}
    table_data.append(new_record)

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')

    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает все записи или записи, соответствующие условию."""
    if where_clause is None:
        return table_data

    return [
        record
        for record in table_data
        if all(record.get(column) == value for column, value in where_clause.items())
    ]


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет записи, соответствующие заданному условию."""
    for record in table_data:
        if all(record.get(column) == value for column, value in where_clause.items()):
            record.update(set_clause)

    return table_data


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):
    """Удаляет записи, соответствующие условию."""
    if not where_clause:
        return table_data

    table_data[:] = [
        record
        for record in table_data
        if not all(
            record.get(column) == value for column, value in where_clause.items()
        )
    ]

    return table_data
