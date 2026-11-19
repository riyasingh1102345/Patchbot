import ast
import operator

# Supported operators for safe mathematical evaluation
SUPPORTED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def _eval_node(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.Num):  # For older Python compatibility
        return node.n
    elif isinstance(node, ast.BinOp):
        if type(node.op) in SUPPORTED_OPERATORS:
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            return SUPPORTED_OPERATORS[type(node.op)](left, right)
        raise ValueError(f"Unsupported operator: {type(node.op)}")
    elif isinstance(node, ast.UnaryOp):
        if type(node.op) in SUPPORTED_OPERATORS:
            operand = _eval_node(node.operand)
            return SUPPORTED_OPERATORS[type(node.op)](operand)
        raise ValueError(f"Unsupported unary operator: {type(node.op)}")
    else:
        raise ValueError(f"Unsupported expression node: {type(node)}")

def evaluate_math(expression: str):
    """Evaluates a mathematical expression safely without using eval()."""
    if not isinstance(expression, str):
        raise TypeError("Expression must be a string")
    
    parsed = ast.parse(expression.strip(), mode='eval')
    return _eval_node(parsed.body)