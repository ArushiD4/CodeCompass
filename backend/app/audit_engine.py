import ast
import os
from typing import List, Dict, Any, Set

# Fix 2: Maximum file size allowed before the AST parser is invoked.
# Files larger than this are skipped with an INFO finding rather than
# potentially exhausting server memory or blowing the recursion stack.
MAX_FILE_BYTES = 512_000  # 500 KB


class StaticAntiPatternAuditor(ast.NodeVisitor):
    """
    Traverses Python AST nodes to identify code anti-patterns, security risks,
    and anti-best practices, attaching student viva defense guidance to each finding.
    """

    def __init__(self, file_path: str, ignored_lines: frozenset):
        self.file_path = file_path
        self.ignored_lines = ignored_lines   # Fix 3: per-line suppression set
        self.issues: List[Dict[str, Any]] = []
        self.functions_defined: Set[str] = set()
        self.functions_called: Set[str] = set()

    # ------------------------------------------------------------------
    # Fix 4: helper — extract decorator names from a function definition
    # ------------------------------------------------------------------
    def _decorator_names(self, node) -> List[str]:
        """
        Return the flat name of every decorator attached to *node*.
        Handles three forms:
          @plain_name          → ast.Name        → plain_name
          @obj.method          → ast.Attribute   → method
          @obj.method(args)    → ast.Call        → method
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

    # ------------------------------------------------------------------
    # Visitor rules
    # ------------------------------------------------------------------

    def visit_Assign(self, node: ast.Assign):
        """
        Rule 1: Detect Hardcoded Credentials & Plaintext Secrets.
        Flags variables matching key/secret/password assigned to hardcoded string literals.
        """
        # Fix 3: honour compass:ignore on this line
        if node.lineno not in self.ignored_lines:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id.upper()
                    secret_keywords = ["KEY", "SECRET", "PASSWORD", "TOKEN", "AUTH", "PASS", "CREDENTIAL"]

                    if any(keyword in var_name for keyword in secret_keywords):
                        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                            self.issues.append({
                                "rule_name": "Hardcoded Credential",
                                "severity": "CRITICAL",
                                "file_path": self.file_path,
                                "line_number": node.lineno,
                                "viva_tip": (
                                    f"Variable '{target.id}' assigns a plain text secret directly in code. "
                                    "During a viva defense, explain that sensitive credentials should always be loaded "
                                    "dynamically from environment variables (`os.getenv`) or `.env` files to prevent "
                                    "exposure in version control."
                                )
                            })
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """
        Rule 2: Detect Resource Leaks (Unclosed File Handles) & Dangerous Call Executions.
        Tracks function calls for call-graphing and flags unmanaged file operations.
        """
        callee_name = None
        if isinstance(node.func, ast.Name):
            callee_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            callee_name = node.func.attr

        if callee_name:
            self.functions_called.add(callee_name)

            # Fix 3: only generate findings on non-ignored lines
            if node.lineno not in self.ignored_lines:
                if callee_name == "open":
                    self.issues.append({
                        "rule_name": "Unclosed Resource Handle",
                        "severity": "WARNING",
                        "file_path": self.file_path,
                        "line_number": node.lineno,
                        "viva_tip": (
                            "Opening files using standalone `open()` can leak file descriptors if an unhandled "
                            "exception occurs before `.close()`. Defend your code by explaining Python's Context "
                            "Managers (`with open(...) as f:`), which guarantee cleanup."
                        )
                    })
                elif callee_name in ["eval", "exec"]:
                    self.issues.append({
                        "rule_name": "Dynamic Code Injection Risk",
                        "severity": "CRITICAL",
                        "file_path": self.file_path,
                        "line_number": node.lineno,
                        "viva_tip": (
                            f"Using `{callee_name}()` enables arbitrary code execution vulnerabilities. "
                            "Tell the examiner that dynamic evaluation should be replaced with safe parsing "
                            "libraries like `ast.literal_eval`."
                        )
                    })

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Track defined functions for dead-code detection.
        Fix 4: if a function carries any decorator, the decorator is acting as
        its caller — add the function name to functions_called so it is never
        classified as an orphaned/dead function.
        """
        self.functions_defined.add(node.name)
        if self._decorator_names(node):
            # At least one decorator exists → the function is reachable via the framework
            self.functions_called.add(node.name)
        self.generic_visit(node)

    # Treat async defs identically to sync defs
    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        """
        Rule 3: Detect Silent Exception Swallowing (`except: pass`).
        """
        # Fix 3: honour compass:ignore on this line
        if node.lineno not in self.ignored_lines:
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                self.issues.append({
                    "rule_name": "Silent Exception Swallowing",
                    "severity": "CRITICAL",
                    "file_path": self.file_path,
                    "line_number": node.lineno,
                    "viva_tip": (
                        "Catching errors with `except: pass` silently suppresses runtime bugs and hinders debugging. "
                        "In an exam, explain that you should catch specific exceptions (e.g., `ValueError`) and log "
                        "errors or re-raise custom exceptions."
                    )
                })
        self.generic_visit(node)


def audit_codebase(directory_path: str) -> Dict[str, Any]:
    """
    Main entry point for auditing a directory of Python code.
    Traverses files, builds metrics, detects anti-patterns, and calculates
    the Code Readiness Score (CRS).
    """
    all_issues: List[Dict[str, Any]] = []
    total_files = 0
    total_lines = 0
    all_defined_functions: Set[str] = set()
    all_called_functions: Set[str] = set()

    for root, dirs, files in os.walk(directory_path):
        # Exclude virtual environments, VCS, and cache directories
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "venv", ".venv", "ccenv", "env"}]
        for file in files:
            if not file.endswith(".py"):
                continue

            total_files += 1
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, directory_path)

            # ----------------------------------------------------------
            # Fix 2: Pre-flight file size guard
            # ----------------------------------------------------------
            try:
                file_size = os.path.getsize(full_path)
            except OSError:
                file_size = 0

            if file_size > MAX_FILE_BYTES:
                all_issues.append({
                    "rule_name": "File Too Large",
                    "severity": "INFO",
                    "file_path": rel_path,
                    "line_number": 1,
                    "viva_tip": (
                        f"File exceeds the 500 KB analysis limit ({file_size // 1024} KB) and was skipped. "
                        "Consider splitting large files into smaller, single-responsibility modules."
                    )
                })
                continue

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    code = f.read()

                lines = code.splitlines()
                total_lines += len(lines)

                # Fix 3: Build the suppression set for this file.
                # Any line containing the literal text "# compass:ignore" (case-sensitive)
                # is added; findings whose line_number is in this set are silently dropped.
                ignored_lines = frozenset(
                    i + 1 for i, line in enumerate(lines) if "# compass:ignore" in line
                )

                tree = ast.parse(code, filename=rel_path)
                auditor = StaticAntiPatternAuditor(rel_path, ignored_lines)
                auditor.visit(tree)

                all_issues.extend(auditor.issues)
                all_defined_functions.update(auditor.functions_defined)
                all_called_functions.update(auditor.functions_called)

            except SyntaxError as e:
                all_issues.append({
                    "rule_name": "Syntax Error",
                    "severity": "CRITICAL",
                    "file_path": rel_path,
                    "line_number": e.lineno or 1,
                    "viva_tip": (
                        f"Syntax error detected: '{e.msg}'. "
                        "Codebases with syntax errors fail compilation/parsing completely. "
                        "Fix syntax errors before presenting code in a viva."
                    )
                })
            except RecursionError:
                # Fix 2: catch pathologically nested files that pass the size check
                all_issues.append({
                    "rule_name": "File Too Complex",
                    "severity": "INFO",
                    "file_path": rel_path,
                    "line_number": 1,
                    "viva_tip": (
                        "File has excessive nesting depth and could not be fully analysed. "
                        "Simplify deeply nested structures to improve readability and maintainability."
                    )
                })
            except Exception as e:
                all_issues.append({
                    "rule_name": "File Read Error",
                    "severity": "WARNING",
                    "file_path": rel_path,
                    "line_number": 1,
                    "viva_tip": f"Failed to read file due to error: {str(e)}"
                })

    # ------------------------------------------------------------------
    # Rule 4: Detect Dead / Orphaned Functions (post-traversal)
    # Standard Python entry points and dunder methods are excluded.
    # Fix 4: decorated functions are already in all_called_functions, so
    # framework route handlers like read_root() will never appear here.
    # ------------------------------------------------------------------
    ignored_functions = {"main", "__init__", "read_root", "get_db", "run_audit"}
    orphaned_functions = all_defined_functions - all_called_functions - ignored_functions

    for func_name in orphaned_functions:
        all_issues.append({
            "rule_name": "Orphaned Function",
            "severity": "INFO",
            "file_path": "Global Codebase",
            "line_number": 0,
            "viva_tip": (
                f"Function `{func_name}()` is defined but never invoked in the execution path. "
                "Be ready to explain to the evaluator whether this is dead code or intended for "
                "future modular extension."
            )
        })

    # ------------------------------------------------------------------
    # Calculate Code Readiness Score (CRS)
    # Base = 100 pts  |  CRITICAL −15  |  WARNING −8  |  INFO −3
    # ------------------------------------------------------------------
    deductions = 0
    for issue in all_issues:
        if issue["severity"] == "CRITICAL":
            deductions += 15
        elif issue["severity"] == "WARNING":
            deductions += 8
        elif issue["severity"] == "INFO":
            deductions += 3

    crs_score = max(0, 100 - deductions)

    return {
        "crs_score": crs_score,
        "total_files": total_files,
        "total_lines": total_lines,
        "total_functions": len(all_defined_functions),
        "issues": all_issues
    }