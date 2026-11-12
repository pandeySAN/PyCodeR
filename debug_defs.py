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

print(f"Total definitions: {len(rd.definitions)}")
for def_id, def_info in rd.definitions.items():
    print(f"  {def_info['var']} in block {def_info['block'].name!r} (stmt type: {type(def_info['stmt']).__name__})")

# Check _block_def_vars
for block in cfg.blocks:
    vars = rd._block_def_vars(block)
    if vars:
        print(f"Block {block.name!r}: def_vars = {vars}")
