VALID_TYPES = {"int", "str", "bool"}


def create_table(metadata, table_name, columns):
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


def drop_table(metadata, table_name):

    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]

    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata