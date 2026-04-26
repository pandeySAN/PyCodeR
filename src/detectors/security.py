import ast
import re


class SecurityScanner:
    def __init__(self, tree, source_code=None):
        self.tree = tree
        self.source_code = source_code
        self.vulnerabilities = []
        
    def scan(self):
        self.check_sql_injection()
        self.check_hardcoded_secrets()
        self.check_dangerous_functions()
        self.check_command_injection()
        
        return self.vulnerabilities
        
    def check_sql_injection(self):
        visitor = SQLInjectionVisitor()
        visitor.visit(self.tree)
        
        for vuln in visitor.sql_injections:
            self.vulnerabilities.append({
                'type': 'sql_injection',
                'lineno': vuln['lineno'],
                'message': 'Potential SQL injection - using string concatenation in query',
                'severity': 'critical'
            })
            
    def check_hardcoded_secrets(self):
        if not self.source_code:
            return
            
        patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'hardcoded_password'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'hardcoded_api_key'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'hardcoded_secret'),
            (r'token\s*=\s*["\'][^"\']+["\']', 'hardcoded_token'),
        ]
        
        lines = self.source_code.split('\n')
        for i, line in enumerate(lines):
            for pattern, vuln_type in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.vulnerabilities.append({
                        'type': vuln_type,
                        'lineno': i + 1,
                        'message': f'Hardcoded secret detected',
                        'severity': 'high'
                    })
                    
    def check_dangerous_functions(self):
        visitor = DangerousFunctionVisitor()
        visitor.visit(self.tree)
        
        for vuln in visitor.dangerous_calls:
            self.vulnerabilities.append(vuln)
            
    def check_command_injection(self):
        visitor = CommandInjectionVisitor()
        visitor.visit(self.tree)
        
        for vuln in visitor.command_injections:
            self.vulnerabilities.append({
                'type': 'command_injection',
                'lineno': vuln['lineno'],
                'message': 'Potential command injection - using untrusted input in system command',
                'severity': 'critical'
            })


class SQLInjectionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.sql_injections = []
        
    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            method = node.func.attr
            
            if method in ['execute', 'executemany']:
                if node.args:
                    query_arg = node.args[0]
                    
                    if self.is_string_concat(query_arg):
                        self.sql_injections.append({
                            'lineno': node.lineno
                        })
                        
        self.generic_visit(node)
        
    def is_string_concat(self, node):
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, (ast.Add, ast.Mod)):
                return True
        if isinstance(node, ast.JoinedStr):
            return True
        return False


class DangerousFunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.dangerous_calls = []
        self.dangerous_funcs = {
            'eval': 'critical',
            'exec': 'critical',
            'compile': 'high',
            '__import__': 'high'
        }
        
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            
            if func_name in self.dangerous_funcs:
                self.dangerous_calls.append({
                    'type': 'dangerous_function',
                    'lineno': node.lineno,
                    'message': f"Use of dangerous function '{func_name}'",
                    'severity': self.dangerous_funcs[func_name]
                })
                
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr == 'loads' and self.is_pickle_module(node.func.value):
                self.dangerous_calls.append({
                    'type': 'pickle_loads',
                    'lineno': node.lineno,
                    'message': 'Using pickle.loads() can execute arbitrary code',
                    'severity': 'high'
                })
                
        self.generic_visit(node)
        
    def is_pickle_module(self, node):
        if isinstance(node, ast.Name):
            return node.id == 'pickle'
        return False


class CommandInjectionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.command_injections = []
        
    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            obj = node.func.value
            method = node.func.attr
            
            if isinstance(obj, ast.Name) and obj.id == 'os':
                if method in ['system', 'popen']:
                    if node.args and self.has_user_input(node.args[0]):
                        self.command_injections.append({
                            'lineno': node.lineno
                        })
                        
        elif isinstance(node.func, ast.Name):
            if node.func.id in ['system', 'popen']:
                if node.args and self.has_user_input(node.args[0]):
                    self.command_injections.append({
                        'lineno': node.lineno
                    })
                    
        self.generic_visit(node)
        
    def has_user_input(self, node):
        if isinstance(node, (ast.BinOp, ast.JoinedStr)):
            return True
        return False


def scan_security(tree, source_code=None):
    scanner = SecurityScanner(tree, source_code)
    return scanner.scan()
