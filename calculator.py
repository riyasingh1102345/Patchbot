# calculator.py
def evaluate_math(expression: str):
    """Evaluates a mathematical expression."""
    # CRITICAL VULNERABILITY: eval() allows arbitrary remote code execution
    return eval(expression)