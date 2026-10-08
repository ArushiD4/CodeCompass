"""REST client for the FastAPI backend. Contracts: ARCHITECTURE.md section 6.

Every call returns (data, error). The UI never sees an exception.
"""
import requests
import streamlit as st

FAST, SCAN = 5, 180  # timeouts in seconds


def _base():
    return st.session_state["backend_url"].rstrip("/")


def _explain(resp):
    try:
        detail = resp.json().get("detail")
    except ValueError:
        detail = None
    if resp.status_code == 422:
        return "The backend rejected the request: a required parameter is missing."
    return detail if isinstance(detail, str) else f"Backend returned HTTP {resp.status_code}."


def _call(method, path, timeout=FAST, **kwargs):
    try:
        resp = requests.request(method, _base() + path, timeout=timeout, **kwargs)
    except requests.ConnectionError:
        return None, (f"Cannot reach the backend at {_base()}. "
                      "Start it with: uvicorn main:app --port 8000")
    except requests.Timeout:
        return None, "The backend took too long to answer. Try a smaller directory."
    except requests.RequestException as exc:
        return None, str(exc)
    if resp.status_code != 200:
        return None, _explain(resp)
    try:
        return resp.json(), None
    except ValueError:
        return None, "The backend returned a response that is not valid JSON."


@st.cache_data(ttl=10, show_spinner=False)
def _ping(base):
    try:
        return requests.get(base + "/", timeout=2).status_code == 200
    except requests.RequestException:
        return False


def health():
    """GET / (section 6.1), cached for 10 s so reruns stay fast."""
    return _ping(_base())


def run_audit(project_name, directory_path):
    """POST /api/audit (6.2). Parameters travel in the query string."""
    params = {"project_name": project_name, "directory_path": directory_path}
    return _call("POST", "/api/audit", SCAN, params=params)


def get_project(project_id):
    """GET /api/projects/{id} (6.3)."""
    return _call("GET", f"/api/projects/{int(project_id)}")


def get_graph(directory_path):
    """GET /api/graph (6.4). Returns the inner graph object."""
    data, err = _call("GET", "/api/graph", SCAN, params={"directory_path": directory_path})
    return (data or {}).get("graph"), err
