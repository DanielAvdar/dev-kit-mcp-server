"""Calculator class that integrates basic and advanced operations."""

from typing import List

from .advanced_operations import factorial, logarithm, power, square_root
from .basic_operations import add, divide, multiply, subtract


class Calculator:
    """A calculator that can perform various operations and keep a history.

    Attributes:
        memory: The current value in memory
        history: A list of all operations performed

    """

    def __init__(self):
        """Initialize a new Calculator with memory set to 0."""
        self.memory: float = 0
        self.history: List[str] = []

    def _record_operation(self, operation: str, result: float) -> None:
        """Record an operation in the history.

        Args:
            operation: The operation performed
            result: The result of the operation

        """
        self.history.append(f"{operation} = {result}")

    def clear(self) -> None:
        """Clear the memory and set it to 0."""
        self.memory = 0
        self._record_operation("CLEAR", 0)

    def clear_history(self) -> None:
        """Clear the operation history."""
        self.history = []

    def get_history(self) -> List[str]:
        """Get the operation history.

        Returns:
            A list of strings representing the operations performed

        """
        return self.history

    def add(self, x: float) -> float:
        """Add a number to the memory.

        Args:
            x: The number to add

        Returns:
            The new value in memory

        """
        self.memory = add(self.memory, x)
        self._record_operation(f"ADD {x}", self.memory)
        return self.memory

    def subtract(self, x: float) -> float:
        """Subtract a number from the memory.

        Args:
            x: The number to subtract

        Returns:
            The new value in memory

        """
        self.memory = subtract(self.memory, x)
        self._record_operation(f"SUBTRACT {x}", self.memory)
        return self.memory

    def multiply(self, x: float) -> float:
        """Multiply the memory by a number.

        Args:
            x: The number to multiply by

        Returns:
            The new value in memory

        """
        self.memory = multiply(self.memory, x)
        self._record_operation(f"MULTIPLY {x}", self.memory)
        return self.memory

    def divide(self, x: float) -> float:
        """Divide the memory by a number.

        Args:
            x: The number to divide by

        Returns:
            The new value in memory

        """
        self.memory = divide(self.memory, x)
        self._record_operation(f"DIVIDE {x}", self.memory)
        return self.memory

    def power(self, x: float) -> float:
        """Raise the memory to the power of x.

        Args:
            x: The exponent

        Returns:
            The new value in memory

        """
        self.memory = power(self.memory, x)
        self._record_operation(f"POWER {x}", self.memory)
        return self.memory

    def square_root(self) -> float:
        """Calculate the square root of the memory.

        Returns:
            The new value in memory

        """
        self.memory = square_root(self.memory)
        self._record_operation("SQUARE_ROOT", self.memory)
        return self.memory

    def factorial(self) -> float:
        """Calculate the factorial of the memory.

        Returns:
            The new value in memory

        Raises:
            TypeError: If the memory is not an integer

        """
        if self.memory != int(self.memory):
            raise TypeError("Factorial is only defined for integers")
        self.memory = factorial(int(self.memory))
        self._record_operation("FACTORIAL", self.memory)
        return self.memory

    def logarithm(self, base: float = 10) -> float:
        """Calculate the logarithm of the memory with the given base.

        Args:
            base: The logarithm base (default is 10)

        Returns:
            The new value in memory

        """
        self.memory = logarithm(self.memory, base)
        self._record_operation(f"LOGARITHM (base {base})", self.memory)
        return self.memory


if __name__ == "__main__":
    # Demonstrate the calculator
    calc = Calculator()
    print(f"Initial memory: {calc.memory}")

    calc.add(5)
    print(f"After adding 5: {calc.memory}")

    calc.multiply(2)
    print(f"After multiplying by 2: {calc.memory}")

    calc.power(2)
    print(f"After raising to power 2: {calc.memory}")

    calc.subtract(10)
    print(f"After subtracting 10: {calc.memory}")

    calc.square_root()
    print(f"After taking square root: {calc.memory}")

    print("\nOperation history:")
    for operation in calc.get_history():
        print(f"  {operation}")
