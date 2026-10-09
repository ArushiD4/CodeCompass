"""report_picker.py — Previous audits discovery, time formatting, and labels."""
from collections import Counter
from datetime import datetime, timezone
import api_client


def fmt_time(created_at) -> str:
    if not created_at:
        return "Unknown date"
    try:
        dt = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone().strftime("%d %b %Y, %I:%M %p")
    except (ValueError, TypeError):
        return str(created_at)


def report_label(project, duplicates=None) -> str:
    if not isinstance(project, dict):
        return str(project)
    name = project.get("project_name") or "Untitled"
    time_str = fmt_time(project.get("created_at"))
    score = project.get("crs_score", 0)
    base = f"{name} · {time_str} · CRS {score}"
    if duplicates and base in duplicates:
        return f"{base} (#{project.get('id')})"
    return base


def load_report_options(base_url: str):
    projects, err = api_client.list_projects(base_url)
    if err or not projects:
        return projects or [], {}, None, err

    bases = [f"{p.get('project_name') or 'Untitled'} · {fmt_time(p.get('created_at'))} · CRS {p.get('crs_score', 0)}" for p in projects]
    counts = Counter(bases)
    duplicates = {b for b, c in counts.items() if c > 1}

    proj_map = {p["id"]: p for p in projects if "id" in p}
    label_map = {p["id"]: report_label(p, duplicates) for p in projects if "id" in p}
    return projects, proj_map, label_map, None
