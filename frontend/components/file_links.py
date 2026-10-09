"""file_links.py — Pure cross-file called_by, calls_into, and dependents queries."""
from pathlib import Path
from components.graph_data import resolve_edges_detailed


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def calls_into(target_file: str, graph: dict) -> list:
    nodes, edges = resolve_edges_detailed(graph)
    target = _norm(target_file)
    results = {}
    for src, dst, possible in edges:
        s_node, d_node = nodes.get(src), nodes.get(dst)
        if not s_node or not d_node:
            continue
        s_file = _norm(s_node.get("file"))
        d_file = _norm(d_node.get("file"))
        if s_file == target and d_file != target:
            func = d_node.get("label", "")
            key = (d_file, func)
            if key not in results or not possible:
                results[key] = possible
    return sorted([(f, fn, p) for (f, fn), p in results.items()])


def called_by(target_file: str, graph: dict) -> list:
    nodes, edges = resolve_edges_detailed(graph)
    target = _norm(target_file)
    results = {}
    for src, dst, possible in edges:
        s_node, d_node = nodes.get(src), nodes.get(dst)
        if not s_node or not d_node:
            continue
        s_file = _norm(s_node.get("file"))
        d_file = _norm(d_node.get("file"))
        if d_file == target and s_file != target:
            func = s_node.get("label", "")
            key = (s_file, func)
            if key not in results or not possible:
                results[key] = possible
    return sorted([(f, fn, p) for (f, fn), p in results.items()])


def dependents(target_file: str, file_facts: dict, graph: dict) -> list:
    target = _norm(target_file)
    target_stem = Path(target).stem.lower()
    deps = set()

    # 1. Callers
    for other_file, _, _ in called_by(target, graph):
        deps.add(other_file)

    # 2. Importers
    for fpath, facts in (file_facts or {}).items():
        norm_f = _norm(fpath)
        if norm_f == target:
            continue
        for imp_name, kind in facts.get("imports", []):
            top_mod = imp_name.split(".")[0].lower()
            if top_mod == target_stem:
                deps.add(norm_f)
                break

    return sorted(deps)
