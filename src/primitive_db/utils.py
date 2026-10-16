import json
from pathlib import Path


def load_metadata(filepath):
    """Загружает метаданные из JSON-файла."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_table_data(table_name):
    """Загружает записи таблицы из JSON-файла."""
    filepath = Path("data") / f"{table_name}.json"

    try:
        with filepath.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохраняет записи таблицы в JSON-файл."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    filepath = data_dir / f"{table_name}.json"

    with filepath.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def delete_table_data(table_name):
    filepath = Path("data") / f"{table_name}.json"
    filepath.unlink(missing_ok=True)