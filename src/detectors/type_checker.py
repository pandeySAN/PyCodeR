import ast


class TypeInference:
    def __init__(self, tree):
        self.tree = tree
        self.type_map = {}
        self.errors = []
        
    def infer(self):
        visitor = TypeVisitor(self.type_map)
        visitor.visit(self.tree)
        self.errors = visitor.type_errors
        return self.type_map, self.errors
        
    def get_type_errors(self):
        return self.errors


class TypeVisitor(ast.NodeVisitor):
    def __init__(self, type_map):
        self.type_map = type_map
        self.type_errors = []
        
    def visit_Assign(self, node):
        value_type = self.infer_type(node.value)
        
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.type_map[target.id] = value_type
                
        self.generic_visit(node)
        
    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            obj_name = self.get_name(node.func.value)
            method = node.func.attr
            
            if obj_name in self.type_map:
                obj_type = self.type_map[obj_name]
                
                if obj_type == 'NoneType' and method in ['upper', 'lower', 'strip']:
                    self.type_errors.append({
                        'type': 'none_type_error',
                        'lineno': node.lineno,
                        'message': f"Calling '{method}' on potentially None object '{obj_name}'",
                        'severity': 'error'
                    })
                    
        self.generic_visit(node)
        
    def infer_type(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                return 'str'
            elif isinstance(node.value, int):
                return 'int'
            elif isinstance(node.value, float):
                return 'float'
            elif isinstance(node.value, bool):
                return 'bool'
            elif node.value is None:
                return 'NoneType'
                
        elif isinstance(node, ast.List):
            return 'list'
        elif isinstance(node, ast.Dict):
            return 'dict'
        elif isinstance(node, ast.Set):
            return 'set'
        elif isinstance(node, ast.Tuple):
            return 'tuple'
            
        elif isinstance(node, ast.Name):
            return self.type_map.get(node.id, 'unknown')
            
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name == 'str':
                    return 'str'
                elif func_name == 'int':
                    return 'int'
                elif func_name == 'list':
                    return 'list'
                elif func_name == 'dict':
                    return 'dict'
                    
        return 'unknown'
        
    def get_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        return None


class TypeChecker:
    def __init__(self, tree):
        self.tree = tree
        self.issues = []
        
    def check(self):
        inferencer = TypeInference(self.tree)
        type_map, errors = inferencer.infer()
        
        self.issues.extend(errors)
        
        self.check_function_args()
        self.check_subscript_operations()
        
        return self.issues
        
    def check_function_args(self):
        visitor = FunctionCallVisitor()
        visitor.visit(self.tree)
        
        for error in visitor.errors:
            self.issues.append(error)
            
    def check_subscript_operations(self):
        visitor = SubscriptVisitor()
        visitor.visit(self.tree)
        
        for error in visitor.errors:
            self.issues.append(error)


class FunctionCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors = []
        self.function_defs = {}
        
    def visit_FunctionDef(self, node):
        self.function_defs[node.name] = {
            'args': len(node.args.args),
            'lineno': node.lineno
        }
        self.generic_visit(node)
        
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self.function_defs:
                expected = self.function_defs[func_name]['args']
                actual = len(node.args)
                
                if expected != actual:
                    self.errors.append({
                        'type': 'arg_count_mismatch',
                        'lineno': node.lineno,
                        'message': f"Function '{func_name}' expects {expected} args, got {actual}",
                        'severity': 'error'
                    })
                    
        self.generic_visit(node)


class SubscriptVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors = []
        
    def visit_Subscript(self, node):
        self.generic_visit(node)


def check_types(tree):
    checker = TypeChecker(tree)
    return checker.check()
