"""Basic arithmetic operations module."""

from typing import Union

Number = Union[int, float]


def add(a: Number, b: Number) -> Number:
    """Add two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        The sum of a and b

    """
    return a + b


def subtract(a: Number, b: Number) -> Number:
    """Subtract b from a.

    Args:
        a: First number
        b: Second number

    Returns:
        The difference a - b

    """
    return a - b


def multiply(a: Number, b: Number) -> Number:
    """Multiply two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        The product of a and b

    """
    return a * b


def divide(a: Number, b: Number) -> float:
    """Divide a by b.

    Args:
        a: Numerator
        b: Denominator

    Returns:
        The quotient a / b

    Raises:
        ZeroDivisionError: If b is zero

    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b
