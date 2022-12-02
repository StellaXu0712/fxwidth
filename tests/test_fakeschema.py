from dataclasses import dataclass
from typing import Any
from fxwidth import __version__, ColumnQuery, RecordQuery, column, Record
from fxwidth.coders import StaticCoder, IntCoder, StringCoder, BoolCoder
from fxwidth.validators import EqualityValidator, MinMaxValidator, MaxLengthValidator, FixedLengthValidator
import pytest

happyfile = \
"""
 0  0Admin     1972-01-011
 0  1Bob       1990-10-050
 0  3Wendy     1990-10-05
 0999JeromeVonB1990-10-051
 2123   2.5 180.5 2000 001 111 111 111 111 110 000    60    45
 2123   2.5 180.5 2000 001 111 111 111 111 110 000    60
 2123   2.5 180.550000 001 111 111 111 111 110 000
"""

sadfile = \
"""
 0  0Admin     1972-01-011
 0  1Bob       1990-10-050
 0  3Wendy     1990-10-05
 0999JeromeVonB1990-10-051
 2123   2.5 180.551000 001 111 111 111 111 110 000    60    45
 2123   2.5 180.5 2000 001 111 111 111 111 110 000    60    45  2 45
 2123   2.5 180.5 2000 001 111 111 111 111 110 000   1.5
 2123   2.5 180.5AA000 001 111 111 111 111 110 000
 21.5   2.5 180.5 2000 001 111 111 111 111 110 000
"""

# Declare your schemas here
# ....

@Record.default
class User:
    section_id: int = column(slice(0, 2), IntCoder(), EqualityValidator(0))
    user_id: int = column(slice(2, 5),IntCoder(), MinMaxValidator(0, 999))
    user_name: str = column(slice(5,15), StringCoder(), MaxLengthValidator(10))
    user_birthday: str = column(slice(15,25),StringCoder(),FixedLengthValidator(10))
    user_verified: bool = column(slice(25,26),BoolCoder())

def test_version():
    assert __version__ == '0.1.0'

def test_happy_user_reencode():
    expected = " 0  4Admin     1972-01-011"

    print("has_column ", RecordQuery.has_columns(expected))

    decoded = User.decode(expected)
    print('User section id', decoded.section_id)
    print(decoded)
    actual = decoded.encode()

    assert expected == actual

    

# def test_happy_solarpanel_reencode():
#     expected = " 2123   2.5 180.5 2000 001 111 111 111 111 110 000    60    45"

#     decoded = User.decode(expected)
#     actual = decoded.encode()
    
#     assert expected == actual


# def test_sad_user_reencode():
#     expected = " 0  0Admin     1972-01-011"

#     with pytest.raises(____):
#         User.decode(expected)


# def test_sad_solarpanel_reencode():
#     expected = " 2123   2.5 180.5 2000 001 111 111 111 111 110 000    60    45  2 45"

#     with pytest.raises(____):
#         SolarPanel.decode(expected)

# def test_decode_and_encode_happy():
#     # Iterate over all the lines and make objects from the schemas
#     #
#     pass