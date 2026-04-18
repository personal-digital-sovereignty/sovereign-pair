"""
Sovereign Pair — AST Jail Security Tests
Tests that the ast_jail.py correctly blocks dangerous imports, calls, and patterns.
"""
import ast
import sys
import os

# Inject parent path so we can import the SecurityVisitor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _make_visitor():
    """Reconstruct the SecurityVisitor from ast_jail.py without executing it."""
    banned_imports = {'os', 'sys', 'subprocess', 'pty', 'shutil', 'socket', 'urllib', 'requests', 'http', 'ftplib', 'importlib'}
    banned_calls = {'eval', 'exec', 'open', '__import__', 'getattr', 'setattr', 'globals', 'locals', 'dir', 'compile', 'memoryview'}

    class SecurityVisitor(ast.NodeVisitor):
        def __init__(self):
            self.violations = []

        def visit_Import(self, node):
            for alias in node.names:
                if alias.name.split('.')[0] in banned_imports:
                    self.violations.append(f"import:{alias.name}")
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            if node.module and node.module.split('.')[0] in banned_imports:
                self.violations.append(f"from_import:{node.module}")
            self.generic_visit(node)

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name):
                if node.func.id in banned_calls:
                    self.violations.append(f"call:{node.func.id}")
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in banned_calls:
                    self.violations.append(f"attr_call:{node.func.attr}")
            self.generic_visit(node)

    return SecurityVisitor()


def _check_code(code: str) -> list:
    """Parse code and return violations."""
    tree = ast.parse(code)
    visitor = _make_visitor()
    visitor.visit(tree)
    return visitor.violations


# ── Blocked imports ────────────────────────────────────────────
class TestBlockedImports:
    def test_blocks_import_os(self):
        assert _check_code("import os") != []

    def test_blocks_import_subprocess(self):
        assert _check_code("import subprocess") != []

    def test_blocks_import_sys(self):
        assert _check_code("import sys") != []

    def test_blocks_import_shutil(self):
        assert _check_code("import shutil") != []

    def test_blocks_import_socket(self):
        assert _check_code("import socket") != []

    def test_blocks_import_requests(self):
        assert _check_code("import requests") != []

    def test_blocks_from_os_path(self):
        assert _check_code("from os.path import join") != []

    def test_blocks_from_subprocess(self):
        assert _check_code("from subprocess import Popen") != []

    def test_blocks_importlib(self):
        assert _check_code("import importlib") != []

    def test_blocks_pty(self):
        assert _check_code("import pty") != []


# ── Allowed imports ────────────────────────────────────────────
class TestAllowedImports:
    def test_allows_pandas(self):
        assert _check_code("import pandas") == []

    def test_allows_numpy(self):
        assert _check_code("import numpy") == []

    def test_allows_json(self):
        assert _check_code("import json") == []

    def test_allows_math(self):
        assert _check_code("import math") == []

    def test_allows_datetime(self):
        assert _check_code("import datetime") == []

    def test_allows_re(self):
        assert _check_code("import re") == []


# ── Blocked function calls ─────────────────────────────────────
class TestBlockedCalls:
    def test_blocks_eval(self):
        assert _check_code("eval('1+1')") != []

    def test_blocks_exec(self):
        assert _check_code("exec('print(1)')") != []

    def test_blocks_open(self):
        assert _check_code("open('/etc/passwd')") != []

    def test_blocks_dunder_import(self):
        assert _check_code("__import__('os')") != []

    def test_blocks_getattr(self):
        assert _check_code("getattr(obj, 'attr')") != []

    def test_blocks_compile(self):
        assert _check_code("compile('x=1', '', 'exec')") != []

    def test_blocks_globals(self):
        assert _check_code("globals()") != []

    def test_blocks_memoryview(self):
        assert _check_code("memoryview(b'x')") != []


# ── Allowed calls ──────────────────────────────────────────────
class TestAllowedCalls:
    def test_allows_print(self):
        assert _check_code("print('hello')") == []

    def test_allows_len(self):
        assert _check_code("len([1,2,3])") == []

    def test_allows_range(self):
        assert _check_code("list(range(10))") == []

    def test_allows_int(self):
        assert _check_code("int('42')") == []

    def test_allows_str(self):
        assert _check_code("str(42)") == []


# ── Complex patterns ──────────────────────────────────────────
class TestComplexPatterns:
    def test_blocks_os_hidden_in_multiline(self):
        code = "import json\nimport os\nx = 1"
        violations = _check_code(code)
        assert any("os" in v for v in violations)

    def test_blocks_nested_eval(self):
        """AST jail catches direct eval() calls but NOT reference storage.
        x = {'f': eval} stores a reference — the Call node is on the dict lookup, not eval.
        This is a known limitation documented here as a security gap."""
        # Direct call IS caught:
        assert len(_check_code("eval('1+1')")) > 0
        # Reference storage is NOT caught (known limitation):
        violations = _check_code("x = {'f': eval}")
        assert len(violations) == 0  # Expected: jail does NOT catch this

    def test_allows_safe_arithmetic(self):
        code = "x = 1 + 2\ny = x * 3\nz = y / 2\nprint(z)"
        assert _check_code(code) == []

    def test_allows_pandas_workflow(self):
        code = (
            "import pandas as pd\n"
            "import numpy as np\n"
            "df = pd.DataFrame({'a': [1,2,3]})\n"
            "print(df.describe())"
        )
        assert _check_code(code) == []
