import ast
from .basic_block import BasicBlock, ControlFlowGraph


class CFGBuilder(ast.NodeVisitor):
    def __init__(self, name="main"):
        self.cfg = ControlFlowGraph(name)
        self.current_block = self.cfg.entry
        self.break_stack = []
        self.continue_stack = []
        self.func_exit = None
        
    def build(self, tree):
        self.visit(tree)
        if self.current_block and not self.current_block.has_terminator():
            self.cfg.add_edge(self.current_block, self.cfg.exit)
        return self.cfg
        
    def new_block(self, name=None):
        block = self.cfg.new_block(name)
        return block
        
    def add_stmt(self, stmt):
        if self.current_block:
            self.current_block.add_statement(stmt)
            
    def visit_Module(self, node):
        for stmt in node.body:
            self.visit(stmt)
            
    def visit_FunctionDef(self, node):
        func_entry = self.new_block(f"{node.name}_entry")
        func_exit = self.new_block(f"{node.name}_exit")
        
        old_block = self.current_block
        old_exit = self.func_exit
        
        if self.current_block:
            self.cfg.add_edge(self.current_block, func_entry)
        self.current_block = func_entry
        self.func_exit = func_exit
        
        for stmt in node.body:
            self.visit(stmt)
            
        if self.current_block and not self.current_block.has_terminator():
            self.cfg.add_edge(self.current_block, func_exit)
            
        self.current_block = func_exit
        self.func_exit = old_exit
        
    def visit_If(self, node):
        test_block = self.current_block
        self.add_stmt(node)
        
        then_block = self.new_block("if_then")
        else_block = self.new_block("if_else")
        merge_block = self.new_block("if_merge")
        
        self.cfg.add_edge(test_block, then_block)
        self.cfg.add_edge(test_block, else_block)
        
        self.current_block = then_block
        for stmt in node.body:
            self.visit(stmt)
        if not self.current_block.has_terminator():
            self.cfg.add_edge(self.current_block, merge_block)
            
        self.current_block = else_block
        for stmt in node.orelse:
            self.visit(stmt)
        if not self.current_block.has_terminator():
            self.cfg.add_edge(self.current_block, merge_block)
            
        self.current_block = merge_block
        
    def visit_While(self, node):
        loop_header = self.new_block("while_header")
        loop_body = self.new_block("while_body")
        loop_exit = self.new_block("while_exit")
        
        if self.current_block:
            self.cfg.add_edge(self.current_block, loop_header)
            
        loop_header.add_statement(node)
        self.cfg.add_edge(loop_header, loop_body)
        self.cfg.add_edge(loop_header, loop_exit)
        
        self.break_stack.append(loop_exit)
        self.continue_stack.append(loop_header)
        
        self.current_block = loop_body
        for stmt in node.body:
            self.visit(stmt)
            
        if self.current_block and not self.current_block.has_terminator():
            self.cfg.add_edge(self.current_block, loop_header)
            
        self.break_stack.pop()
        self.continue_stack.pop()
        
        self.current_block = loop_exit
        
    def visit_For(self, node):
        loop_header = self.new_block("for_header")
        loop_body = self.new_block("for_body")
        loop_exit = self.new_block("for_exit")
        
        if self.current_block:
            self.cfg.add_edge(self.current_block, loop_header)
            
        loop_header.add_statement(node)
        self.cfg.add_edge(loop_header, loop_body)
        self.cfg.add_edge(loop_header, loop_exit)
        
        self.break_stack.append(loop_exit)
        self.continue_stack.append(loop_header)
        
        self.current_block = loop_body
        for stmt in node.body:
            self.visit(stmt)
            
        if self.current_block and not self.current_block.has_terminator():
            self.cfg.add_edge(self.current_block, loop_header)
            
        self.break_stack.pop()
        self.continue_stack.pop()
        
        self.current_block = loop_exit
        
    def visit_Break(self, node):
        self.add_stmt(node)
        if self.break_stack:
            self.cfg.add_edge(self.current_block, self.break_stack[-1])
        self.current_block = self.new_block("after_break")
        
    def visit_Continue(self, node):
        self.add_stmt(node)
        if self.continue_stack:
            self.cfg.add_edge(self.current_block, self.continue_stack[-1])
        self.current_block = self.new_block("after_continue")
        
    def visit_Return(self, node):
        self.add_stmt(node)
        if self.func_exit:
            self.cfg.add_edge(self.current_block, self.func_exit)
        else:
            self.cfg.add_edge(self.current_block, self.cfg.exit)
        self.current_block = self.new_block("after_return")
        
    def visit_Try(self, node):
        try_block = self.new_block("try_body")
        except_blocks = []
        else_block = None
        finally_block = None
        merge_block = self.new_block("try_merge")
        
        if self.current_block:
            self.cfg.add_edge(self.current_block, try_block)
            
        self.current_block = try_block
        for stmt in node.body:
            self.visit(stmt)
            
        for handler in node.handlers:
            except_block = self.new_block("except")
            except_blocks.append(except_block)
            self.cfg.add_edge(try_block, except_block)
            
            self.current_block = except_block
            for stmt in handler.body:
                self.visit(stmt)
            if not self.current_block.has_terminator():
                self.cfg.add_edge(self.current_block, merge_block)
                
        if not self.current_block.has_terminator():
            self.cfg.add_edge(self.current_block, merge_block)
            
        self.current_block = merge_block
        
    def visit_Raise(self, node):
        self.add_stmt(node)
        self.cfg.add_edge(self.current_block, self.cfg.exit)
        self.current_block = self.new_block("after_raise")
        
    def generic_visit(self, node):
        if isinstance(node, ast.stmt):
            self.add_stmt(node)
        super().generic_visit(node)


def build_cfg(tree, name="main"):
    builder = CFGBuilder(name)
    return builder.build(tree)
