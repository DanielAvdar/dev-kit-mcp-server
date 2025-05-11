"""Advanced arithmetic operations module."""

import math

from .basic_operations import Number


def power(base: Number, exponent: Number) -> Number:
    """Raise base to the power of exponent.

    Args:
        base: The base number
        exponent: The exponent

    Returns:
        base raised to the power of exponent

    """
    return base**exponent


def square_root(x: Number) -> float:
    """Calculate the square root of x.

    Args:
        x: The number to find the square root of

    Returns:
        The square root of x

    Raises:
        ValueError: If x is negative

    """
    if x < 0:
        raise ValueError("Cannot calculate square root of a negative number")
    return math.sqrt(x)


def factorial(n: int) -> int:
    """Calculate the factorial of n.

    Args:
        n: A non-negative integer

    Returns:
        The factorial of n

    Raises:
        ValueError: If n is negative
        TypeError: If n is not an integer

    """
    if not isinstance(n, int):
        raise TypeError("Factorial is only defined for integers")
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)


def logarithm(x: Number, base: Number = 10) -> float:
    """Calculate the logarithm of x with the given base.

    Args:
        x: The number to calculate the logarithm of
        base: The logarithm base (default is 10)

    Returns:
        The logarithm of x with the given base

    Raises:
        ValueError: If x is negative or zero, or if base is negative, zero, or 1

    """
    if x <= 0:
        raise ValueError("Logarithm is not defined for non-positive numbers")
    if base <= 0 or base == 1:
        raise ValueError("Logarithm base must be positive and not equal to 1")
    return math.log(x, base)
