import ast
import os
from typing import Dict, List, Any

class CallGraphVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.current_function = None
        self.functions = []  # Nodes
        self.calls = []      # Edges

    def visit_FunctionDef(self, node: ast.FunctionDef):
        previous_function = self.current_function
        self.current_function = node.name
        
        # Record node
        self.functions.append({
            "id": f"{self.file_path}::{node.name}",
            "label": node.name,
            "file": self.file_path,
            "line": node.lineno
        })

        self.generic_visit(node)
        self.current_function = previous_function

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
    nodes = []
    edges = []

    for root, dirs, files in os.walk(directory_path):
        # Exclude virtual environments, VCS, and cache directories to avoid scanning library files
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "venv", ".venv", "ccenv", "env"}]
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, directory_path)

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        code = f.read()

                    tree = ast.parse(code, filename=rel_path)
                    visitor = CallGraphVisitor(rel_path)
                    visitor.visit(tree)

                    nodes.extend(visitor.functions)
                    edges.extend(visitor.calls)

                except SyntaxError:
                    continue

    return {
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges)
    }