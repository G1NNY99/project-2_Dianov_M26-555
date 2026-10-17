import ast

from primitive_db.constants import VALID_VALUE_TYPES


def parse_condition(text):
    """Преобразует условие вида age = 28 в словарь."""
    column, separator, raw_value = text.partition("=")

    column = column.strip()
    raw_value = raw_value.strip()

    if not separator or not column or not raw_value:
        raise ValueError("Некорректный формат условия.")

    if raw_value.lower() == "true":
        value = True
    elif raw_value.lower() == "false":
        value = False
    else:
        try:
            value = ast.literal_eval(raw_value)
        except (ValueError, SyntaxError):
            raise ValueError(f"Некорректное значение: {raw_value}.") from None

    if type(value) not in VALID_VALUE_TYPES:
        raise ValueError("Поддерживаются только типы int, str и bool.")

    return {column: value}


def parse_values(text):
    """Преобразует список значений INSERT в список Python."""
    if not (text.startswith("(") and text.endswith(")")):
        raise ValueError("Значения должны быть заключены в круглые скобки.")

    try:
        node = ast.parse(f"[{text[1:-1]}]", mode="eval").body
    except SyntaxError:
        raise ValueError("Некорректный список значений.") from None

    if not isinstance(node, ast.List):
        raise ValueError("Некорректный список значений.")

    values = []

    for item in node.elts:
        if isinstance(item, ast.Name) and item.id in ("true", "false"):
            value = item.id == "true"
        else:
            try:
                value = ast.literal_eval(item)
            except (ValueError, SyntaxError, TypeError):
                raise ValueError("Некорректное значение.") from None

        if type(value) not in VALID_VALUE_TYPES:
            raise ValueError("Поддерживаются только типы int, str и bool.")

        values.append(value)

    return values
