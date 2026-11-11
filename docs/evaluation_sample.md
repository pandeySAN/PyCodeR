# Manual False-Positive Review (sample of 50 findings)
Overall FP rate: 13/50 = 26.0%

| # | repo | category | FP? | file:lineno | message | reason |
|---|------|----------|-----|-------------|---------|--------|
| 1 | flask | security | TP | config.py:209 | Use of dangerous function 'exec' | security finding (TP candidate) |
| 2 | flask | undefined_variable | TP | test_basic.py:1621 | Variable 'ZeroDivisionError' may be used before definition | 'ZeroDivisionError' possibly undefined (TP candidate) |
| 3 | requests | undefined_variable | TP | adapters.py:158 | Variable 'connections' may be used before definition | 'connections' possibly undefined (TP candidate) |
| 4 | flask | dead_code | TP | test_basic.py:1023 | Block test_errorhandler_precedence_entry is unreachable | unreachable code (TP candidate) |
| 5 | flask | arg_count_mismatch | FP | cli.py:349 | Function 'locate_app' expects 3 args, got 2 | callee may accept *args/**kwargs (FP candidate) |
| 6 | flask | unused | TP | test_request.py:18 | Function 'catcher' is defined but never called | 'catcher' no references found (TP candidate) |
| 7 | requests | dead_code | TP | test_utils.py:280 | Block test_not_bypass_no_proxy_keyword_entry is unreachable | unreachable code (TP candidate) |
| 8 | requests | undefined_variable | TP | cookies.py:616 | Variable 'cookie_in_jar' may be used before definition | 'cookie_in_jar' possibly undefined (TP candidate) |
| 9 | requests | undefined_variable | TP | models.py:254 | Variable 'event' may be used before definition | 'event' possibly undefined (TP candidate) |
| 10 | requests | arg_count_mismatch | FP | cookies.py:380 | Function 'remove_cookie_by_name' expects 4 args, got 2 | callee may accept *args/**kwargs (FP candidate) |
| 11 | requests | undefined_variable | FP | test_requests.py:188 | Variable 'bytes' may be used before definition | 'bytes' is a builtin/framework name |
| 12 | flask | unused | TP | app.py:390 | Function 'send_static_file' is defined but never called | 'send_static_file' no references found (TP candidate) |
| 13 | requests | undefined_variable | TP | adapters.py:158 | Variable 'DEFAULT_POOLBLOCK' may be used before definition | 'DEFAULT_POOLBLOCK' possibly undefined (TP candidate) |
| 14 | requests | dead_code | TP | test_requests.py:2157 | Block for_header is unreachable | unreachable code (TP candidate) |
| 15 | flask | unused | TP | test_blueprints.py:87 | Function 'app_forbidden' is defined but never called | 'app_forbidden' no references found (TP candidate) |
| 16 | flask | dead_code | TP | test_basic.py:1065 | Block fail_entry is unreachable | unreachable code (TP candidate) |
| 17 | flask | security | TP | helpers.py:623 | Use of dangerous function '__import__' | security finding (TP candidate) |
| 18 | flask | arg_count_mismatch | FP | test_cli.py:469 | Function 'invoke' expects 3 args, got 1 | callee may accept *args/**kwargs (FP candidate) |
| 19 | requests | unused | FP | test_requests.py:2397 | Function 'test_update' is defined but never called | 'test_update' is a pytest test function |
| 20 | flask | undefined_variable | TP | testing.py:27 | Variable 'kwargs' may be used before definition | 'kwargs' possibly undefined (TP candidate) |
| 21 | flask | other | TP | app.py:1145 | Function 'url_for' has complexity 13 (max 10) | other (TP candidate) |
| 22 | requests | arg_count_mismatch | FP | utils.py:932 | Function 'should_bypass_proxies' expects 2 args, got 1 | callee may accept *args/**kwargs (FP candidate) |
| 23 | requests | unused | FP | conf.py:277 | Variable 'man_pages' is assigned but never used | 'man_pages' used elsewhere in file |
| 24 | requests | unused | TP | server.py:88 | Function '_close_server_sock_ignore_errors' is defined but never called | '_close_server_sock_ignore_errors' no references found (TP candidate) |
| 25 | requests | security | TP | test_requests.py:1550 | Using pickle.loads() can execute arbitrary code | security finding (TP candidate) |
| 26 | flask | unused | TP | test_user_error_handler.py:194 | Function 'catchall_forbidden_handler' is defined but never called | 'catchall_forbidden_handler' no references found (TP candidate) |
| 27 | flask | dead_code | TP | test_basic.py:1755 | Block for_bar_foo_entry is unreachable | unreachable code (TP candidate) |
| 28 | flask | dead_code | TP | cli.py:692 | Block _path_is_ancestor_entry is unreachable | unreachable code (TP candidate) |
| 29 | requests | undefined_variable | TP | cookies.py:325 | Variable 'iter' may be used before definition | 'iter' possibly undefined (TP candidate) |
| 30 | flask | unused | FP | test_blueprints.py:1063 | Function 'test_unique_blueprint_names' is defined but never called | 'test_unique_blueprint_names' is a pytest test function |
| 31 | flask | arg_count_mismatch | FP | test_cli.py:489 | Function 'invoke' expects 3 args, got 1 | callee may accept *args/**kwargs (FP candidate) |
| 32 | flask | unused | FP | test_factory.py:10 | Function 'test_hello' is defined but never called | 'test_hello' is a pytest test function |
| 33 | requests | dead_code | TP | utils.py:1088 | Block check_header_validity_entry is unreachable | unreachable code (TP candidate) |
| 34 | flask | undefined_variable | TP | ctx.py:260 | Variable 'exc_value' may be used before definition | 'exc_value' possibly undefined (TP candidate) |
| 35 | flask | other | TP | test_user_error_handler.py:163 | Function 'test_default_error_handler' has 52 lines (consider splitting) | other (TP candidate) |
| 36 | flask | dead_code | TP | scaffold.py:345 | Block route_entry is unreachable | unreachable code (TP candidate) |
| 37 | requests | unused | TP | adapters.py:269 | Function 'proxy_manager_for' is defined but never called | 'proxy_manager_for' no references found (TP candidate) |
| 38 | flask | unused | TP | tag.py:169 | Function 'to_python' is defined but never called | 'to_python' no references found (TP candidate) |
| 39 | requests | undefined_variable | TP | models.py:108 | Variable 'result' may be used before definition | 'result' possibly undefined (TP candidate) |
| 40 | requests | security | TP | test_utils.py:443 | Hardcoded secret detected | security finding (TP candidate) |
| 41 | requests | undefined_variable | TP | models.py:732 | Variable 'chunk_size' may be used before definition | 'chunk_size' possibly undefined (TP candidate) |
| 42 | flask | unused | TP | test_views.py:266 | Function 'dispatch_request' is defined but never called | 'dispatch_request' no references found (TP candidate) |
| 43 | flask | unused | FP | test_blog.py:57 | Function 'test_update' is defined but never called | 'test_update' is a pytest test function |
| 44 | flask | security | TP | config.py:209 | Use of dangerous function 'compile' | security finding (TP candidate) |
| 45 | requests | undefined_variable | TP | test_requests.py:2760 | Variable 'expected' may be used before definition | 'expected' possibly undefined (TP candidate) |
| 46 | requests | undefined_variable | TP | test_requests.py:84 | Variable 'd2' may be used before definition | 'd2' possibly undefined (TP candidate) |
| 47 | requests | security | TP | test_requests.py:1623 | Using pickle.loads() can execute arbitrary code | security finding (TP candidate) |
| 48 | requests | undefined_variable | TP | adapters.py:158 | Variable 'timeout' may be used before definition | 'timeout' possibly undefined (TP candidate) |
| 49 | requests | arg_count_mismatch | FP | cookies.py:617 | Function 'cookiejar_from_dict' expects 3 args, got 1 | callee may accept *args/**kwargs (FP candidate) |
| 50 | flask | unused | FP | test_cli.py:603 | Function 'test_run_cert_adhoc' is defined but never called | 'test_run_cert_adhoc' is a pytest test function |
