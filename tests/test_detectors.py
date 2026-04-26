import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parser.ast_parser import ASTParser
from src.parser.symbol_table import build_symbol_table
from src.cfg.cfg_builder import build_cfg
from src.detectors.unused_vars import detect_unused_vars
from src.detectors.dead_code import detect_dead_code
from src.detectors.type_checker import check_types
from src.detectors.security import scan_security


class TestUnusedVarDetector(unittest.TestCase):
    
    def test_detect_unused_variable(self):
        code = """
x = 5
y = 10
z = x
"""
        parser = ASTParser(code)
        tree = parser.parse()
        sym_table = build_symbol_table(tree)
        
        unused = detect_unused_vars(sym_table)
        unused_names = [u['name'] for u in unused]
        self.assertIn('y', unused_names)
        
    def test_detect_unused_import(self):
        code = """
import os
import sys
print(sys.version)
"""
        parser = ASTParser(code)
        tree = parser.parse()
        sym_table = build_symbol_table(tree)
        
        unused = detect_unused_vars(sym_table)
        unused_imports = [u for u in unused if u['type'] == 'import']
        self.assertGreater(len(unused_imports), 0)


class TestDeadCodeDetector(unittest.TestCase):
    
    def test_detect_code_after_return(self):
        code = """
def foo():
    return 5
    x = 10
"""
        parser = ASTParser(code)
        tree = parser.parse()
        cfg = build_cfg(tree)
        
        dead = detect_dead_code(cfg, tree)
        self.assertGreater(len(dead), 0)
        
    def test_detect_infinite_loop(self):
        code = """
while True:
    x = 5
"""
        parser = ASTParser(code)
        tree = parser.parse()
        cfg = build_cfg(tree)
        
        from src.detectors.dead_code import InfiniteLoopDetector
        detector = InfiniteLoopDetector(tree)
        loops = detector.detect()
        self.assertGreater(len(loops), 0)


class TestTypeChecker(unittest.TestCase):
    
    def test_none_type_error(self):
        code = """
x = None
y = x.upper()
"""
        parser = ASTParser(code)
        tree = parser.parse()
        
        issues = check_types(tree)
        self.assertGreater(len(issues), 0)


class TestSecurityScanner(unittest.TestCase):
    
    def test_sql_injection(self):
        code = """
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)
"""
        parser = ASTParser(code)
        tree = parser.parse()
        
        vulns = scan_security(tree, code)
        sql_issues = [v for v in vulns if v['type'] == 'sql_injection']
        self.assertGreater(len(sql_issues), 0)
        
    def test_dangerous_function(self):
        code = """
eval(user_input)
"""
        parser = ASTParser(code)
        tree = parser.parse()
        
        vulns = scan_security(tree, code)
        dangerous = [v for v in vulns if v['type'] == 'dangerous_function']
        self.assertGreater(len(dangerous), 0)


if __name__ == '__main__':
    unittest.main()
