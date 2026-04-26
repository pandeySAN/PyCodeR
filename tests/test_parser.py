import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parser.ast_parser import ASTParser
from src.parser.symbol_table import build_symbol_table


class TestASTParser(unittest.TestCase):
    
    def test_parse_simple_code(self):
        code = "x = 5\ny = 10"
        parser = ASTParser(code)
        tree = parser.parse()
        self.assertIsNotNone(tree)
        
    def test_parse_function(self):
        code = """
def foo(a, b):
    return a + b
"""
        parser = ASTParser(code)
        tree = parser.parse()
        funcs = parser.get_functions()
        self.assertEqual(len(funcs), 1)
        self.assertEqual(funcs[0]['name'], 'foo')
        
    def test_parse_class(self):
        code = """
class MyClass:
    def __init__(self):
        pass
"""
        parser = ASTParser(code)
        tree = parser.parse()
        classes = parser.get_classes()
        self.assertEqual(len(classes), 1)
        self.assertEqual(classes[0]['name'], 'MyClass')
        
    def test_get_imports(self):
        code = """
import os
from sys import argv
"""
        parser = ASTParser(code)
        tree = parser.parse()
        imports = parser.get_imports()
        self.assertGreaterEqual(len(imports), 2)


class TestSymbolTable(unittest.TestCase):
    
    def test_symbol_table_vars(self):
        code = """
x = 5
y = 10
z = x + y
"""
        parser = ASTParser(code)
        tree = parser.parse()
        sym_table = build_symbol_table(tree)
        
        all_syms = sym_table.get_all_symbols()
        var_names = [s.name for s in all_syms]
        self.assertIn('x', var_names)
        self.assertIn('y', var_names)
        
    def test_function_scope(self):
        code = """
def foo():
    local_var = 5
    return local_var
"""
        parser = ASTParser(code)
        tree = parser.parse()
        sym_table = build_symbol_table(tree)
        
        self.assertGreater(len(sym_table.scopes), 1)


if __name__ == '__main__':
    unittest.main()
