from typing import Any

from rest_framework.exceptions import ValidationError


def validate_non_negative_int(value: Any) -> int:
    """
    >>> validate_non_negative_int(123)
    123

    >>> validate_non_negative_int(0)
    0

    >>> validate_non_negative_int("123")
    Traceback (most recent call last):
    ...
    rest_framework.exceptions.ValidationError: [ErrorDetail(string='Value must be a positive integer', code=400)]

    >>> validate_non_negative_int(123.3)
    Traceback (most recent call last):
    ...
    rest_framework.exceptions.ValidationError: [ErrorDetail(string='Value must be a positive integer', code=400)]

    >>> validate_non_negative_int(-123)
    Traceback (most recent call last):
    ...
    rest_framework.exceptions.ValidationError: [ErrorDetail(string='Value must be a positive integer', code=400)]

    >>> validate_non_negative_int(object())
    Traceback (most recent call last):
    ...
    rest_framework.exceptions.ValidationError: [ErrorDetail(string='Value must be a positive integer', code=400)]
    """
    if isinstance(value, int) and value >= 0:
        return value
    raise ValidationError("Value must be a positive integer", code=400)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True, raise_on_error=True)
