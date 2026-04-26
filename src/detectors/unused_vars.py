import ast


class UnusedVarDetector:
    def __init__(self, symbol_table, cfg=None):
        self.symbol_table = symbol_table
        self.cfg = cfg
        self.unused = []
        
    def detect(self):
        self.unused = []
        
        for scope in self.symbol_table.scopes:
            for symbol in scope.symbols.values():
                if self.is_unused(symbol):
                    # Create appropriate message based on symbol type
                    if symbol.type == 'import':
                        message = f"Imported module '{symbol.name}' is never used"
                    elif symbol.type == 'function':
                        message = f"Function '{symbol.name}' is defined but never called"
                    elif symbol.type == 'variable':
                        message = f"Variable '{symbol.name}' is assigned but never used"
                    elif symbol.type == 'class':
                        message = f"Class '{symbol.name}' is defined but never used"
                    else:
                        message = f"'{symbol.name}' is unused"
                    
                    self.unused.append({
                        'name': symbol.name,
                        'type': f'unused_{symbol.type}',
                        'lineno': symbol.lineno,
                        'scope': scope.name,
                        'message': message,
                        'severity': 'warning'
                    })
                    
        return self.unused
        
    def is_unused(self, symbol):
        if symbol.type == 'import':
            return len(symbol.references) == 0
            
        if symbol.type == 'parameter':
            return False
            
        if symbol.type == 'function':
            return len(symbol.references) == 0
            
        if symbol.type == 'variable':
            return len(symbol.references) == 0
            
        if symbol.type == 'class':
            return len(symbol.references) == 0
            
        return False
        
    def get_unused_imports(self):
        unused_imports = []
        for item in self.unused:
            if item['type'] == 'unused_import':
                unused_imports.append(item)
        return unused_imports
        
    def get_unused_variables(self):
        unused_vars = []
        for item in self.unused:
            if item['type'] == 'unused_variable':
                unused_vars.append(item)
        return unused_vars
        
    def get_unused_functions(self):
        unused_funcs = []
        for item in self.unused:
            if item['type'] == 'unused_function':
                unused_funcs.append(item)
        return unused_funcs


class UnusedCodeDetector:
    def __init__(self, tree):
        self.tree = tree
        self.issues = []
        
    def detect(self):
        self.issues = []
        visitor = UnusedCodeVisitor()
        visitor.visit(self.tree)
        
        for issue in visitor.unused_code:
            self.issues.append({
                'type': 'unused_code',
                'message': issue['message'],
                'lineno': issue['lineno'],
                'severity': 'info'
            })
            
        return self.issues


class UnusedCodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.unused_code = []
        self.defined_vars = set()
        self.used_vars = set()
        
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.defined_vars.add(target.id)
        self.generic_visit(node)
        
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_vars.add(node.id)
        self.generic_visit(node)
        
    def get_unused(self):
        return self.defined_vars - self.used_vars


def detect_unused_vars(symbol_table, cfg=None):
    detector = UnusedVarDetector(symbol_table, cfg)
    return detector.detect()
