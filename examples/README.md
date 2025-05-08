# Examples for Testing

This directory contains example Python files that are used for testing the code analysis tools. The examples are organized into three categories:

## Simple Examples

The `simple` directory contains basic Python files with simple functions, classes, and imports. These examples are used to test the basic functionality of the code analysis tools.

- `hello_world.py`: A simple script with functions for printing greetings
- `person.py`: A simple class representing a person with methods for greeting and celebrating birthdays

## Complex Examples

The `complex` directory contains more complex Python files with inheritance, decorators, and other advanced language features. These examples are used to test the code analysis tools' ability to handle more complex code structures.

- `shapes.py`: A complex example demonstrating inheritance, abstract base classes, properties, and other advanced features

## Integration Examples

The `integration` directory contains files that work together to simulate a small project. These examples are used for integration testing to verify that the code analysis tools can correctly analyze real-world code with dependencies between files.

- `__init__.py`: Package initialization file that imports from other modules
- `basic_operations.py`: Module with basic arithmetic operations
- `advanced_operations.py`: Module with more complex operations that imports from basic_operations
- `calculator.py`: Module with a Calculator class that uses both basic and advanced operations

## Usage in Tests

These examples are used in the following test files:

- `tests/test_analyzer_integration.py`: Integration tests that use the example files to test the code analyzer
- `tests/test_analyzer_simple_parameterized.py`: Parameterized tests for the CodeAnalyzer class
- `tests/test_analyzer_additional_parameterized.py`: Additional parameterized tests for the analyzer module

## Benefits

Using real-world examples for testing provides several benefits:

1. **Realistic Test Cases**: The examples simulate real-world code structures and dependencies, providing more realistic test cases than synthetic examples.
2. **Integration Testing**: The examples allow testing how the code analysis tools handle dependencies between files and modules.
3. **Documentation**: The examples serve as documentation for how the code analysis tools work with different types of Python code.
4. **Improved Coverage**: The examples help improve test coverage by testing the code analysis tools with a wider variety of code structures.
