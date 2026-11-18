import ast
import operator

def evaluate_math(expression: str):
    """Evaluates a mathematical expression safely."""
    operators = {
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

    def _eval(node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise TypeError(f"Unsupported constant type: {type(node.value)}")
        elif isinstance(node, ast.BinOp):
            if type(node.op) in operators:
                return operators[type(node.op)](_eval(node.left), _eval(node.right))
            raise TypeError(f"Unsupported operator: {type(node.op)}")
        elif isinstance(node, ast.UnaryOp):
            if type(node.op) in operators:
                return operators[type(node.op)](_eval(node.operand))
            raise TypeError(f"Unsupported unary operator: {type(node.op)}")
        else:
            raise TypeError(f"Unsupported expression: {type(node)}")

    node = ast.parse(expression, mode='eval')
    return _eval(node.body)