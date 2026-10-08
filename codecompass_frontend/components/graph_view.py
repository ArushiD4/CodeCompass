"""Call graph tab: controls, vis.js render via streamlit-agraph, node detail panel."""
import streamlit as st
from components import graph_data
from components.primitives import esc

try:
    from streamlit_agraph import Config, Edge, Node, agraph
except ImportError:  # section 5.3: fall back to a table if the component is missing
    agraph = None

LAYOUTS = ("Hierarchical", "Force-directed")
FONT = {"size": 13, "face": "Inter, sans-serif", "color": "#0E1624"}


def _config(layout, count):
    height = max(460, min(760, 360 + count * 14))
    if layout == "Hierarchical":  # deterministic, left-to-right call flow: no hairball
        cfg = Config(width=700, height=height, directed=True, physics=False, hierarchical=True,
                     direction="LR", sortMethod="directed", levelSeparation=240, nodeSpacing=95,
                     treeSpacing=120, blockShifting=True, edgeMinimization=True)
        smooth = {"type": "cubicBezier", "forceDirection": "horizontal", "roundness": 0.45}
    else:  # ForceAtlas2 with strong repulsion + collision avoidance, frozen once settled
        cfg = Config(width=700, height=height, directed=True, physics=True, hierarchical=False,
                     solver="forceAtlas2Based", minVelocity=0.75, maxVelocity=40)
        cfg.physics["forceAtlas2Based"] = {"gravitationalConstant": -140, "centralGravity": 0.012,
                                           "springLength": 170, "springConstant": 0.05,
                                           "damping": 0.6, "avoidOverlap": 1}
        cfg.physics["stabilization"] = {"enabled": True, "iterations": 350, "fit": True}
        smooth = {"type": "continuous"}
    cfg.width = "100%"
    cfg.nodes = {"borderWidth": 1.5, "borderWidthSelected": 3}
    cfg.edges = {"smooth": smooth, "width": 1.2, "selectionWidth": 2.5,
                 "color": {"color": "#B8C0CC", "highlight": "#2B50E6", "hover": "#2B50E6"}}
    cfg.interaction = {"hover": True, "hoverConnectedEdges": True, "selectConnectedEdges": True,
                       "multiselect": False, "tooltipDelay": 150}
    return cfg


def _nodes(model):
    nodes = []
    for n in model["nodes"]:
        node = Node(id=n["id"], label=n["label"], size=14 + min(n["degree"], 8) * 3, shape="dot",
                    color={"background": n["color"], "border": "#FFFFFF",
                           "highlight": {"background": n["color"], "border": "#0E1624"}}, font=FONT)
        node.title = None  # agraph opens a node's title as a URL on double-click
        nodes.append(node)
    return nodes


def _detail(model, selected):
    node = next((n for n in model["nodes"] if n["id"] == selected), None)
    if not node:
        return '<p class="cc-muted">Click a function to see who calls it and what it calls.</p>'
    label = {n["id"]: n["label"] for n in model["nodes"]}
    callers = sorted(label[s] for s, d in model["edges"] if d == node["id"])
    callees = sorted(label[d] for s, d in model["edges"] if s == node["id"])
    join = lambda names: esc(", ".join(names)) if names else "none"
    return (f'<p class="cc-h2">{esc(node["label"])}()</p><p class="cc-mono">{esc(node["file"])}:{node["line"]}</p>'
            f'<p class="cc-muted"><b>Called by</b> {join(callers)}</p>'
            f'<p class="cc-muted"><b>Calls</b> {join(callees)}</p>')


def _legend(model):
    rows = "".join(f'<li style="color:{c}"><span class="cc-dot"></span>'
                   f'<span class="cc-mono">{esc(m)}</span></li>' for m, c in model["colors"].items())
    return f'<ul class="cc-legend" style="flex-direction:column;gap:.4rem">{rows}</ul>'


def render():
    ss = st.session_state
    graph = ss.get("graph_data")
    if not graph:
        st.info(ss.get("graph_error") or "Run an audit to build the call graph for that directory.")
        return
    c1, c2, c3 = st.columns([2, 3, 2], vertical_alignment="center")
    layout = c1.segmented_control("Layout", LAYOUTS, default=LAYOUTS[0], key="graph_layout",
                                  label_visibility="collapsed") or LAYOUTS[0]
    top_k = c2.slider("Most connected functions", 5, 80, 30, key="graph_topk")
    hide = c3.toggle("Hide isolated functions", value=True, key="graph_hide")
    model = graph_data.shape(graph, top_k, hide)
    if not model["nodes"]:
        st.info("No function-to-function calls were found in this project.")
        return
    left, right = st.columns([7, 3])
    with left:
        if agraph is None:
            st.dataframe([{k: n[k] for k in ("label", "file", "line", "in", "out")} for n in model["nodes"]])
            selected = None
        else:
            edges = [Edge(source=s, target=d, arrows="to", color="#B8C0CC", width=1.2) for s, d in model["edges"]]
            selected = agraph(nodes=_nodes(model), edges=edges, config=_config(layout, len(model["nodes"])))
    with right:
        st.html(f'<div class="cc-card"><p class="cc-muted">Showing {len(model["nodes"])} of {model["total"]} '
                f'functions, {len(model["edges"])} calls. Scroll to zoom, drag to pan.</p>'
                f'<hr style="border:0;border-top:1px solid var(--line);margin:.9rem 0">{_detail(model, selected)}'
                f'<hr style="border:0;border-top:1px solid var(--line);margin:.9rem 0">{_legend(model)}</div>')
