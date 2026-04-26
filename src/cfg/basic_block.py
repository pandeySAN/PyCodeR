class BasicBlock:
    _id_counter = 0
    
    def __init__(self, name=None):
        self.id = BasicBlock._id_counter
        BasicBlock._id_counter += 1
        self.name = name if name else f"BB{self.id}"
        self.statements = []
        self.predecessors = []
        self.successors = []
        self.gen = set()
        self.kill = set()
        self.live_in = set()
        self.live_out = set()
        self.reach_in = set()
        self.reach_out = set()
        
    def add_statement(self, stmt):
        self.statements.append(stmt)
        
    def add_successor(self, block):
        if block not in self.successors:
            self.successors.append(block)
        if self not in block.predecessors:
            block.predecessors.append(self)
            
    def add_predecessor(self, block):
        if block not in self.predecessors:
            self.predecessors.append(block)
        if self not in block.successors:
            block.successors.append(self)
            
    def __repr__(self):
        return f"BasicBlock({self.name}, stmts={len(self.statements)})"
        
    def __str__(self):
        return self.name
        
    def get_defs(self):
        defs = set()
        for stmt in self.statements:
            if hasattr(stmt, 'targets'):
                for target in stmt.targets:
                    if hasattr(target, 'id'):
                        defs.add(target.id)
        return defs
        
    def get_uses(self):
        uses = set()
        import ast
        for stmt in self.statements:
            for node in ast.walk(stmt):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    uses.add(node.id)
        return uses
        
    def is_empty(self):
        return len(self.statements) == 0
        
    def has_terminator(self):
        import ast
        if not self.statements:
            return False
        last = self.statements[-1]
        return isinstance(last, (ast.Return, ast.Break, ast.Continue, ast.Raise))


class ControlFlowGraph:
    def __init__(self, name):
        self.name = name
        self.entry = BasicBlock(f"{name}_entry")
        self.exit = BasicBlock(f"{name}_exit")
        self.blocks = [self.entry, self.exit]
        self.current_block = self.entry
        
    def new_block(self, name=None):
        block = BasicBlock(name)
        self.blocks.append(block)
        return block
        
    def add_edge(self, from_block, to_block):
        from_block.add_successor(to_block)
        
    def get_blocks(self):
        return self.blocks
        
    def get_all_paths(self, start=None, end=None):
        if not start:
            start = self.entry
        if not end:
            end = self.exit
            
        paths = []
        current_path = []
        visited = set()
        
        def dfs(block):
            if block in visited:
                return
            visited.add(block)
            current_path.append(block)
            
            if block == end:
                paths.append(list(current_path))
            else:
                for succ in block.successors:
                    dfs(succ)
                    
            current_path.pop()
            visited.remove(block)
            
        dfs(start)
        return paths
        
    def to_dot(self):
        lines = [f'digraph {self.name} {{']
        for block in self.blocks:
            label = f"{block.name}\\n"
            if block.statements:
                label += f"{len(block.statements)} stmts"
            lines.append(f'  {block.id} [label="{label}"];')
            
        for block in self.blocks:
            for succ in block.successors:
                lines.append(f'  {block.id} -> {succ.id};')
                
        lines.append('}')
        return '\n'.join(lines)
