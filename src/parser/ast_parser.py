import ast
import sys


class ASTParser:
    def __init__(self, source_code):
        self.source = source_code
        self.tree = None
        self.errors = []
        
    def parse(self):
        try:
            self.tree = ast.parse(self.source)
            return self.tree
        except SyntaxError as e:
            self.errors.append({
                'type': 'SyntaxError',
                'line': e.lineno,
                'message': str(e)
            })
            return None
            
    def get_functions(self):
        funcs = []
        if not self.tree:
            return funcs
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                funcs.append({
                    'name': node.name,
                    'lineno': node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'node': node
                })
        return funcs
        
    def get_classes(self):
        classes = []
        if not self.tree:
            return classes
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'lineno': node.lineno,
                    'node': node
                })
        return classes
        
    def get_imports(self):
        imports = []
        if not self.tree:
            return imports
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'name': alias.name,
                        'asname': alias.asname,
                        'lineno': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ''
                for alias in node.names:
                    imports.append({
                        'name': f"{module}.{alias.name}" if module else alias.name,
                        'asname': alias.asname,
                        'lineno': node.lineno,
                        'from_module': module
                    })
        return imports
        
    def get_assignments(self):
        assigns = []
        if not self.tree:
            return assigns
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assigns.append({
                            'var': target.id,
                            'lineno': node.lineno,
                            'node': node
                        })
        return assigns
        
    def get_all_names(self):
        names = set()
        if not self.tree:
            return names
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Name):
                names.add(node.id)
        return names
        
    def visit_node(self, node, visitor_func):
        visitor_func(node)
        for child in ast.iter_child_nodes(node):
            self.visit_node(child, visitor_func)


class CodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.variables = []
        self.function_calls = []
        self.returns = []
        
    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Load)):
            self.variables.append({
                'name': node.id,
                'lineno': node.lineno,
                'type': 'store' if isinstance(node.ctx, ast.Store) else 'load'
            })
        self.generic_visit(node)
        
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.function_calls.append({
                'name': node.func.id,
                'lineno': node.lineno
            })
        self.generic_visit(node)
        
    def visit_Return(self, node):
        self.returns.append({
            'lineno': node.lineno,
            'has_value': node.value is not None
        })
        self.generic_visit(node)


def parse_file(filepath):
    try:
        with open(filepath, 'r') as f:
            source = f.read()
        parser = ASTParser(source)
        tree = parser.parse()
        return parser, tree
    except IOError as e:
        print(f"Error reading file: {e}")
        return None, None
