"""Tests for buildlib.interface module."""

import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'buildlib'))

import interface


class TestInterface(unittest.TestCase):

    def setUp(self):
        self.iface = interface.Interface()

    def test_write(self):
        """Test that write outputs text to stdout."""
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            self.iface.write("Hello World")
            output = mock_out.getvalue()
            self.assertIn("Hello World", output)

    def test_info(self):
        """Test info method outputs styled text."""
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            self.iface.info("Test info message")
            output = mock_out.getvalue()
            self.assertIn("Test info message", output)

    def test_success(self):
        """Test success method outputs styled text."""
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            self.iface.success("Test success message")
            output = mock_out.getvalue()
            self.assertIn("Test success message", output)

    def test_fail(self):
        """Test that fail exits with non-zero status."""
        with patch('sys.stdout', new_callable=StringIO):
            with self.assertRaises(SystemExit) as cm:
                self.iface.fail("Test failure")
            self.assertEqual(cm.exception.code, -1)

    def test_yesno_yes(self):
        """Test yesno with 'yes' input."""
        with patch('builtins.input', return_value='yes'):
            with patch('sys.stdout', new_callable=StringIO):
                result = self.iface.yesno("Accept?")
                self.assertTrue(result)

    def test_yesno_no(self):
        """Test yesno with 'no' input."""
        with patch('builtins.input', return_value='no'):
            with patch('sys.stdout', new_callable=StringIO):
                result = self.iface.yesno("Accept?")
                self.assertFalse(result)

    def test_yesno_y(self):
        """Test yesno with 'y' input."""
        with patch('builtins.input', return_value='y'):
            with patch('sys.stdout', new_callable=StringIO):
                result = self.iface.yesno("Accept?")
                self.assertTrue(result)

    def test_yesno_n(self):
        """Test yesno with 'n' input."""
        with patch('builtins.input', return_value='n'):
            with patch('sys.stdout', new_callable=StringIO):
                result = self.iface.yesno("Accept?")
                self.assertFalse(result)

    def test_yesno_default_true(self):
        """Test yesno with empty input and default True."""
        with patch('builtins.input', return_value=''):
            with patch('sys.stdout', new_callable=StringIO):
                result = self.iface.yesno("Accept?", default=True)
                self.assertTrue(result)

    def test_yesno_default_false(self):
        """Test yesno with empty input and default False."""
        with patch('builtins.input', return_value=''):
            with patch('sys.stdout', new_callable=StringIO):
                result = self.iface.yesno("Accept?", default=False)
                self.assertFalse(result)

    def test_input_with_value(self):
        """Test input method with a value."""
        with patch('builtins.input', return_value='test value'):
            with patch('sys.stdout', new_callable=StringIO):
                result = self.iface.input("Enter value:")
                self.assertEqual(result, "test value")

    def test_input_with_empty_default(self):
        """Test input method with empty input and default."""
        with patch('builtins.input', return_value=''):
            with patch('sys.stdout', new_callable=StringIO):
                result = self.iface.input("Enter value:", empty="default_val")
                self.assertEqual(result, "default_val")

    def test_choice(self):
        """Test choice method with valid selection."""
        choices = [("a", "Option A"), ("b", "Option B"), ("c", "Option C")]
        with patch('builtins.input', return_value='2'):
            with patch('sys.stdout', new_callable=StringIO):
                result = self.iface.choice("Choose:", choices)
                self.assertEqual(result, "b")

    def test_choice_default(self):
        """Test choice method with default selection."""
        choices = [("a", "Option A"), ("b", "Option B")]
        with patch('builtins.input', return_value=''):
            with patch('sys.stdout', new_callable=StringIO):
                result = self.iface.choice("Choose:", choices, default="b")
                self.assertEqual(result, "b")


if __name__ == "__main__":
    unittest.main()
