"""Call graph tab: controls, dark vis.js constellation via streamlit-agraph."""
import streamlit as st
from components import graph_data
from components.primitives import esc

try:
    from streamlit_agraph import Config, Edge, Node, agraph
except ImportError:
    agraph = None

LAYOUTS = ("Hierarchical", "Force-directed")
FONT = {"size": 12, "face": "Plus Jakarta Sans, sans-serif", "color": "#E6EBF2"}


def _config(layout, count):
    height = max(480, min(760, 380 + count * 14))
    if layout == "Hierarchical":
        cfg = Config(width="100%", height=height, directed=True, physics=False, hierarchical=True,
                     direction="LR", sortMethod="directed", levelSeparation=240, nodeSpacing=95,
                     treeSpacing=120, blockShifting=True, edgeMinimization=True)
        smooth = {"type": "cubicBezier", "forceDirection": "horizontal", "roundness": 0.45}
    else:
        cfg = Config(width="100%", height=height, directed=True, physics=True, hierarchical=False,
                     solver="forceAtlas2Based", minVelocity=0.75, maxVelocity=40)
        cfg.physics["forceAtlas2Based"] = {"gravitationalConstant": -140, "centralGravity": 0.012,
                                           "springLength": 170, "springConstant": 0.05,
                                           "damping": 0.6, "avoidOverlap": 1}
        cfg.physics["stabilization"] = {"enabled": True, "iterations": 350, "fit": True}
        smooth = {"type": "continuous"}
    cfg.nodes = {"borderWidth": 0, "borderWidthSelected": 2}
    cfg.edges = {"smooth": smooth, "width": 1.2, "selectionWidth": 2.5,
                 "color": {"color": "#3A4556", "highlight": "#00F5A0", "hover": "#00F5A0"}}
    cfg.interaction = {"hover": True, "hoverConnectedEdges": True, "selectConnectedEdges": True,
                       "multiselect": False, "tooltipDelay": 150}
    return cfg


def _nodes(model, selected=None):
    nodes = []
    neighbors = set()
    if selected:
        neighbors = {s for s, d in model["edges"] if d == selected} | {d for s, d in model["edges"] if s == selected} | {selected}
    for n in model["nodes"]:
        bg = n["color"] if (not selected or n["id"] in neighbors) else "#1A2232"
        lbl_col = "#E6EBF2" if (not selected or n["id"] in neighbors) else "#505C72"
        node = Node(id=n["id"], label=n["label"], size=13 + min(n["degree"], 8) * 3, shape="dot",
                    color={"background": bg, "border": "transparent",
                           "highlight": {"background": "#00F5A0", "border": "#FFFFFF"}},
                    font={**FONT, "color": lbl_col})
        node.title = None
        nodes.append(node)
    return nodes


def _detail(model, selected):
    node = next((n for n in model["nodes"] if n["id"] == selected), None)
    if not node:
        return '<p class="cc-muted">Click a function node to isolate its callers and callees.</p>'
    label = {n["id"]: n["label"] for n in model["nodes"]}
    callers = sorted(label[s] for s, d in model["edges"] if d == node["id"])
    callees = sorted(label[d] for s, d in model["edges"] if s == node["id"])
    join = lambda names: esc(", ".join(names)) if names else "none"
    return (f'<p class="cc-h2" style="color:var(--brand)">{esc(node["label"])}()</p>'
            f'<p class="cc-mono">{esc(node["file"])}:{node["line"]}</p>'
            f'<p class="cc-muted" style="margin-top:.5rem"><b>Called by</b> {join(callers)}</p>'
            f'<p class="cc-muted"><b>Calls</b> {join(callees)}</p>')


def _legend(model):
    rows = "".join(f'<li style="color:{c}"><span class="cc-dot"></span>'
                   f'<span class="cc-mono">{esc(m)}</span></li>' for m, c in model["colors"].items())
    return f'<ul class="cc-legend" style="flex-direction:column;gap:.45rem">{rows}</ul>'


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
            edges = [Edge(source=s, target=d, arrows="to", color="#3A4556", width=1.2) for s, d in model["edges"]]
            selected = agraph(nodes=_nodes(model, ss.get("graph_selected")), edges=edges, config=_config(layout, len(model["nodes"])))
            if selected != ss.get("graph_selected"):
                ss["graph_selected"] = selected
    with right:
        st.html(f'<div class="cc-card"><p class="cc-muted">Showing {len(model["nodes"])} of {model["total"]} '
                f'functions, {len(model["edges"])} calls.</p>'
                f'<hr style="border:0;border-top:1px solid var(--line);margin:.75rem 0">{_detail(model, ss.get("graph_selected"))}'
                f'<hr style="border:0;border-top:1px solid var(--line);margin:.75rem 0">{_legend(model)}</div>')
