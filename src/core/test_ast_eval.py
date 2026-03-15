import ast
import operator

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def safe_math_eval(expr: str):
    allowed_chars = set("0123456789.+-*/() ")
    clean_expr = "".join(c for c in expr if c in allowed_chars)
    try:
        node = ast.parse(clean_expr, mode='eval')
        def _eval(node):
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.BinOp):
                return ALLOWED_OPERATORS[type(node.op)](_eval(node.left), _eval(node.right))
            elif isinstance(node, ast.UnaryOp):
                return ALLOWED_OPERATORS[type(node.op)](_eval(node.operand))
            else:
                raise TypeError(node)
        return float(_eval(node.body))
    except Exception as e:
        return f"#ERROR! {e}"

print(safe_math_eval("(-55545.0)+2"))
print(safe_math_eval("10 - (-5.0)"))
print(safe_math_eval("(-10.0) * (20.0)"))
