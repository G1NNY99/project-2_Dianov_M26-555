from pathlib import Path

META_FILE = "db_meta.json"
DATA_DIR = Path("data")

TYPE_MAPPING = {
    "int": int,
    "str": str,
    "bool": bool,
}

VALID_TYPES = frozenset(TYPE_MAPPING)
VALID_VALUE_TYPES = tuple(TYPE_MAPPING.values())
