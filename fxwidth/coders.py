from abc import ABC, abstractmethod
from fxwidth.alignments import Alignment


class ColumnCoder(ABC):
    @property
    @abstractmethod
    def kind(self):
        pass

    @abstractmethod
    def decode(self, string):
        pass

    @abstractmethod
    def encode(self, value, width):
        pass

    @staticmethod
    def is_blank(string):
        return str.isspace(string) or not string


@ColumnCoder.register
class OptionalCoder:
    def __init__(self, other_coder: ColumnCoder):
        self.other_coder = other_coder

    @property
    def kind(self):
        return self.other_coder.kind

    def decode(self, string):
        if ColumnCoder.is_blank(string):
            return None
        else:
            return self.other_coder.decode(string)

    def encode(self, value, width):
        if value is None:
            return f'{str():{width}}'
        else:
            return self.other_coder.decode(value, width)


@ColumnCoder.register
class IntCoder:
    def __init__(self, blank_if_zero=False):
        self.blank_if_zero = blank_if_zero

    @property
    def kind(self):
        return int

    def decode(self, string):
        if self.blank_if_zero and ColumnCoder.is_blank(string):
            return int(0)
        return int(string)

    def encode(self, value, width):
        if self.blank_if_zero and value == 0:
            return f'{str():{width}}'
        return f'{value:>{width}d}'


@ColumnCoder.register
class FloatCoder:
    def __init__(self, precision=1, blank_if_zero=False, int_if_whole=True):
        self.precision = precision
        self.blank_if_zero = blank_if_zero
        self.int_if_whole = int_if_whole

    @property
    def kind(self):
        return float

    def decode(self, string):
        if self.blank_if_zero and ColumnCoder.is_blank(string):
            return float(0.0)
        return float(string)

    def encode(self, value, width):
        if self.blank_if_zero and value == 0.0:
            return f'{str():{width}}'
        if self.int_if_whole and value.is_integer():
            return f'{value:>{width}.0f}'
        return f'{value:>{width}.{self.precision}f}'


@ColumnCoder.register
class BoolCoder:
    def __init__(self, true='1', false='0', blank_if_false=True):
        self.true = true
        self.false = false
        self.blank_if_false = blank_if_false

    @property
    def kind(self):
        return bool

    def decode(self, string):
        string = string.strip()
        if self.blank_if_false and ColumnCoder.is_blank(string):
            return False
        if string == self.true:
            return True
        if string == self.false:
            return False
        raise Exception(f'BoolCoder found an unknown case "{string}"')

    def encode(self, value, width):
        string = self.true if value else self.false
        return f'{string:>{width}}'


@ColumnCoder.register
class StringCoder:
    def __init__(self, align=Alignment.LEFT, strip=True, preserved=False):
        self.align = align
        self.strip = strip
        self.preserved = preserved

    @property
    def kind(self):
        return str

    def decode(self, string):
        if self.strip and not self.preserved:
            return string.strip()
        return string

    def encode(self, value, width):
        # Edge case for handling indefinite and undefined endings to lines
        if self.preserved:
            return value
        arrow = '<'
        if self.align == Alignment.RIGHT:
            arrow = '>'
        return f'{value:{arrow}{width}}'


@ColumnCoder.register
class RecordCoder:
    def __init__(self, record):
        self.record = record

    @property
    def kind(self):
        return self.record

    def decode(self, string):
        return self.record.decode(string)

    def encode(self, value, width):
        return self.record.encode(value)


@ColumnCoder.register
class ListCoder:
    def __init__(self, max, item_column, variadic=False):
        self.max = max
        self.item_column = item_column
        self.variadic = variadic

    @property
    def kind(self):
        return list

    def decode(self, string):
        items = []
        for i in range(0, self.item_column.width * self.max):
            start = i * self.item_column.width
            stop = start + self.item_column.width

            item_string = string[start:stop]

            if ColumnCoder.is_blank(item_string) and self.variadic:
                return items
            if ColumnCoder.is_blank(item_string):
                raise Exception('Ran out of items to decode mid-way')

            value = self.item_column.decode(item_string)
            items.append(value)

        return items

    def encode(self, value, width):
        strings = [self.item_column.encode(item) for item in value]
        string = "".join(strings)
        return f'{string:<{width}}'


@ColumnCoder.register
class StaticCoder:
    def __init__(self, string):
        self.string = string

    @property
    def kind(self):
        return str

    def decode(self, string):
        return self.string

    def encode(self, value, width):
        return self.string
