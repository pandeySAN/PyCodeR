import ast


class AutoFixer:
    def __init__(self, tree, source_code, issues):
        self.tree = tree
        self.source = source_code
        self.issues = issues
        self.fixes = []
        
    def apply_fixes(self):
        self.fix_unused_imports()
        self.fix_unused_variables()
        
        return self.fixes
        
    def fix_unused_imports(self):
        unused_imports = [i for i in self.issues if i.get('type') == 'unused_import']
        
        if not unused_imports:
            return
            
        lines = self.source.split('\n')
        imports_to_remove = set()
        
        for issue in unused_imports:
            imports_to_remove.add(issue['lineno'])
            
        new_lines = []
        for i, line in enumerate(lines):
            if (i + 1) not in imports_to_remove:
                new_lines.append(line)
            else:
                self.fixes.append({
                    'type': 'remove_import',
                    'lineno': i + 1,
                    'original': line,
                    'fixed': ''
                })
                
        return '\n'.join(new_lines)
        
    def fix_unused_variables(self):
        unused_vars = [i for i in self.issues if i.get('type') == 'variable']
        
        for issue in unused_vars:
            self.fixes.append({
                'type': 'unused_variable',
                'lineno': issue['lineno'],
                'name': issue['name'],
                'suggestion': f"Remove unused variable '{issue['name']}' or use it"
            })


class ASTRewriter(ast.NodeTransformer):
    def __init__(self, removals):
        self.removals = removals
        
    def visit_Import(self, node):
        if node.lineno in self.removals:
            return None
        return node
        
    def visit_ImportFrom(self, node):
        if node.lineno in self.removals:
            return None
        return node
        
    def visit_Assign(self, node):
        targets_to_keep = []
        for target in node.targets:
            if isinstance(target, ast.Name):
                if target.id not in self.removals:
                    targets_to_keep.append(target)
            else:
                targets_to_keep.append(target)
                
        if not targets_to_keep:
            return None
            
        node.targets = targets_to_keep
        return node


class CodeFormatter:
    def __init__(self, tree):
        self.tree = tree
        
    def format(self):
        try:
            import astor
            return astor.to_source(self.tree)
        except ImportError:
            return ast.unparse(self.tree) if hasattr(ast, 'unparse') else None


def apply_auto_fixes(tree, source_code, issues):
    fixer = AutoFixer(tree, source_code, issues)
    return fixer.apply_fixes()
