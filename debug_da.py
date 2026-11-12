import sys
sys.path.insert(0, '.')
from src.parser.ast_parser import ASTParser
from src.cfg.cfg_builder import build_cfg
from src.analysis.reaching_defs import ReachingDefinitions

code = open('tests/fixtures/regress_global_nonlocal.py').read()
tree = ASTParser(code).parse()
cfg = build_cfg(tree)

rd = ReachingDefinitions(cfg, tree)
rd.analyze()

# Print definite assignment
da = rd.compute_definite_assignment()
for block in cfg.blocks:
    if block.statements:
        print(f"Block {block.name!r} (fn={block.function}):")
        print(f"  statements: {[type(s).__name__ for s in block.statements]}")
        print(f"  definite_in: {da['in'][block]}")
        print(f"  definite_out: {da['out'][block]}")
        print()

# Print possibly undefined
pu = rd.find_possibly_undefined_uses()
for u in pu:
    print(f"POSSIBLY UNDEFINED: {u['var']} at line {u['lineno']} in block {u['block']}")
