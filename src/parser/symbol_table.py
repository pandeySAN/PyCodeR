import ast
from enum import Enum


class ScopeType(Enum):
    GLOBAL = 1
    FUNCTION = 2
    CLASS = 3
    LOCAL = 4


class Symbol:
    def __init__(self, name, symbol_type, lineno, scope):
        self.name = name
        self.type = symbol_type
        self.lineno = lineno
        self.scope = scope
        self.references = []
        self.is_used = False
        
    def add_reference(self, lineno):
        self.references.append(lineno)
        self.is_used = True


class Scope:
    def __init__(self, name, scope_type, parent=None):
        self.name = name
        self.type = scope_type
        self.parent = parent
        self.symbols = {}
        self.children = []
        
    def define(self, symbol):
        self.symbols[symbol.name] = symbol
        
    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None
        
    def lookup_local(self, name):
        return self.symbols.get(name)


class SymbolTable:
    def __init__(self):
        self.global_scope = Scope("global", ScopeType.GLOBAL)
        self.current_scope = self.global_scope
        self.scopes = [self.global_scope]
        
    def enter_scope(self, name, scope_type):
        new_scope = Scope(name, scope_type, self.current_scope)
        self.current_scope.children.append(new_scope)
        self.current_scope = new_scope
        self.scopes.append(new_scope)
        return new_scope
        
    def exit_scope(self):
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
            
    def define_symbol(self, name, sym_type, lineno):
        symbol = Symbol(name, sym_type, lineno, self.current_scope)
        self.current_scope.define(symbol)
        return symbol
        
    def lookup_symbol(self, name):
        return self.current_scope.lookup(name)
        
    def get_all_symbols(self):
        all_syms = []
        for scope in self.scopes:
            all_syms.extend(scope.symbols.values())
        return all_syms
        
    def get_unused_symbols(self):
        unused = []
        for scope in self.scopes:
            for symbol in scope.symbols.values():
                if not symbol.is_used and symbol.type != 'import':
                    unused.append(symbol)
        return unused


class SymbolTableBuilder(ast.NodeVisitor):
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_function = None
        
    def visit_FunctionDef(self, node):
        self.symbol_table.define_symbol(node.name, 'function', node.lineno)
        self.symbol_table.enter_scope(node.name, ScopeType.FUNCTION)
        
        for arg in node.args.args:
            self.symbol_table.define_symbol(arg.arg, 'parameter', node.lineno)
            
        old_func = self.current_function
        self.current_function = node.name
        
        self.generic_visit(node)
        
        self.current_function = old_func
        self.symbol_table.exit_scope()
        
    def visit_ClassDef(self, node):
        self.symbol_table.define_symbol(node.name, 'class', node.lineno)
        self.symbol_table.enter_scope(node.name, ScopeType.CLASS)
        self.generic_visit(node)
        self.symbol_table.exit_scope()
        
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.symbol_table.define_symbol(target.id, 'variable', node.lineno)
        self.generic_visit(node)
        
    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.symbol_table.define_symbol(name, 'import', node.lineno)
            
    def visit_ImportFrom(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.symbol_table.define_symbol(name, 'import', node.lineno)
            
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            symbol = self.symbol_table.lookup_symbol(node.id)
            if symbol:
                symbol.add_reference(node.lineno)
        self.generic_visit(node)
        
    def build(self, tree):
        self.visit(tree)
        return self.symbol_table


def build_symbol_table(tree):
    builder = SymbolTableBuilder()
    return builder.build(tree)
