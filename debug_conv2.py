import sys
sys.path.insert(0, '.')
from src.parser.ast_parser import ASTParser
from src.cfg.cfg_builder import build_cfg
from src.analysis.reaching_defs import ReachingDefinitions

code = open('tests/fixtures/regress_global_nonlocal.py').read()
tree = ASTParser(code).parse()
cfg = build_cfg(tree)

rd = ReachingDefinitions(cfg, tree)
rd.collect_definitions()

da = rd.compute_definite_assignment()
print(f"outer_exit definite_in: {da['in'][next(b for b in cfg.blocks if b.name == 'outer_exit')]}")
for block in cfg.blocks:
    if block.name == 'outer_exit':
        print(f"outer_exit predecessors: {[p.name for p in block.predecessors]}")
        for p in block.predecessors:
            print(f"  pred {p.name!r}: definite_out = {da['out'][p]}")
