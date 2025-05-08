"""Test to reproduce the ASGI app loading error with create_combined_server()."""

import importlib
import unittest

import pytest


@pytest.mark.skip("Skipped because integrated_server.py has been removed")
class TestASGIAppLoading(unittest.TestCase):
    """Tests for reproducing the ASGI app loading error."""

    def test_import_with_parentheses_fails(self):
        """Test that trying to import create_combined_server() fails."""
        # This test reproduces the error:
        # ERROR: Error loading ASGI app.
        # Attribute "create_combined_server()" not found in module "py_code.integrated_server"

        # First verify we can import the module itself
        import py_code.integrated_server

        self.assertIsNotNone(py_code.integrated_server)

        # Verify we can access the function without parentheses (correct way)
        self.assertTrue(hasattr(py_code.integrated_server, "create_combined_server"))
        self.assertTrue(callable(py_code.integrated_server.create_combined_server))

        # Now try to access with parentheses (incorrect way)
        # This should raise an AttributeError
        with self.assertRaises(AttributeError):
            # This line simulates what happens when trying to access create_combined_server()
            # with parentheses in the module
            getattr(py_code.integrated_server, "create_combined_server()")

    def test_programmatic_import_with_parentheses(self):
        """Test importing using importlib to simulate ASGI import error."""
        # Import the module
        module = importlib.import_module("py_code.integrated_server")

        # Verify normal access works
        self.assertTrue(hasattr(module, "create_combined_server"))

        # Try to access with parentheses (which will fail)
        with self.assertRaises(AttributeError):
            # This simulates the ASGI app loading error
            attribute_name = "create_combined_server()"
            getattr(module, attribute_name)


if __name__ == "__main__":
    unittest.main()
