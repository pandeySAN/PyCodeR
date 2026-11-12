import sys
sys.path.insert(0, '.')
from src.parser.ast_parser import ASTParser
from src.cfg.cfg_builder import build_cfg
from src.analysis.reaching_defs import ReachingDefinitions

code = open('tests/fixtures/regress_global_nonlocal.py').read()
tree = ASTParser(code).parse()
cfg = build_cfg(tree)

for block in cfg.blocks:
    if block.statements or block.name in ('outer_entry', 'increment_exit'):
        print(f"Block {block.name!r} (fn={block.function}):")
        print(f"  predecessors: {[p.name for p in block.predecessors]}")
        print(f"  successors: {[s.name for s in block.successors]}")
        print(f"  statements: {[type(s).__name__ for s in block.statements]}")
        print()
