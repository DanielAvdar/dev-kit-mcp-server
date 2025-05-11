"""A more complex example demonstrating inheritance and properties."""

import math
from abc import ABC, abstractmethod
from typing import List


class Shape(ABC):
    """Abstract base class for all shapes.

    This class defines the interface that all shapes must implement.
    """

    @abstractmethod
    def area(self) -> float:
        """Calculate the area of the shape.

        Returns:
            The area as a float

        """
        pass

    @abstractmethod
    def perimeter(self) -> float:
        """Calculate the perimeter of the shape.

        Returns:
            The perimeter as a float

        """
        pass

    def __str__(self) -> str:
        """Return a string representation of the shape.

        Returns:
            A string describing the shape

        """
        return f"{self.__class__.__name__} with area {self.area():.2f} and perimeter {self.perimeter():.2f}"


class Circle(Shape):
    """A circle shape.

    Attributes:
        radius: The radius of the circle

    """

    def __init__(self, radius: float):
        """Initialize a circle with the given radius.

        Args:
            radius: The radius of the circle

        Raises:
            ValueError: If radius is negative

        """
        if radius < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = radius

    @property
    def radius(self) -> float:
        """Get the radius of the circle."""
        return self._radius

    @radius.setter
    def radius(self, value: float):
        """Set the radius of the circle.

        Args:
            value: The new radius

        Raises:
            ValueError: If value is negative

        """
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

    def area(self) -> float:
        """Calculate the area of the circle.

        Returns:
            The area as a float

        """
        return math.pi * self.radius**2

    def perimeter(self) -> float:
        """Calculate the perimeter (circumference) of the circle.

        Returns:
            The perimeter as a float

        """
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    """A rectangle shape.

    Attributes:
        width: The width of the rectangle
        height: The height of the rectangle

    """

    def __init__(self, width: float, height: float):
        """Initialize a rectangle with the given width and height.

        Args:
            width: The width of the rectangle
            height: The height of the rectangle

        Raises:
            ValueError: If width or height is negative

        """
        if width < 0 or height < 0:
            raise ValueError("Width and height cannot be negative")
        self._width = width
        self._height = height

    @property
    def width(self) -> float:
        """Get the width of the rectangle."""
        return self._width

    @width.setter
    def width(self, value: float):
        """Set the width of the rectangle.

        Args:
            value: The new width

        Raises:
            ValueError: If value is negative

        """
        if value < 0:
            raise ValueError("Width cannot be negative")
        self._width = value

    @property
    def height(self) -> float:
        """Get the height of the rectangle."""
        return self._height

    @height.setter
    def height(self, value: float):
        """Set the height of the rectangle.

        Args:
            value: The new height

        Raises:
            ValueError: If value is negative

        """
        if value < 0:
            raise ValueError("Height cannot be negative")
        self._height = value

    def area(self) -> float:
        """Calculate the area of the rectangle.

        Returns:
            The area as a float

        """
        return self.width * self.height

    def perimeter(self) -> float:
        """Calculate the perimeter of the rectangle.

        Returns:
            The perimeter as a float

        """
        return 2 * (self.width + self.height)


class Square(Rectangle):
    """A square shape (special case of rectangle).

    Attributes:
        side: The side length of the square

    """

    def __init__(self, side: float):
        """Initialize a square with the given side length.

        Args:
            side: The side length of the square

        """
        super().__init__(side, side)

    @property
    def side(self) -> float:
        """Get the side length of the square."""
        return self.width

    @side.setter
    def side(self, value: float):
        """Set the side length of the square.

        Args:
            value: The new side length

        """
        self.width = value
        self.height = value


def calculate_total_area(shapes: List[Shape]) -> float:
    """Calculate the total area of a list of shapes.

    Args:
        shapes: A list of Shape objects

    Returns:
        The sum of the areas of all shapes

    """
    return sum(shape.area() for shape in shapes)


if __name__ == "__main__":
    # Create some shapes
    circle = Circle(5)
    rectangle = Rectangle(4, 6)
    square = Square(3)

    # Print information about each shape
    print(circle)
    print(rectangle)
    print(square)

    # Calculate and print the total area
    shapes = [circle, rectangle, square]
    total_area = calculate_total_area(shapes)
    print(f"Total area of all shapes: {total_area:.2f}")
