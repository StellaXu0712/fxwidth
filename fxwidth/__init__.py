__version__ = '0.1.0'

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any, Optional
from coders import ColumnCoder
from validators import ColumnValidator
from alignments import Alignment

# This constant stores where the column definition will be stored
FIELD_METADATA_NAMESPACE = 'fxwidth_columndef'


class ColumnDefinition:
    """
    ColumnDefinition defines the schema for a single column
    in a fixed-width column rocord, and handles
    encoding, decoding, and validation.
    """

    def __init__(
            self,
            slice: slice,
            coder: Optional[ColumnCoder] = None,
            validator: Optional[ColumnValidator] = None
    ):
        self.slice = slice
        self.coder = coder
        self.validator = validator

    @property
    def width(self) -> int:
        return self.slice.stop - self.slice.start

    @property
    def kind(self) -> Any:
        # Can't remember what type this is!
        return self.coder.kind

    # Forgot how to do this properly...
    # see self.kind and generics
    def decode(self, line_string: str) -> Any:
        column_string = line_string[self.slice]
        return self.coder.decode(column_string)

    def encode(self, value):
        return self.coder.encode(value, self.width)

    def validate(self, instance, new):
        if self.validator:
            return self.validator.validate(instance, new, self.kind)
        else:
            return new


def column(
        slice: slice,
        coder: Optional[ColumnCoder] = None,
        validator: Optional[ColumnValidator] = None,
        **kwargs
):
    """
    Denotes a dataclass field with a ColumnDefinition instance
    saved under a specific namespace for resuse when encoding/decoding. 
    """
    definition = ColumnDefinition(slice, coder, validator)

    if 'metadata' in kwargs:
        metadata = kwargs['metadata']
    else:
        metadata = {}
    metadata[FIELD_METADATA_NAMESPACE] = definition

    return field(**kwargs, metadata=metadata)


class ColumnQuery:
    @staticmethod
    def has_definition(field) -> bool:
        return FIELD_METADATA_NAMESPACE in field.metadata and isinstance(field.metadata[FIELD_METADATA_NAMESPACE], ColumnDefinition)

    @staticmethod
    def get_definition(field) -> ColumnDefinition:
        return field.metadata[FIELD_METADATA_NAMESPACE]


class RecordQuery:
    @staticmethod
    def get_column_fields(dc) -> list[ColumnDefinition]:
        if is_dataclass(dc):
            return [field for field in fields(dc) if ColumnQuery.has_definition(field)]
        return []

    @staticmethod
    def get_column_items(dc) -> list[tuple[str, ColumnDefinition]]:
        if is_dataclass(dc):
            return [(field.name, ColumnQuery.get_definition(field)) for field in fields(dc) if ColumnQuery.has_definition(field)]
        return []

    @staticmethod
    def get_column_items_sorted(dc) -> list[tuple[str, ColumnDefinition]]:
        items = RecordQuery.get_column_items(dc)
        items.sort(key=lambda t: t[1].slice.start)

    @staticmethod
    def count_columns(dc) -> int:
        return len(RecordQuery.get_column_fields(dc))

    @staticmethod
    def has_columns(dc) -> bool:
        return is_dataclass(dc) and RecordQuery.count_columns(dc) > 0


class Record(ABC):
    @staticmethod
    def decode(dc, string):
        if not RecordQuery.has_columns(dc):
            raise Exception(
                'Can only decode dataclasses with column definitions')
        entries = {}
        for name, definition in RecordQuery.get_column_items(dc):
            entries[name] = definition.decode(string)

        return dc(**entries)

    @abstractmethod
    def encode(dc, string):
        if not RecordQuery.has_columns(dc):
            raise Exception(
                'Can only encode dataclasses with column definitions')
        # TODO: Do we need to check for gaps?
        strings = []
        for name, definition in RecordQuery.get_column_items_sorted(dc):
            value = getattr(dc, name)
            string = definition.encode(value)
            strings.append(string)

        return "".join(strings)

    def __setattr__(self, name, value):
        if name in self.__dataclass_fields__:
            field = self.__dataclass_fields__[name]
            if ColumnQuery.has_definition(field):
                definition = ColumnQuery.get_definition(field)
                value = definition.validate(self, value)
        as_super = super(type(self), self)
        as_super.__setattr__(name, value)

    # not sure how well this will work!
    # e.g. kwards in a decorator? worried...

    @staticmethod
    def configure(dc=None, *, rstrip=True):
        def record_decorator(dc):
            if isinstance(dc, Record):
                return dc

            if not RecordQuery.has_columns(dc):
                raise Exception(
                    'fxwidth can only decorate dataclasses with column metadata')

            @classmethod
            def decode(dc, string):
                return Record.decode(dc, string)

            def encode(self):
                string = Record.encode(dc, string)
                return string.rstrip() if rstrip else string

            dc.decode = decode
            dc.encode = encode
            dc.__setattr__ = Record.__setattr__
            return dc

        if (dc is None):
            return record_decorator
        else:
            return record_decorator(dc)
