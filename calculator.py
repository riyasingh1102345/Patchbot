import ast
import operator

def evaluate_math(expression: str):
    """Evaluates a mathematical expression safely."""
    ops = {
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
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        elif isinstance(node, ast.Num):  # For older Python compatibility
            return node.n
        elif isinstance(node, ast.BinOp):
            if type(node.op) in ops:
                return ops[type(node.op)](_eval(node.left), _eval(node.right))
            raise TypeError(f"Unsupported operator: {type(node.op)}")
        elif isinstance(node, ast.UnaryOp):
            if type(node.op) in ops:
                return ops[type(node.op)](_eval(node.operand))
            raise TypeError(f"Unsupported operator: {type(node.op)}")
        else:
            raise TypeError(f"Unsupported expression node: {type(node)}")

    parsed = ast.parse(expression.strip(), mode='eval')
    return _eval(parsed.body)