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

    def _block_def_vars(self, block):
        """Return the set of variable names defined by statements in a block."""
        defs = set()
        for stmt in block.statements:
            for def_id, def_info in self.definitions.items():
                if def_info['block'] is block and def_info['stmt'] is stmt:
                    defs.add(def_info['var'])
        return defs

    def compute_definite_assignment(self):
        """Compute definite assignment using intersection at join points.

        A variable is definitely assigned at a program point only if it is
        assigned on every path reaching that point. This catches cases like::

            if flag:
                r = 1
            print(r)   # r possibly undefined

        Returns a dict mapping block name -> set of variables definitely
        assigned at block exit (reach_out analogue).
        """
        # gen[kill] per block: variables defined in the block
        gen = {}
        for block in self.cfg.blocks:
            gen[block] = self._block_def_vars(block)

        definite_in = {block: set() for block in self.cfg.blocks}
        definite_out = {block: set() for block in self.cfg.blocks}

        # Worklist algorithm: guaranteed to converge for finite lattices.
        # Compute reachability from entry so that isolated blocks (e.g. empty
        # ``after_return`` blocks created by the CFG builder with no incoming
        # edge) don't poison intersections at join points.
        reachable = set()
        worklist_reach = [self.cfg.entry]
        while worklist_reach:
            b = worklist_reach.pop(0)
            if b in reachable:
                continue
            reachable.add(b)
            worklist_reach.extend(s for s in b.successors if s not in reachable)

        worklist = list(self.cfg.blocks)
        iterations = 0
        while worklist:
            block = worklist.pop(0)
            iterations += 1
            if block.predecessors:
                # Only intersect reachable predecessors; unreachable ones
                # (e.g. isolated after_return blocks) would empty the set.
                reachable_preds = [p for p in block.predecessors if p in reachable]
                if reachable_preds:
                    new_in = set(definite_out[reachable_preds[0]])
                    for pred in reachable_preds[1:]:
                        new_in &= definite_out[pred]
                else:
                    new_in = set()
            else:
                new_in = set()

            old_out = definite_out[block].copy()

            definite_in[block] = new_in
            definite_out[block] = (new_in - gen[block]) | gen[block]

            if definite_out[block] != old_out:
                for succ in block.successors:
                    if succ not in worklist:
                        worklist.append(succ)

        return {'in': definite_in, 'out': definite_out}

    def find_possibly_undefined_uses(self):
        """Find variables used without being definitely assigned on all paths.

        Uses definite-assignment (intersection) analysis to catch cases where
        a variable may be used before definition on some execution paths::

            if flag:
                r = 1
            print(r)   # possibly undefined

        Returns a list of dicts with 'var', 'stmt', 'block', 'lineno' keys.
        """
        # Metadata: builtins, function params, function/class names.
        builtin_names = set(dir(builtins))
        builtin_names.update({'__file__', '__name__'})

        params_by_function = {}
        func_parent = {}
        function_and_class_names = set()

        def _collect_params(func_node):
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

        if self.tree is not None:
            def walk(node, enclosing_func=None):
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        function_and_class_names.add(child.name)
                        params_by_function[child.name] = _collect_params(child)
                        func_parent[child.name] = enclosing_func
                        walk(child, child.name)
                    elif isinstance(child, ast.ClassDef):
                        function_and_class_names.add(child.name)
                        walk(child, enclosing_func)
                    else:
                        walk(child, enclosing_func)

            walk(self.tree)

        def all_params_in_scope(func_name):
            params = set()
            current = func_name
            while current is not None:
                params.update(params_by_function.get(current, set()))
                current = func_parent.get(current)
            return params

        da = self.compute_definite_assignment()
        definite_in = da['in']

        undefined = []

        for block in self.cfg.blocks:
            enclosing_fn = block.function
            inside_function = enclosing_fn is not None
            params = all_params_in_scope(enclosing_fn) if inside_function else set()

            # Start with definitely-assigned variables at block entry,
            # plus parameters and function/class names for functions.
            local_definite = set(definite_in[block])
            if inside_function:
                local_definite.update(params)
                local_definite.update(function_and_class_names)

            for stmt in block.statements:
                if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    continue

                uses = self.get_uses(stmt)
                # Vars defined by this same statement (comprehension targets,
                # with-statement optional vars, etc.).
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
                    if inside_function and var in params:
                        continue
                    if var in stmt_def_vars:
                        continue
                    if var in local_definite:
                        continue

                    undefined.append({
                        'var': var,
                        'stmt': stmt,
                        'block': block.name,
                        'lineno': getattr(stmt, 'lineno', -1),
                        'message': f"Variable '{var}' may be used before definition",
                        'severity': 'error',
                    })

                for def_id, def_info in self.definitions.items():
                    if def_info['block'] is block and def_info['stmt'] is stmt:
                        local_definite.add(def_info['var'])

        return undefined

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
