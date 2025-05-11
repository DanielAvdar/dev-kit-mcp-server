"""A simple hello world example."""


def hello_world():
    """Print a greeting to the world."""
    print("Hello, World!")


def greet(name):
    """Greet someone by name.

    Args:
        name: The name of the person to greet

    Returns:
        A greeting message

    """
    return f"Hello, {name}!"


if __name__ == "__main__":
    hello_world()
    print(greet("Python"))
