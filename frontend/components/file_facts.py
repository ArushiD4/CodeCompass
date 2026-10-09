"""file_facts.py — Pure AST fact extraction from Python source code."""
import ast


def extract_facts(source: str, rel_path: str = "", project_modules: set | None = None) -> dict:
    empty = {
        "imports": [], "classes": [], "functions": [],
        "entry_point": False, "io_calls": [], "globals": [],
        "parse_error": None
    }
    project_modules = project_modules or set()
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        empty["parse_error"] = f"Syntax error at line {exc.lineno}: {exc.msg}"
        return empty
    except (ValueError, RecursionError) as exc:
        empty["parse_error"] = str(exc)
        return empty

    imports = []
    classes = []
    functions = []
    entry_point = False
    io_calls = []
    globals_list = []

    # Imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                kind = "local" if top in project_modules else "external"
                imports.append((alias.name, kind))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            top = mod.split(".")[0]
            is_local = (node.level > 0) or (top in project_modules)
            kind = "local" if is_local else "external"
            for alias in node.names:
                name = f"{mod}.{alias.name}" if mod and alias.name != "*" else (mod or alias.name)
                imports.append((name, kind))

    # Top-level functions, classes, globals
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            methods = sum(1 for b in node.body if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)))
            classes.append((node.name, methods))
        elif isinstance(node, ast.Assign):
            kind = _val_kind(node.value)
            for t in node.targets:
                if isinstance(t, ast.Name):
                    globals_list.append((t.id, kind))
        elif isinstance(node, ast.AnnAssign):
            kind = _val_kind(node.value)
            if isinstance(node.target, ast.Name):
                globals_list.append((node.target.id, kind))

    # Entry point & IO calls
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and _is_main_check(node.test):
            entry_point = True
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
            io_calls.append(_describe_open(node))

    return {
        "imports": imports, "classes": classes, "functions": functions,
        "entry_point": entry_point, "io_calls": io_calls,
        "globals": globals_list, "parse_error": None
    }


def _val_kind(val_node) -> str:
    if val_node is None:
        return "other"
    if isinstance(val_node, ast.List):
        return "list"
    if isinstance(val_node, ast.Dict):
        return "dict"
    if isinstance(val_node, ast.Set):
        return "set"
    if isinstance(val_node, ast.Constant):
        return "constant"
    return "other"


def _is_main_check(test_node) -> bool:
    if not isinstance(test_node, ast.Compare):
        return False
    left = test_node.left
    comps = test_node.comparators
    if isinstance(left, ast.Name) and left.id == "__name__":
        for c in comps:
            if isinstance(c, ast.Constant) and c.value == "__main__":
                return True
    for c in comps:
        if isinstance(c, ast.Name) and c.id == "__name__":
            if isinstance(left, ast.Constant) and left.value == "__main__":
                return True
    return False


def _describe_open(call_node: ast.Call) -> str:
    path = "dynamic path"
    if call_node.args and isinstance(call_node.args[0], ast.Constant) and isinstance(call_node.args[0].value, str):
        path = call_node.args[0].value
    mode = "r"
    if len(call_node.args) >= 2 and isinstance(call_node.args[1], ast.Constant) and isinstance(call_node.args[1].value, str):
        mode = call_node.args[1].value
    for kw in call_node.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
            mode = kw.value.value
    if "w" in mode or "x" in mode:
        action = "writes"
    elif "a" in mode:
        action = "appends"
    else:
        action = "reads"
    return f"{action} ({path})"
