"""A simple class example."""


class Person:
    """A class representing a person.

    Attributes:
        name: The person's name
        age: The person's age

    """

    def __init__(self, name, age):
        """Initialize a new Person.

        Args:
            name: The person's name
            age: The person's age

        """
        self.name = name
        self.age = age

    def greet(self):
        """Return a greeting from this person.

        Returns:
            A greeting string

        """
        return f"Hello, my name is {self.name} and I am {self.age} years old."

    def celebrate_birthday(self):
        """Increment the person's age by 1."""
        self.age += 1
        return f"Happy birthday! {self.name} is now {self.age} years old."


if __name__ == "__main__":
    # Create a person and demonstrate the methods
    alice = Person("Alice", 30)
    print(alice.greet())
    print(alice.celebrate_birthday())
    print(alice.greet())
