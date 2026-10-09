"""
api_client.py — REST API Client layer.

Manages all HTTP communication with the FastAPI backend. Abstracts network errors,
JSON parsing, and authentication headers, ensuring the UI layer only ever receives 
clean data payloads or user-friendly error strings.

Contracts defined in ARCHITECTURE.md section 6.
"""
import requests
import streamlit as st

FAST, SCAN = 5, 180  # timeouts in seconds


def _base():
    return st.session_state["backend_url"].rstrip("/")


# Fix 1: Load the API key from Streamlit secrets (frontend/.streamlit/secrets.toml).
# Falls back gracefully if the file is missing or the key is not set, which keeps
# the app functional in environments where the backend key guard is not activated.
def _api_key() -> str:
    try:
        return st.secrets.get("CODECOMPASS_API_KEY", "")
    except FileNotFoundError:
        return ""


def _explain(resp):
    try:
        detail = resp.json().get("detail")
    except ValueError:
        detail = None
    if resp.status_code == 401:
        return "Backend rejected the request: invalid or missing API key (X-API-Key)."
    if resp.status_code == 422:
        return "The backend rejected the request: a required parameter is missing."
    return detail if isinstance(detail, str) else f"Backend returned HTTP {resp.status_code}."


def _call(method, path, timeout=FAST, **kwargs):
    # Fix 1: inject the API key header into every outbound request.
    # If the key is empty the header is omitted, matching the backend's permissive mode.
    headers = kwargs.pop("headers", {})
    key = _api_key()
    if key:
        headers["X-API-Key"] = key

    try:
        resp = requests.request(method, _base() + path, timeout=timeout, headers=headers, **kwargs)
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
    """
    GET / (section 6.1) — Backend health check.
    
    Verifies backend connectivity. The result is cached for 10 seconds to 
    prevent UI lag during rapid Streamlit script reruns.
    
    Returns:
        bool: True if the backend responds with HTTP 200, False otherwise.
    """
    return _ping(_base())


def run_audit(project_name, directory_path):
    """
    POST /api/audit (6.2) — Executes a full AST static analysis scan.
    
    Args:
        project_name (str): Arbitrary name assigned to this audit run.
        directory_path (str): The local file system path to the target codebase.
        
    Returns:
        tuple: (dict_of_results, error_message_string)
    """
    params = {"project_name": project_name, "directory_path": directory_path}
    return _call("POST", "/api/audit", SCAN, params=params)


def get_project(project_id):
    """
    GET /api/projects/{id} (6.3) — Retrieves a historical audit report.
    
    Args:
        project_id (int): The database primary key of the project.
        
    Returns:
        tuple: (dict_of_report_data, error_message_string)
    """
    return _call("GET", f"/api/projects/{int(project_id)}")


def get_graph(directory_path):
    """
    GET /api/graph (6.4) — Retrieves call-graph nodes and edges for visualisation.
    
    Args:
        directory_path (str): The local file system path to the target codebase.
        
    Returns:
        tuple: (dict_of_graph_data, error_message_string)
    """
    data, err = _call("GET", "/api/graph", SCAN, params={"directory_path": directory_path})
    return (data or {}).get("graph"), err
