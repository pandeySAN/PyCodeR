import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parser.ast_parser import ASTParser
from src.cfg.cfg_builder import build_cfg
from src.analysis.dataflow import analyze_dataflow
from src.analysis.liveness import analyze_liveness
from src.analysis.reaching_defs import ReachingDefinitions


class TestDataFlow(unittest.TestCase):
    
    def test_basic_dataflow(self):
        code = """
x = 5
y = x + 10
z = y * 2
"""
        parser = ASTParser(code)
        tree = parser.parse()
        cfg = build_cfg(tree)
        
        analysis = analyze_dataflow(cfg)
        self.assertIsNotNone(analysis)
        
    def test_liveness_analysis(self):
        code = """
def foo():
    x = 5
    y = 10
    return x
"""
        parser = ASTParser(code)
        tree = parser.parse()
        cfg = build_cfg(tree)
        
        result = analyze_liveness(cfg)
        self.assertIsNotNone(result)
        
    def test_reaching_definitions(self):
        code = """
x = 5
if condition:
    x = 10
y = x
"""
        parser = ASTParser(code)
        tree = parser.parse()
        cfg = build_cfg(tree)
        
        rd = ReachingDefinitions(cfg)
        result = rd.analyze()
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
