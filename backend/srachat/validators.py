from typing import Any

from rest_framework.exceptions import ValidationError


def int_validator(value: Any) -> int:
    """
    >>> int_validator(123)
    123

    >>> int_validator("123")
    Traceback (most recent call last):
    ...
    rest_framework.exceptions.ValidationError: [ErrorDetail(string='Value must be a positive integer', code=400)]

    >>> int_validator(123.3)
    Traceback (most recent call last):
    ...
    rest_framework.exceptions.ValidationError: [ErrorDetail(string='Value must be a positive integer', code=400)]

    >>> int_validator(-123)
    Traceback (most recent call last):
    ...
    rest_framework.exceptions.ValidationError: [ErrorDetail(string='Value must be a positive integer', code=400)]

    >>> int_validator(object())
    Traceback (most recent call last):
    ...
    rest_framework.exceptions.ValidationError: [ErrorDetail(string='Value must be a positive integer', code=400)]
    """
    if isinstance(value, int) and value > 0:
        return value
    raise ValidationError("Value must be a positive integer", code=400)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
