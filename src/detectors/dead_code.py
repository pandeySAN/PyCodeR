import ast


class DeadCodeDetector:
    def __init__(self, cfg, tree=None):
        self.cfg = cfg
        self.tree = tree
        self.dead_blocks = []
        self.unreachable_code = []
        
    def detect(self):
        self.find_unreachable_blocks()
        if self.tree:
            self.find_code_after_terminator()
        return self.unreachable_code
        
    def find_unreachable_blocks(self):
        reachable = set()
        worklist = [self.cfg.entry]
        
        while worklist:
            block = worklist.pop()
            if block in reachable:
                continue
            reachable.add(block)
            
            for succ in block.successors:
                if succ not in reachable:
                    worklist.append(succ)
                    
        for block in self.cfg.blocks:
            if block not in reachable and block != self.cfg.exit:
                self.dead_blocks.append(block)
                self.unreachable_code.append({
                    'type': 'unreachable_block',
                    'block': block.name,
                    'message': f'Block {block.name} is unreachable',
                    'severity': 'warning'
                })
                
    def find_code_after_terminator(self):
        visitor = DeadCodeVisitor()
        visitor.visit(self.tree)
        
        for issue in visitor.dead_code:
            self.unreachable_code.append({
                'type': 'code_after_terminator',
                'lineno': issue['lineno'],
                'message': issue['message'],
                'severity': 'warning'
            })
            
    def get_dead_blocks(self):
        return self.dead_blocks


class DeadCodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.dead_code = []
        self.in_function = False
        
    def visit_FunctionDef(self, node):
        old_in_func = self.in_function
        self.in_function = True
        
        self.check_function_body(node.body)
        
        self.in_function = old_in_func
        
    def check_function_body(self, body):
        found_terminator = False
        terminator_line = None
        
        for i, stmt in enumerate(body):
            if found_terminator:
                self.dead_code.append({
                    'lineno': stmt.lineno,
                    'message': f'Code after return/raise at line {terminator_line} is unreachable'
                })
                
            if isinstance(stmt, (ast.Return, ast.Raise)):
                found_terminator = True
                terminator_line = stmt.lineno
                
            if isinstance(stmt, ast.If):
                self.check_function_body(stmt.body)
                self.check_function_body(stmt.orelse)
                
            elif isinstance(stmt, (ast.While, ast.For)):
                self.check_function_body(stmt.body)
                
            elif isinstance(stmt, ast.Try):
                self.check_function_body(stmt.body)
                for handler in stmt.handlers:
                    self.check_function_body(handler.body)
                self.check_function_body(stmt.orelse)
                self.check_function_body(stmt.finalbody)


class InfiniteLoopDetector:
    def __init__(self, tree):
        self.tree = tree
        self.infinite_loops = []
        
    def detect(self):
        visitor = InfiniteLoopVisitor()
        visitor.visit(self.tree)
        self.infinite_loops = visitor.infinite_loops
        return self.infinite_loops


class InfiniteLoopVisitor(ast.NodeVisitor):
    def __init__(self):
        self.infinite_loops = []
        
    def visit_While(self, node):
        if self.is_constant_true(node.test):
            has_break = self.has_break_statement(node.body)
            if not has_break:
                self.infinite_loops.append({
                    'type': 'infinite_loop',
                    'lineno': node.lineno,
                    'message': 'Potential infinite loop without break',
                    'severity': 'error'
                })
        self.generic_visit(node)
        
    def is_constant_true(self, node):
        if isinstance(node, ast.Constant):
            return node.value is True
        if isinstance(node, ast.NameConstant):
            return node.value is True
        return False
        
    def has_break_statement(self, body):
        for stmt in body:
            if isinstance(stmt, ast.Break):
                return True
            if isinstance(stmt, (ast.If, ast.While, ast.For)):
                if hasattr(stmt, 'body') and self.has_break_statement(stmt.body):
                    return True
        return False


def detect_dead_code(cfg, tree=None):
    detector = DeadCodeDetector(cfg, tree)
    return detector.detect()
