"""entrypoints.py — Decorator for Streamlit callbacks and dispatch functions."""


def entrypoint(func=None):
    """Marks functions invoked by Streamlit callbacks, route dispatch or worker pools, which static AST analysis cannot trace."""
    if func is None:
        return lambda f: f
    return func
