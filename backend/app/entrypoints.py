"""entrypoints.py — Decorator for framework-invoked entrypoints and AST visitors."""


def entrypoint(func=None):
    """Marks functions invoked by FastAPI dependency injection or ast.NodeVisitor dispatch, which static AST analysis cannot trace."""
    if func is None:
        return lambda f: f
    return func
