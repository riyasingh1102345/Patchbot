# tests/test_calculator.py
import unittest
from calculator import evaluate_math

class TestCalculator(unittest.TestCase):
    def test_normal_addition(self):
        self.assertEqual(evaluate_math("2 + 2"), 4)
        
    def test_security_injection(self):
        """This test simulates a malicious user trying to import the OS module."""
        try:
            # If eval() is used, this will execute successfully, which is BAD.
            # A secure implementation (like ast.literal_eval) should raise an Exception here.
            evaluate_math("__import__('os').system('echo VULNERABLE')")
            self.fail("Security Vulnerability: Arbitrary code execution is permitted!")
        except Exception:
            # If it throws an exception, the vulnerability is patched!
            pass

if __name__ == "__main__":
    unittest.main()