# fakeschema (for testing)

This describes a fake schema for a fixed-width column file

Numeric types are right aligned.
String types are normally left-aligned, but are sometimes right-aligned.

## User

Columns:

1. Always `0` (2 characters wide), signifying this is a User record. - `StaticCoder`
2. ID, Integer, 3 characters, maximum `999` - `IntCoder`
3. Name, String, 10 characters, left-aligned - `StringCoder`
4. Date of birth, String, 10 characters, left-aligned. Format: `yyyy-mm-dd`. No special type considerations required - `StringCoder`
5. Verified - Boolean flag, 0 or 1, if blank then treat as false - `BoolCoder`

Example rows:

```
 0  0Admin     1972-01-011
 0  1Bob       1990-10-050
 0  3Wendy     1990-10-05
 0999JeromeVonB1990-10-051
```

## Daily Schedule

This is an embedded record used by others.
It has 24 Boolean flag fields, each 3 fields separated by a single space (`StaticCoder`)
E.g.
`000 001 111 111 111 111 110 000`
Is equal to
`12am: off, 1am: off, 2am: off, 3am: off, 4am: off, 5am: on ...`

## Solar Panels

1. Always `2` (2 characters wide)
2. ID - 3 chars, max 999
3. Maximum Power - 6 chars, float, precision: 1 digit
4. Orientation - 360 degrees, 6 chars, floating point, must be validated (e.g. can be 0 to 360 but not higher or lower). 0/360 represents north
5. BIOS Version - int, 2 char, max 50 - must be validated
6. Daily Expected Usage - embedded Daily Schedule
7. Optional: List of optional rotations, maximum 4 allowed, blank is interpreted as null/None (no change made), maximum rotation is 360 (full rotation), 3 characters each, displayed as integers but interpreted as floating point

Should be trimmed from the right hand side if no optional rotations.

```
 2123   2.5 180.5 2000 001 111 111 111 111 110 000    60    45
 2123   2.5 180.5 2000 001 111 111 111 111 110 000    60
 2123   2.5 180.550000 001 111 111 111 111 110
```

And failing cases

```
 2123   2.5 180.551000 001 111 111 111 111 110 000    60    45
 2123   2.5 180.5 2000 001 111 111 111 111 110 000    60    45  2 45
 2123   2.5 180.5 2000 001 111 111 111 111 110 000   1.5
```
