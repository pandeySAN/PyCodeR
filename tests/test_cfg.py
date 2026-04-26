import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parser.ast_parser import ASTParser
from src.cfg.cfg_builder import build_cfg


class TestCFG(unittest.TestCase):
    
    def test_simple_cfg(self):
        code = """
x = 5
y = 10
"""
        parser = ASTParser(code)
        tree = parser.parse()
        cfg = build_cfg(tree)
        
        self.assertIsNotNone(cfg)
        self.assertGreater(len(cfg.blocks), 0)
        
    def test_if_statement_cfg(self):
        code = """
if x > 5:
    y = 10
else:
    y = 20
"""
        parser = ASTParser(code)
        tree = parser.parse()
        cfg = build_cfg(tree)
        
        self.assertGreater(len(cfg.blocks), 2)
        
    def test_while_loop_cfg(self):
        code = """
while x < 10:
    x = x + 1
"""
        parser = ASTParser(code)
        tree = parser.parse()
        cfg = build_cfg(tree)
        
        self.assertGreater(len(cfg.blocks), 2)
        
    def test_for_loop_cfg(self):
        code = """
for i in range(10):
    print(i)
"""
        parser = ASTParser(code)
        tree = parser.parse()
        cfg = build_cfg(tree)
        
        self.assertGreater(len(cfg.blocks), 2)


if __name__ == '__main__':
    unittest.main()
