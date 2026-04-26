import ast


class ComplexityAnalyzer:
    def __init__(self, tree):
        self.tree = tree
        self.issues = []
        self.max_complexity = 10
        self.max_nesting = 4
        
    def analyze(self):
        self.check_cyclomatic_complexity()
        self.check_nesting_depth()
        self.check_function_length()
        
        return self.issues
        
    def check_cyclomatic_complexity(self):
        visitor = CyclomaticComplexityVisitor(self.max_complexity)
        visitor.visit(self.tree)
        
        for issue in visitor.complex_functions:
            self.issues.append({
                'type': 'high_complexity',
                'lineno': issue['lineno'],
                'message': f"Function '{issue['name']}' has complexity {issue['complexity']} (max {self.max_complexity})",
                'severity': 'warning'
            })
            
    def check_nesting_depth(self):
        visitor = NestingDepthVisitor(self.max_nesting)
        visitor.visit(self.tree)
        
        for issue in visitor.deep_nesting:
            self.issues.append({
                'type': 'deep_nesting',
                'lineno': issue['lineno'],
                'message': f"Nesting depth {issue['depth']} exceeds maximum {self.max_nesting}",
                'severity': 'warning'
            })
            
    def check_function_length(self):
        visitor = FunctionLengthVisitor(50)
        visitor.visit(self.tree)
        
        for issue in visitor.long_functions:
            self.issues.append({
                'type': 'long_function',
                'lineno': issue['lineno'],
                'message': f"Function '{issue['name']}' has {issue['lines']} lines (consider splitting)",
                'severity': 'info'
            })


class CyclomaticComplexityVisitor(ast.NodeVisitor):
    def __init__(self, threshold):
        self.threshold = threshold
        self.complex_functions = []
        self.current_function = None
        self.current_complexity = 0
        
    def visit_FunctionDef(self, node):
        old_func = self.current_function
        old_complexity = self.current_complexity
        
        self.current_function = node.name
        self.current_complexity = 1
        
        self.generic_visit(node)
        
        if self.current_complexity > self.threshold:
            self.complex_functions.append({
                'name': node.name,
                'complexity': self.current_complexity,
                'lineno': node.lineno
            })
            
        self.current_function = old_func
        self.current_complexity = old_complexity
        
    def visit_If(self, node):
        if self.current_function:
            self.current_complexity += 1
        self.generic_visit(node)
        
    def visit_While(self, node):
        if self.current_function:
            self.current_complexity += 1
        self.generic_visit(node)
        
    def visit_For(self, node):
        if self.current_function:
            self.current_complexity += 1
        self.generic_visit(node)
        
    def visit_ExceptHandler(self, node):
        if self.current_function:
            self.current_complexity += 1
        self.generic_visit(node)
        
    def visit_BoolOp(self, node):
        if self.current_function and isinstance(node.op, (ast.And, ast.Or)):
            self.current_complexity += len(node.values) - 1
        self.generic_visit(node)


class NestingDepthVisitor(ast.NodeVisitor):
    def __init__(self, max_depth):
        self.max_depth = max_depth
        self.current_depth = 0
        self.deep_nesting = []
        
    def visit_If(self, node):
        self.current_depth += 1
        if self.current_depth > self.max_depth:
            self.deep_nesting.append({
                'depth': self.current_depth,
                'lineno': node.lineno
            })
        self.generic_visit(node)
        self.current_depth -= 1
        
    def visit_While(self, node):
        self.current_depth += 1
        if self.current_depth > self.max_depth:
            self.deep_nesting.append({
                'depth': self.current_depth,
                'lineno': node.lineno
            })
        self.generic_visit(node)
        self.current_depth -= 1
        
    def visit_For(self, node):
        self.current_depth += 1
        if self.current_depth > self.max_depth:
            self.deep_nesting.append({
                'depth': self.current_depth,
                'lineno': node.lineno
            })
        self.generic_visit(node)
        self.current_depth -= 1
        
    def visit_Try(self, node):
        self.current_depth += 1
        if self.current_depth > self.max_depth:
            self.deep_nesting.append({
                'depth': self.current_depth,
                'lineno': node.lineno
            })
        self.generic_visit(node)
        self.current_depth -= 1


class FunctionLengthVisitor(ast.NodeVisitor):
    def __init__(self, max_lines):
        self.max_lines = max_lines
        self.long_functions = []
        
    def visit_FunctionDef(self, node):
        if hasattr(node, 'end_lineno') and node.end_lineno:
            lines = node.end_lineno - node.lineno + 1
            if lines > self.max_lines:
                self.long_functions.append({
                    'name': node.name,
                    'lines': lines,
                    'lineno': node.lineno
                })
        self.generic_visit(node)


def analyze_complexity(tree):
    analyzer = ComplexityAnalyzer(tree)
    return analyzer.analyze()
