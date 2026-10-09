"""api_client.py — REST API Client layer."""
import os
from concurrent.futures import ThreadPoolExecutor
import requests
import streamlit as st

FAST, SCAN = 5, 180


def _base():
    return st.session_state["backend_url"].rstrip("/")


def _api_key() -> str:
    env_key = os.getenv("CODECOMPASS_API_KEY", "")
    if env_key:
        return env_key
    try:
        secret_key = st.secrets.get("CODECOMPASS_API_KEY", "")
        if secret_key:
            return secret_key
    except Exception:
        pass
    return "pink-clounding"


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
    headers = kwargs.pop("headers", {})
    key = _api_key()
    if key:
        headers["X-API-Key"] = key
    try:
        resp = requests.request(method, _base() + path, timeout=timeout, headers=headers, **kwargs)
    except requests.ConnectionError:
        return None, f"Cannot reach the backend at {_base()}. Start it with: uvicorn main:app --port 8000"
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


def run_audit(project_name, directory_path):
    params = {"project_name": project_name, "directory_path": directory_path}
    return _call("POST", "/api/audit", SCAN, params=params)


def get_project(project_id):
    return _call("GET", f"/api/projects/{int(project_id)}")


def get_graph(directory_path):
    data, err = _call("GET", "/api/graph", SCAN, params={"directory_path": directory_path})
    return (data or {}).get("graph"), err


def discover_projects(fetch, batch=25, workers=8, limit=500):
    projects = []
    current_id = 1
    with ThreadPoolExecutor(max_workers=workers) as executor:
        while current_id <= limit:
            batch_ids = list(range(current_id, min(current_id + batch, limit + 1)))
            if not batch_ids:
                break
            results = list(executor.map(fetch, batch_ids))
            batch_successes = []
            for proj, fatal_err in results:
                if fatal_err:
                    return [], fatal_err
                if proj:
                    batch_successes.append(proj)
            if not batch_successes:
                break
            projects.extend(batch_successes)
            current_id += batch

    projects.sort(key=lambda p: (str(p.get("created_at") or ""), int(p.get("id") or 0)), reverse=True)
    return projects, None


@st.cache_data(ttl=15)
def list_projects(base_url):
    key = _api_key()
    headers = {"X-API-Key": key} if key else {}

    def fetch(pid):
        try:
            r = requests.get(f"{base_url.rstrip('/')}/api/projects/{pid}", headers=headers, timeout=FAST)
            if r.status_code == 200:
                data = r.json()
                return data.get("project", data), None
            if r.status_code == 404:
                return None, None
            if r.status_code >= 500:
                return None, f"Backend returned HTTP {r.status_code}."
            if r.status_code in (401, 403):
                return None, "Backend authentication failed: invalid or missing API key."
            return None, f"Backend returned HTTP {r.status_code}."
        except requests.ConnectionError:
            return None, f"Cannot reach the backend at {base_url}."
        except requests.Timeout:
            return None, "Request timed out."
        except Exception as exc:
            return None, str(exc)

    return discover_projects(fetch)
