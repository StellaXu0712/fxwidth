from abc import ABC, abstractmethod
from typing import Any


class ColumnValidator(ABC):
    @abstractmethod
    def validate(self, record: Any, new, kind):
        return new


# Needs to be made generic!
class MinMaxValidator(ColumnValidator):
    def __init__(self, min, max):
        self.min = min
        self.max = max

    def validate(self, record: Any, new, kind):
        if not isinstance(new, kind):
            raise Exception('Not the right instance')
        if new < self.min:
            raise Exception('Value is too low')
        if new > self.max:
            raise Exception('Value is too high')
        return new


class AzimuthValidator(ColumnValidator):
    def validate(self, record: Any, new, kind):
        if not isinstance(new, kind):
            raise Exception('Not the right instance')

        # You will just keep rotating, no errors required!
        return new % 360


class MaxLengthValidator(ColumnValidator):
    def __init__(self, max):
        self.max = max

    def validate(self, instance, new, kind):
        if len(new) > self.max:
            raise Exception('Exceeded maximum length')
        return new


class FixedLengthValidator(ColumnValidator):
    def __init__(self, length):
        self.length = length

    def validate(self, instance, new, kind):
        if len(new) != self.length:
            raise Exception('Exceeded required length')
        return new

# Prototype for Clock Validator:


class ClockValidator(ColumnValidator):
    def validate(self, instance, new, kind):
        if not isinstance(new, kind):
            raise Exception('Not the right instance')

        # Clock is stored in 24 hours, stored like a clock (25.00 -> 1.00)
        return new % 24
