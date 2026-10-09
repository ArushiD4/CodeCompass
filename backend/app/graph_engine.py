import ast
import os
from typing import Dict, List, Any

# Fix 2: Pre-flight file size guard — mirrors the same constant in audit_engine.py.
MAX_FILE_BYTES = 512_000  # 500 KB


class CallGraphVisitor(ast.NodeVisitor):
    """
    AST Visitor that maps function definitions and function calls.
    
    This visitor records defined functions as 'nodes' and function invocations as 'edges',
    constructing a structured call graph of the parsed source file. It also resolves
    decorators into synthetic edges to correctly link framework-driven code (like route handlers).
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.current_function = None
        self.functions = []   # Nodes
        self.calls = []       # Edges

    # ------------------------------------------------------------------
    # Fix 4: helper — extract decorator names from a function definition
    # ------------------------------------------------------------------
    def _decorator_names(self, node: ast.FunctionDef) -> List[str]:
        """
        Extracts and returns the flat names of every decorator attached to the given node.
        
        Handles three common decorator forms:
          - @plain_name          -> ast.Name        -> 'plain_name'
          - @obj.method          -> ast.Attribute   -> 'method'
          - @obj.method(args)    -> ast.Call        -> 'method'
          
        Args:
            node (ast.FunctionDef): The AST node representing the function definition.
            
        Returns:
            List[str]: A list containing the string names of the decorators.
        """
        names = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                names.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                names.append(dec.attr)
            elif isinstance(dec, ast.Call):
                inner = dec.func
                if isinstance(inner, ast.Name):
                    names.append(inner.id)
                elif isinstance(inner, ast.Attribute):
                    names.append(inner.attr)
        return names

    def visit_FunctionDef(self, node: ast.FunctionDef):
        previous_function = self.current_function
        self.current_function = node.name

        # Record the function as a graph node
        self.functions.append({
            "id": f"{self.file_path}::{node.name}",
            "label": node.name,
            "file": self.file_path,
            "line": node.lineno
        })

        # Fix 4: create a synthetic edge for each decorator so that
        # framework route handlers appear connected in the call graph
        # rather than floating as isolated nodes.
        # Edge direction: decorator → function  (the decorator "invokes" the function)
        for dec_name in self._decorator_names(node):
            self.calls.append({
                "caller": f"{self.file_path}::{dec_name}",
                "callee": node.name,
                "line": node.lineno
            })

        self.generic_visit(node)
        self.current_function = previous_function

    # Treat async defs identically to sync defs
    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node: ast.Call):
        if self.current_function:
            callee_name = None
            if isinstance(node.func, ast.Name):
                callee_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                callee_name = node.func.attr

            if callee_name:
                self.calls.append({
                    "caller": f"{self.file_path}::{self.current_function}",
                    "callee": callee_name,
                    "line": node.lineno
                })

        self.generic_visit(node)


def generate_codebase_graph(directory_path: str) -> Dict[str, Any]:
    """
    Generates a complete call-graph for all Python files in the given directory.
    
    Recursively scans the directory, parses each valid Python file into an AST, 
    and leverages the `CallGraphVisitor` to build a unified map of all internal
    function definitions and invocations.
    
    Args:
        directory_path (str): The absolute or relative path to the project directory.
        
    Returns:
        Dict[str, Any]: A structured dictionary containing:
            - 'nodes': List of defined functions.
            - 'edges': List of caller-callee relationships.
            - 'total_nodes': Count of nodes.
            - 'total_edges': Count of edges.
    """
    nodes = []
    edges = []

    for root, dirs, files in os.walk(directory_path):
        # Exclude virtual environments, VCS, and cache directories
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "venv", ".venv", "ccenv", "env"}]
        for file in files:
            if not file.endswith(".py"):
                continue

            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, directory_path)

            # Fix 2: Pre-flight file size guard — silently skip oversized files
            try:
                if os.path.getsize(full_path) > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    code = f.read()

                tree = ast.parse(code, filename=rel_path)
                visitor = CallGraphVisitor(rel_path)
                visitor.visit(tree)

                nodes.extend(visitor.functions)
                edges.extend(visitor.calls)

            except (SyntaxError, RecursionError):
                # Fix 2: RecursionError catches pathologically nested files
                continue

    return {
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges)
    }