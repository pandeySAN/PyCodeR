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

gen = {}
for block in cfg.blocks:
    gen[block] = rd._block_def_vars(block)

definite_in = {b: set() for b in cfg.blocks}
definite_out = {b: set() for b in cfg.blocks}

changed = True
iterations = 0
while changed and iterations < 100:
    changed = False
    iterations += 1
    for block in cfg.blocks:
        if block.predecessors:
            new_in = set(definite_out[block.predecessors[0]])
            for pred in block.predecessors[1:]:
                new_in &= definite_out[pred]
        else:
            new_in = set()
        old_out = definite_out[block].copy()
        definite_in[block] = new_in
        definite_out[block] = (new_in - gen[block]) | gen[block]
        if definite_out[block] != old_out:
            changed = True

print(f"Iterations: {iterations}")
for block in cfg.blocks:
    if block.name == 'outer_exit':
        print(f"outer_exit definite_in: {definite_in[block]}")
        print(f"outer_exit predecessors: {[p.name for p in block.predecessors]}")
        for p in block.predecessors:
            print(f"  pred {p.name!r}: definite_out = {definite_out[p]}")
