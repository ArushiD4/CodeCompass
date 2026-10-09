"""Graph shaping, pure Python (no Streamlit). Section 5.3 of ARCHITECTURE.md.

The API returns edges as caller-id -> callee *name*. We resolve each name to
node ids, drop built-ins, count degrees and keep only the top-K hubs.
"""
from collections import defaultdict
from config import BUILTIN_EXCLUDE, MODULE_PALETTE


def module_of(file_path):
    parts = file_path.replace("\\", "/").split("/")
    return "/".join(parts[:-1]) or "(root)"


def resolve_edges_detailed(graph, hide_builtins=True):
    nodes = {n["id"]: n for n in graph.get("nodes", [])}
    by_label = defaultdict(list)
    for node in nodes.values():
        by_label[node["label"]].append(node["id"])
    seen, edges = set(), []
    for edge in graph.get("edges", []):
        src, name = edge["caller"], edge["callee"]
        if src not in nodes or (hide_builtins and name in BUILTIN_EXCLUDE):
            continue
        targets = by_label.get(name, [])
        if not targets:
            continue
        possible = len(targets) > 1
        same_file = [t for t in targets if nodes[t]["file"] == nodes[src]["file"]]
        for dst in same_file or targets:
            if dst != src and (src, dst) not in seen:
                seen.add((src, dst))
                edges.append((src, dst, possible))
    return nodes, edges


def resolve_edges(graph, hide_builtins=True):
    nodes, detailed = resolve_edges_detailed(graph, hide_builtins)
    return nodes, [(s, d) for s, d, _ in detailed]


def shape(graph, top_k, hide_isolated=True):
    nodes, edges = resolve_edges(graph)
    degree = defaultdict(lambda: [0, 0])  # [in, out]
    for src, dst in edges:
        degree[src][1] += 1
        degree[dst][0] += 1
    ids = [i for i in nodes if not (hide_isolated and sum(degree[i]) == 0)]
    ids.sort(key=lambda i: (-sum(degree[i]), nodes[i]["label"]))
    kept = set(ids[:top_k])
    kept_edges = [(s, d) for s, d in edges if s in kept and d in kept]
    modules = sorted({module_of(nodes[i]["file"]) for i in kept})
    colors = {m: MODULE_PALETTE[k % len(MODULE_PALETTE)] for k, m in enumerate(modules)}
    out = []
    for i in ids[:top_k]:
        node, (n_in, n_out) = nodes[i], degree[i]
        mod = module_of(node["file"])
        out.append({**node, "in": n_in, "out": n_out, "degree": n_in + n_out,
                    "module": mod, "color": colors[mod]})
    return {"nodes": out, "edges": kept_edges, "colors": colors,
            "total": len(nodes), "total_edges": len(edges)}
