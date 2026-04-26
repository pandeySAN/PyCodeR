import ast


class LivenessAnalyzer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.live_vars = {}
        
    def analyze(self):
        changed = True
        iteration = 0
        max_iterations = 100
        
        for block in self.cfg.blocks:
            block.live_in = set()
            block.live_out = set()
            
        while changed and iteration < max_iterations:
            changed = False
            iteration += 1
            
            for block in reversed(self.cfg.blocks):
                old_in = block.live_in.copy()
                old_out = block.live_out.copy()
                
                block.live_out = set()
                for succ in block.successors:
                    block.live_out.update(succ.live_in)
                    
                uses, defs = self.get_use_def(block)
                block.live_in = uses.union(block.live_out - defs)
                
                if block.live_in != old_in or block.live_out != old_out:
                    changed = True
                    
        return self.build_result()
        
    def get_use_def(self, block):
        uses = set()
        defs = set()
        
        for stmt in block.statements:
            stmt_uses = self.get_uses_from_stmt(stmt)
            stmt_defs = self.get_defs_from_stmt(stmt)
            
            uses.update(stmt_uses - defs)
            defs.update(stmt_defs)
            
        return uses, defs
        
    def get_uses_from_stmt(self, stmt):
        uses = set()
        for node in ast.walk(stmt):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                uses.add(node.id)
        return uses
        
    def get_defs_from_stmt(self, stmt):
        defs = set()
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    defs.add(target.id)
        elif isinstance(stmt, ast.AugAssign):
            if isinstance(stmt.target, ast.Name):
                defs.add(stmt.target.id)
        elif isinstance(stmt, (ast.For, ast.While)):
            if hasattr(stmt, 'target') and isinstance(stmt.target, ast.Name):
                defs.add(stmt.target.id)
        return defs
        
    def build_result(self):
        result = {}
        for block in self.cfg.blocks:
            result[block.name] = {
                'live_in': block.live_in,
                'live_out': block.live_out
            }
        return result
        
    def is_variable_live(self, var_name, block):
        return var_name in block.live_out
        
    def get_dead_assignments(self):
        dead = []
        for block in self.cfg.blocks:
            defs = self.get_defs_from_block(block)
            for var in defs:
                if var not in block.live_out:
                    dead.append({
                        'var': var,
                        'block': block.name
                    })
        return dead
        
    def get_defs_from_block(self, block):
        defs = set()
        for stmt in block.statements:
            defs.update(self.get_defs_from_stmt(stmt))
        return defs


def analyze_liveness(cfg):
    analyzer = LivenessAnalyzer(cfg)
    return analyzer.analyze()
