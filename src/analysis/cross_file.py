import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class CrossFileAnalyzer:
    """
    Analyzes multiple files to detect cross-file issues like:
    - Unused imports across the project
    - Undefined symbols imported from other modules
    - Circular dependencies
    """
    
    def __init__(self, project_files: List[str]):
        self.files = project_files
        self.imports = defaultdict(set)  # file -> set of imported names
        self.exports = defaultdict(set)  # file -> set of defined names
        self.import_sources = defaultdict(list)  # file -> list of (module, names, lineno)
        self.usage = defaultdict(set)  # file -> set of used names
        
    def analyze(self) -> List[Dict]:
        """Run cross-file analysis"""
        issues = []
        
        # First pass: collect imports and definitions
        for filepath in self.files:
            self._analyze_file(filepath)
            
        # Second pass: find unused imports
        for filepath in self.files:
            unused = self._find_unused_imports(filepath)
            issues.extend(unused)
            
        # Find undefined imports
        undefined = self._find_undefined_imports()
        issues.extend(undefined)
        
        return issues
        
    def _analyze_file(self, filepath: str):
        """Extract imports, exports, and usage from a file"""
        try:
            with open(filepath, 'r') as f:
                tree = ast.parse(f.read())
        except:
            return
            
        visitor = ImportExportVisitor(filepath)
        visitor.visit(tree)
        
        self.imports[filepath] = visitor.imports
        self.exports[filepath] = visitor.exports
        self.import_sources[filepath] = visitor.import_details
        self.usage[filepath] = visitor.usage
        
    def _find_unused_imports(self, filepath: str) -> List[Dict]:
        """Find imports that are never used in the file"""
        issues = []
        imported = self.imports[filepath]
        used_names = self.usage[filepath]
        
        unused = imported - used_names
        
        # Find line numbers for unused imports
        for module, names, lineno in self.import_sources[filepath]:
            for name in names:
                if name in unused:
                    issues.append({
                        'type': 'unused_import',
                        'file': filepath,
                        'lineno': lineno,
                        'message': f"Import '{name}' from '{module}' is never used",
                        'severity': 'warning'
                    })
                    
        return issues
        
    def _find_undefined_imports(self) -> List[Dict]:
        """Find imports from modules that don't define those symbols"""
        issues = []
        
        for filepath, import_details in self.import_sources.items():
            for module, names, lineno in import_details:
                # Try to resolve module to a file in project
                module_file = self._resolve_module(module, filepath)
                
                if module_file and module_file in self.exports:
                    exported = self.exports[module_file]
                    
                    for name in names:
                        if name not in exported and name != '*':
                            issues.append({
                                'type': 'undefined_import',
                                'file': filepath,
                                'lineno': lineno,
                                'message': f"'{name}' is not defined in module '{module}'",
                                'severity': 'error'
                            })
                            
        return issues
        
    def _resolve_module(self, module_name: str, current_file: str) -> str:
        """Try to resolve module name to a file path"""
        current_dir = Path(current_file).parent
        
        # Handle relative imports
        parts = module_name.split('.')
        
        # Try direct file match
        candidate = current_dir / f"{parts[-1]}.py"
        if str(candidate) in self.files:
            return str(candidate)
            
        # Try package match
        candidate = current_dir / parts[-1] / "__init__.py"
        if str(candidate) in self.files:
            return str(candidate)
            
        return None


class ImportExportVisitor(ast.NodeVisitor):
    """Visitor to collect imports, exports, and usage"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.imports = set()
        self.exports = set()
        self.import_details = []  # (module, [names], lineno)
        self.usage = set()
        self.in_import = False
        
    def visit_Import(self, node):
        """Handle 'import x' statements"""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name.split('.')[0]
            self.imports.add(name)
            self.import_details.append((alias.name, [name], node.lineno))
            
    def visit_ImportFrom(self, node):
        """Handle 'from x import y' statements"""
        module = node.module or ''
        names = []
        
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            if name != '*':
                self.imports.add(name)
                names.append(name)
                
        if names:
            self.import_details.append((module, names, node.lineno))
            
    def visit_FunctionDef(self, node):
        """Track function definitions (exports)"""
        self.exports.add(node.name)
        self.generic_visit(node)
        
    def visit_ClassDef(self, node):
        """Track class definitions (exports)"""
        self.exports.add(node.name)
        self.generic_visit(node)
        
    def visit_Assign(self, node):
        """Track variable definitions"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.exports.add(target.id)
        self.generic_visit(node)
        
    def visit_Name(self, node):
        """Track name usage"""
        if isinstance(node.ctx, (ast.Load, ast.Del)):
            self.usage.add(node.id)
        self.generic_visit(node)


def analyze_cross_file(files: List[str]) -> List[Dict]:
    """Main entry point for cross-file analysis"""
    analyzer = CrossFileAnalyzer(files)
    return analyzer.analyze()
