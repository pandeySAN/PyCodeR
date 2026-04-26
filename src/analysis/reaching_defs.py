import ast


class ReachingDefinitions:
    def __init__(self, cfg):
        self.cfg = cfg
        self.definitions = {}
        self.def_id = 0
        
    def analyze(self):
        self.collect_definitions()
        
        for block in self.cfg.blocks:
            block.reach_in = set()
            block.reach_out = set()
            
        changed = True
        iterations = 0
        
        while changed and iterations < 100:
            changed = False
            iterations += 1
            
            for block in self.cfg.blocks:
                old_out = block.reach_out.copy()
                
                block.reach_in = set()
                for pred in block.predecessors:
                    block.reach_in.update(pred.reach_out)
                    
                gen = self.get_gen(block)
                kill = self.get_kill(block)
                
                block.reach_out = gen.union(block.reach_in - kill)
                
                if block.reach_out != old_out:
                    changed = True
                    
        return self.build_result()
        
    def collect_definitions(self):
        for block in self.cfg.blocks:
            for stmt in block.statements:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            def_info = {
                                'id': self.def_id,
                                'var': target.id,
                                'stmt': stmt,
                                'block': block
                            }
                            self.definitions[self.def_id] = def_info
                            self.def_id += 1
                            
    def get_gen(self, block):
        gen = set()
        for def_id, def_info in self.definitions.items():
            if def_info['block'] == block:
                gen.add(def_id)
        return gen
        
    def get_kill(self, block):
        kill = set()
        block_defs = {}
        
        for def_id, def_info in self.definitions.items():
            if def_info['block'] == block:
                var = def_info['var']
                if var not in block_defs:
                    block_defs[var] = []
                block_defs[var].append(def_id)
                
        for var, def_ids in block_defs.items():
            for def_id, def_info in self.definitions.items():
                if def_info['var'] == var and def_id not in def_ids:
                    kill.add(def_id)
                    
        return kill
        
    def build_result(self):
        result = {}
        for block in self.cfg.blocks:
            result[block.name] = {
                'reach_in': [self.definitions[d] for d in block.reach_in],
                'reach_out': [self.definitions[d] for d in block.reach_out]
            }
        return result
        
    def find_undefined_uses(self):
        """Find variables that may be used before definition, excluding built-ins and parameters"""
        undefined = []
        
        # Python built-ins to exclude
        builtins = {
            'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple',
            'open', 'input', 'sum', 'min', 'max', 'abs', 'all', 'any', 'enumerate', 'zip',
            'map', 'filter', 'sorted', 'reversed', 'isinstance', 'type', 'hasattr', 'getattr',
            'setattr', 'dir', 'help', 'id', 'hex', 'oct', 'bin', 'chr', 'ord', 'eval', 'exec',
            'compile', 'globals', 'locals', '__name__', '__file__', '__doc__', 'Exception',
            'True', 'False', 'None', 'NotImplemented', 'Ellipsis', 'object', 'super',
        }
        
        # Collect function parameters and imports from symbol table analysis
        defined_names = set()
        for block in self.cfg.blocks:
            for stmt in block.statements:
                # Function parameters
                if isinstance(stmt, ast.FunctionDef):
                    for arg in stmt.args.args:
                        defined_names.add(arg.arg)
                # Imports
                elif isinstance(stmt, ast.Import):
                    for alias in stmt.names:
                        name = alias.asname if alias.asname else alias.name.split('.')[0]
                        defined_names.add(name)
                elif isinstance(stmt, ast.ImportFrom):
                    for alias in stmt.names:
                        name = alias.asname if alias.asname else alias.name
                        defined_names.add(name)
        
        for block in self.cfg.blocks:
            for stmt in block.statements:
                uses = self.get_uses(stmt)
                
                for var in uses:
                    # Skip built-ins and known defined names
                    if var in builtins or var in defined_names:
                        continue
                        
                    reaching = [d for d in block.reach_in 
                               if self.definitions[d]['var'] == var]
                    if not reaching:
                        undefined.append({
                            'var': var,
                            'stmt': stmt,
                            'block': block.name,
                            'lineno': getattr(stmt, 'lineno', -1)
                        })
                        
        return undefined
        
    def get_uses(self, stmt):
        uses = set()
        for node in ast.walk(stmt):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                uses.add(node.id)
        return uses


def analyze_reaching_defs(cfg):
    analyzer = ReachingDefinitions(cfg)
    return analyzer.analyze()
