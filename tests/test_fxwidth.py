from dataclasses import dataclass
from typing import Any
from fxwidth import __version__, ColumnQuery, RecordQuery, column


def test_version():
    assert __version__ == '0.1.0'


def test_column_queries():
    @dataclass
    class ClassWithColumns:
        a: Any = column(slice(0, 10))
        b: Any = column(slice(10, 20))
        c: Any = column(slice(20, 30))
        z: int = 10

    instance_with_columns = ClassWithColumns(10, 20, 30)

    assert RecordQuery.has_columns(instance_with_columns)
    assert RecordQuery.count_columns(instance_with_columns) == 3
