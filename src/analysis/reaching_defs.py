import ast
import builtins


class ReachingDefinitions:
    def __init__(self, cfg, tree=None):
        self.cfg = cfg
        self.tree = tree
        self.definitions = {}
        self.def_id = 0
        
    def analyze(self):
        self.collect_definitions()
        
        for block in self.cfg.blocks:
            block.reach_in = set()
            block.reach_out = set()
            
        changed = True
        iterations = 0
        
        while changed and iterations < 100:
            changed = False
            iterations += 1
            
            for block in self.cfg.blocks:
                old_out = block.reach_out.copy()
                
                block.reach_in = set()
                for pred in block.predecessors:
                    block.reach_in.update(pred.reach_out)
                    
                gen = self.get_gen(block)
                kill = self.get_kill(block)
                
                block.reach_out = gen.union(block.reach_in - kill)
                
                if block.reach_out != old_out:
                    changed = True
                    
        return self.build_result()
        
    def _is_def_target(self, node):
        """Return the name(s) defined by a store target, or None."""
        if isinstance(node, ast.Name):
            return [node.id]
        if isinstance(node, (ast.Tuple, ast.List)):
            names = []
            for elt in node.elts:
                names.extend(self._is_def_target(elt) or [])
            return names or None
        return None
        
    def _collect_stmt_defs(self, stmt, block):
        """Register definitions created by a statement and return their ids."""
        ids = []
        if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
            targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
            for target in targets:
                if target is None:
                    continue
                for name in self._is_def_target(target) or []:
                    def_info = {
                        'id': self.def_id,
                        'var': name,
                        'stmt': stmt,
                        'block': block,
                    }
                    self.definitions[self.def_id] = def_info
                    ids.append(self.def_id)
                    self.def_id += 1
        elif isinstance(stmt, ast.For):
            for name in self._is_def_target(stmt.target) or []:
                def_info = {
                    'id': self.def_id,
                    'var': name,
                    'stmt': stmt,
                    'block': block,
                }
                self.definitions[self.def_id] = def_info
                ids.append(self.def_id)
                self.def_id += 1
        elif isinstance(stmt, ast.With):
            for item in stmt.items:
                if item.optional_vars:
                    for name in self._is_def_target(item.optional_vars) or []:
                        def_info = {
                            'id': self.def_id,
                            'var': name,
                            'stmt': stmt,
                            'block': block,
                        }
                        self.definitions[self.def_id] = def_info
                        ids.append(self.def_id)
                        self.def_id += 1
        elif isinstance(stmt, ast.Try):
            # except-as names are registered in find_undefined_uses via the
            # handler_names mapping so they are scoped to the handler body.
            pass
        # Comprehension/generator targets (e.g. `for x in ...` in a listcomp)
        # bind their names inside the comprehension, so uses within the same
        # comprehension see them.
        for comp in self._comprehensions_in(stmt):
            for name in self._is_def_target(comp.target) or []:
                def_info = {
                    'id': self.def_id,
                    'var': name,
                    'stmt': stmt,
                    'block': block,
                }
                self.definitions[self.def_id] = def_info
                ids.append(self.def_id)
                self.def_id += 1
        # Lambda parameters bind their names inside the lambda body.
        for lam in self._lambdas_in(stmt):
            for arg in lam.args.args:
                def_info = {
                    'id': self.def_id,
                    'var': arg.arg,
                    'stmt': stmt,
                    'block': block,
                }
                self.definitions[self.def_id] = def_info
                ids.append(self.def_id)
                self.def_id += 1
        return ids
            
    def collect_definitions(self):
        # First, register every real assignment in every block.
        for block in self.cfg.blocks:
            for stmt in block.statements:
                self._collect_stmt_defs(stmt, block)
                
        # Seed synthetic definitions for names that are always available so
        # they are treated as reaching definitions instead of false positives:
        #   - function parameters (defined at function entry)
        #   - function and class names (defined after their def/class statement)
        #   - imports
        #   - builtins (always defined)
        for block in self.cfg.blocks:
            for stmt in block.statements:
                if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Function name is defined at function entry (visible inside
                    # the body for recursion).
                    self._add_synthetic(stmt.name, block, stmt, 'function')
                    # Parameters are defined at function entry. Collect all
                    # parameter kinds: pos-only, positional-or-keyword,
                    # keyword-only, *args, **kwargs.
                    for arg in stmt.args.posonlyargs:
                        self._add_synthetic(arg.arg, block, stmt, 'parameter')
                    for arg in stmt.args.args:
                        self._add_synthetic(arg.arg, block, stmt, 'parameter')
                    for arg in stmt.args.kwonlyargs:
                        self._add_synthetic(arg.arg, block, stmt, 'parameter')
                    if stmt.args.vararg:
                        self._add_synthetic(stmt.args.vararg.arg, block, stmt, 'parameter')
                    if stmt.args.kwarg:
                        self._add_synthetic(stmt.args.kwarg.arg, block, stmt, 'parameter')
                    # Default argument values are evaluated at definition time.
                    for default in stmt.args.defaults:
                        for name in self._names_in(default):
                            self._mark_used(name, block, stmt)
                    for default in stmt.args.kw_defaults:
                        if default is not None:
                            for name in self._names_in(default):
                                self._mark_used(name, block, stmt)
                elif isinstance(stmt, ast.ClassDef):
                    self._add_synthetic(stmt.name, block, stmt, 'class')
                    # Methods defined inside the class body become parameters
                    # (self/cls) of their enclosing methods; the class name
                    # itself is already handled above.
                elif isinstance(stmt, ast.Import):
                    for alias in stmt.names:
                        name = alias.asname if alias.asname else alias.name.split('.')[0]
                        self._add_synthetic(name, block, stmt, 'import')
                elif isinstance(stmt, ast.ImportFrom):
                    for alias in stmt.names:
                        name = alias.asname if alias.asname else alias.name
                        self._add_synthetic(name, block, stmt, 'import')
                        
    def _add_synthetic(self, name, block, stmt, kind):
        """Add a synthetic definition for a name that is always defined."""
        def_info = {
            'id': self.def_id,
            'var': name,
            'stmt': stmt,
            'block': block,
            'synthetic': True,
            'kind': kind,
        }
        self.definitions[self.def_id] = def_info
        self.def_id += 1
        
    def _names_in(self, node):
        """Yield all Name ids loaded in an expression (e.g. default values)."""
        names = []
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                names.append(child.id)
        return names

    def _comprehensions_in(self, node):
        """Yield all ast.comprehension nodes nested inside a statement."""
        found = []
        for child in ast.walk(node):
            if isinstance(child, ast.comprehension):
                found.append(child)
        return found

    def _lambdas_in(self, node):
        """Yield all ast.Lambda nodes nested inside a statement."""
        found = []
        for child in ast.walk(node):
            if isinstance(child, ast.Lambda):
                found.append(child)
        return found
        
    def _mark_used(self, name, block, stmt):
        """Placeholder hook: names used in default expressions are resolved
        against reaching definitions by the normal analysis."""
        return None
        
    def get_gen(self, block):
        gen = set()
        for def_id, def_info in self.definitions.items():
            if def_info['block'] == block:
                gen.add(def_id)
        return gen
        
    def get_kill(self, block):
        kill = set()
        block_defs = {}
        
        for def_id, def_info in self.definitions.items():
            if def_info['block'] == block:
                var = def_info['var']
                if var not in block_defs:
                    block_defs[var] = []
                block_defs[var].append(def_id)
                
        for var, def_ids in block_defs.items():
            for def_id, def_info in self.definitions.items():
                if def_info['var'] == var and def_id not in def_ids:
                    kill.add(def_id)
                    
        return kill
        
    def build_result(self):
        result = {}
        for block in self.cfg.blocks:
            result[block.name] = {
                'reach_in': [self.definitions[d] for d in block.reach_in],
                'reach_out': [self.definitions[d] for d in block.reach_out]
            }
        return result
        
    def find_undefined_uses(self):
        """Find variables that may be used before definition.

        A use is considered safe when:
          * it is a builtin (from ``dir(builtins)``),
          * it is a function or class name (defined after its def/class stmt),
          * it is a parameter of the enclosing function (defined at entry),
          * it is a name defined at module level (imports, top-level assigns)
            and the use happens inside a function body (which runs later), or
          * there is a reaching definition for it at this program point.
        """
        undefined = []
        
        # Python built-ins are always defined.
        builtin_names = set(dir(builtins))
        # Interpreter-defined module-level names (__file__, __name__) are also
        # always available at module level, though not in dir(builtins).
        builtin_names.update({'__file__', '__name__'})
        
        # Map function name -> set of parameter names (all kinds: pos-only,
        # positional-or-keyword, keyword-only, *args, **kwargs).
        params_by_function = {}
        # function -> parent enclosing function name (or None at module level).
        func_parent = {}
        # Names defined at module level (safe to use inside function bodies).
        module_level_defined = set()
        # Function/class names are always defined once their statement ran.
        function_and_class_names = set()
        # (function_name, handler_name) -> except-as name defined in that
        # handler's scope.
        handler_names = {}

        def _collect_params(func_node):
            """Return the set of all parameter names for a function node."""
            params = set()
            for arg in func_node.args.posonlyargs:
                params.add(arg.arg)
            for arg in func_node.args.args:
                params.add(arg.arg)
            for arg in func_node.args.kwonlyargs:
                params.add(arg.arg)
            if func_node.args.vararg:
                params.add(func_node.args.vararg.arg)
            if func_node.args.kwarg:
                params.add(func_node.args.kwarg.arg)
            return params

        # Gather metadata from the AST tree. We walk recursively so we know
        # each function's enclosing function, which lets nested functions
        # close over outer parameters, and methods inside classes see their
        # first parameter (self/cls).
        if self.tree is not None:
            def walk(node, enclosing_func=None):
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        function_and_class_names.add(child.name)
                        params_by_function[child.name] = _collect_params(child)
                        func_parent[child.name] = enclosing_func
                        # Recurse into the body with this function as enclosing.
                        walk(child, child.name)
                    elif isinstance(child, ast.ClassDef):
                        function_and_class_names.add(child.name)
                        # Methods inside the class see their own parameters;
                        # the enclosing function context is unchanged for
                        # nested functions defined in class methods.
                        walk(child, enclosing_func)
                    elif isinstance(child, (ast.Import, ast.ImportFrom)):
                        if isinstance(child, ast.Import):
                            for alias in child.names:
                                module_level_defined.add(
                                    alias.asname if alias.asname else alias.name.split('.')[0])
                        else:
                            for alias in child.names:
                                module_level_defined.add(
                                    alias.asname if alias.asname else alias.name)
                    elif isinstance(child, ast.Assign):
                        # Only top-level (module-level) assignments count as
                        # module-level defined.
                        if enclosing_func is None:
                            for target in child.targets:
                                for name in self._is_def_target(target) or []:
                                    module_level_defined.add(name)
                    elif isinstance(child, ast.Try):
                        for handler in child.handlers:
                            if handler.name:
                                key = enclosing_func
                                handler_names.setdefault(key, set()).add(handler.name)
                        walk(child, enclosing_func)
                    else:
                        walk(child, enclosing_func)

            walk(self.tree)

        # Transitive parameter set: a function can close over the parameters of
        # every function that encloses it.
        def all_params_in_scope(func_name):
            params = set()
            current = func_name
            while current is not None:
                params.update(params_by_function.get(current, set()))
                current = func_parent.get(current)
            return params

        for block in self.cfg.blocks:
            enclosing_fn = block.function
            inside_function = enclosing_fn is not None
            params = all_params_in_scope(enclosing_fn) if inside_function else set()
            
            # Definitions that reach the start of this block.
            defined_vars = {
                self.definitions[d]['var'] for d in block.reach_in
            }
            
            # except-as names (e.g. `except ValueError as e`) are defined
            # inside their handler's scope; add them for the enclosing function.
            if inside_function:
                defined_vars.update(handler_names.get(enclosing_fn, set()))
            
            # Walk statements in program order so a use only sees definitions
            # that come before it (from predecessors or earlier in the block).
            for stmt in block.statements:
                # Function/async-function/class definitions create their own
                # CFG blocks; their bodies are analyzed separately, so skip
                # them here to avoid picking up names from nested scopes.
                if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    # Still register definitions made by this statement.
                    stmt_def_vars = {
                        def_info['var']
                        for def_id, def_info in self.definitions.items()
                        if def_info['block'] is block and def_info['stmt'] is stmt
                    }
                    defined_vars.update(stmt_def_vars)
                    continue
                uses = self.get_uses(stmt)
                # Vars defined by this same statement (covers lambda/comprehension
                # parameters and x = x + 1 style statements where the use is
                # bound by the statement's own definition).
                stmt_def_vars = {
                    def_info['var']
                    for def_id, def_info in self.definitions.items()
                    if def_info['block'] is block and def_info['stmt'] is stmt
                }
                
                for var in uses:
                    if var in builtin_names:
                        continue
                    if var in function_and_class_names:
                        continue
                    if inside_function and var in module_level_defined:
                        continue
                    if var in params:
                        continue
                    if var in stmt_def_vars:
                        continue
                    
                    if var not in defined_vars:
                        undefined.append({
                            'var': var,
                            'stmt': stmt,
                            'block': block.name,
                            'lineno': getattr(stmt, 'lineno', -1)
                        })
                
                # Register definitions made by this statement for later uses.
                defined_vars.update(stmt_def_vars)
                
        return undefined
        
    def get_uses(self, stmt):
        uses = set()
        for node in ast.walk(stmt):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                uses.add(node.id)
        return uses


def analyze_reaching_defs(cfg):
    analyzer = ReachingDefinitions(cfg)
    return analyzer.analyze()
