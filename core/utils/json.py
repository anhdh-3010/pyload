import json
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from enum import Enum
from uuid import UUID


def to_jsonable(value):
    if value is None or isinstance(value, str | int | float | bool):
        return value

    if isinstance(value, UUID):
        return str(value)

    if isinstance(value, Enum):
        return to_jsonable(value.value)

    if isinstance(value, datetime | date):
        return value.isoformat()

    if isinstance(value, Mapping):
        return {str(key): to_jsonable(item) for key, item in value.items()}

    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [to_jsonable(item) for item in value]

    return value


def dumps_json(value) -> str:
    return json.dumps(to_jsonable(value))


def loads_json(value: str | bytes | bytearray):
    if isinstance(value, bytes | bytearray):
        value = value.decode("utf-8")
    return json.loads(value)
