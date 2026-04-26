import ast


class DataFlowAnalysis:
    def __init__(self, cfg):
        self.cfg = cfg
        self.variables = set()
        self.collect_variables()
        
    def collect_variables(self):
        for block in self.cfg.blocks:
            for stmt in block.statements:
                for node in ast.walk(stmt):
                    if isinstance(node, ast.Name):
                        self.variables.add(node.id)
                        
    def get_gen_kill(self, block):
        gen = set()
        kill = set()
        
        for stmt in block.statements:
            uses = self.get_uses(stmt)
            defs = self.get_defs(stmt)
            
            gen.update(uses - kill)
            kill.update(defs)
            
        return gen, kill
        
    def get_defs(self, stmt):
        defs = set()
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    defs.add(target.id)
        elif isinstance(stmt, ast.AugAssign):
            if isinstance(stmt.target, ast.Name):
                defs.add(stmt.target.id)
        elif isinstance(stmt, ast.For):
            if isinstance(stmt.target, ast.Name):
                defs.add(stmt.target.id)
        return defs
        
    def get_uses(self, stmt):
        uses = set()
        for node in ast.walk(stmt):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                uses.add(node.id)
        return uses
        
    def worklist_algorithm(self, direction='forward'):
        worklist = list(self.cfg.blocks)
        
        for block in self.cfg.blocks:
            if direction == 'forward':
                block.reach_in = set()
                block.reach_out = set()
            else:
                block.live_in = set()
                block.live_out = set()
                
        while worklist:
            block = worklist.pop(0)
            
            if direction == 'forward':
                old_out = block.reach_out.copy()
                
                block.reach_in = set()
                for pred in block.predecessors:
                    block.reach_in.update(pred.reach_out)
                    
                gen, kill = self.get_gen_kill(block)
                block.reach_out = gen.union(block.reach_in - kill)
                
                if block.reach_out != old_out:
                    for succ in block.successors:
                        if succ not in worklist:
                            worklist.append(succ)
            else:
                old_in = block.live_in.copy()
                
                block.live_out = set()
                for succ in block.successors:
                    block.live_out.update(succ.live_in)
                    
                uses = set()
                defs = set()
                for stmt in block.statements:
                    uses.update(self.get_uses(stmt))
                    defs.update(self.get_defs(stmt))
                    
                block.live_in = uses.union(block.live_out - defs)
                
                if block.live_in != old_in:
                    for pred in block.predecessors:
                        if pred not in worklist:
                            worklist.append(pred)
                            
    def compute_reaching_definitions(self):
        self.worklist_algorithm(direction='forward')
        
    def compute_liveness(self):
        self.worklist_algorithm(direction='backward')
        
    def get_def_use_chains(self):
        chains = {}
        for block in self.cfg.blocks:
            for stmt in block.statements:
                defs = self.get_defs(stmt)
                for var in defs:
                    if var not in chains:
                        chains[var] = []
                    chains[var].append({
                        'def': stmt,
                        'block': block,
                        'uses': []
                    })
        return chains
        
    def find_uninitialized_vars(self):
        uninit = []
        for block in self.cfg.blocks:
            for stmt in block.statements:
                uses = self.get_uses(stmt)
                for var in uses:
                    if var not in block.reach_in:
                        uninit.append({
                            'var': var,
                            'stmt': stmt,
                            'block': block
                        })
        return uninit


def analyze_dataflow(cfg):
    analysis = DataFlowAnalysis(cfg)
    analysis.compute_reaching_definitions()
    analysis.compute_liveness()
    return analysis
