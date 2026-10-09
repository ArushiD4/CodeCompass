"""audit_diff.py — Pure audit diffing, fingerprinting, and report comparison."""
from datetime import datetime, timezone
import hashlib
import re
from config import CRS_BANDS

SEV_RANK = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}


def fingerprint(issue: dict, occurrence: int = 0) -> str:
    rule = (issue.get("rule_name") or "").strip().lower()
    fpath = (issue.get("file_path") or "").strip().replace("\\", "/")
    tip = re.sub(r"\d+", "#", issue.get("viva_tip") or "")
    payload = f"{rule}|{fpath}|{tip}|{occurrence}".encode("utf-8")
    return hashlib.sha1(payload).hexdigest()


def _parse_ts(proj: dict):
    ca = proj.get("created_at")
    if not ca:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        dt = datetime.fromisoformat(str(ca).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


def order_reports(a: dict, b: dict):
    p_a = a.get("project", a)
    p_b = b.get("project", b)
    ts_a, id_a = _parse_ts(p_a), int(p_a.get("id") or 0)
    ts_b, id_b = _parse_ts(p_b), int(p_b.get("id") or 0)
    if (ts_a, id_a) <= (ts_b, id_b):
        return a, b, False
    return b, a, True


def _band(score: int):
    for min_s, label, tone, _ in CRS_BANDS:
        if score >= min_s:
            return label, tone
    return CRS_BANDS[-1][1], CRS_BANDS[-1][2]


def _build_fps(issues: list):
    sorted_issues = sorted(issues, key=lambda x: int(x.get("line_number") or 0))
    counts, fps = {}, []
    for iss in sorted_issues:
        key = (
            (iss.get("rule_name") or "").strip().lower(),
            (iss.get("file_path") or "").strip().replace("\\", "/"),
            re.sub(r"\d+", "#", iss.get("viva_tip") or ""),
        )
        occ = counts.get(key, 0)
        counts[key] = occ + 1
        fps.append((fingerprint(iss, occ), iss))
    return fps


def _sort_issues(issues: list):
    return sorted(issues, key=lambda i: (
        SEV_RANK.get(i.get("severity", "INFO"), 3),
        (i.get("file_path") or "").lower(),
        int(i.get("line_number") or 0),
    ))


def compare_reports(earlier: dict, later: dict) -> dict:
    p_e = earlier.get("project", earlier)
    p_l = later.get("project", later)
    crs_b, crs_a = int(p_e.get("crs_score") or 0), int(p_l.get("crs_score") or 0)
    delta = crs_a - crs_b
    band_b, band_a = _band(crs_b), _band(crs_a)

    e_fps = _build_fps(earlier.get("issues", []))
    l_fps = _build_fps(later.get("issues", []))
    e_map = {fp: iss for fp, iss in e_fps}
    l_map = {fp: iss for fp, iss in l_fps}

    fixed = _sort_issues([iss for fp, iss in e_fps if fp not in l_map])
    new = _sort_issues([iss for fp, iss in l_fps if fp not in e_map])
    remaining = _sort_issues([iss for fp, iss in l_fps if fp in e_map])

    sev_b = {"CRITICAL": 0, "WARNING": 0, "INFO": 0}
    for iss in earlier.get("issues", []):
        s = iss.get("severity", "INFO")
        if s in sev_b:
            sev_b[s] += 1
    sev_a = {"CRITICAL": 0, "WARNING": 0, "INFO": 0}
    for iss in later.get("issues", []):
        s = iss.get("severity", "INFO")
        if s in sev_a:
            sev_a[s] += 1

    all_rules = set(i.get("rule_name") for i in earlier.get("issues", [])) | \
                set(i.get("rule_name") for i in later.get("issues", []))
    by_rule = []
    for r in sorted(all_rules):
        bn = sum(1 for i in earlier.get("issues", []) if i.get("rule_name") == r)
        an = sum(1 for i in later.get("issues", []) if i.get("rule_name") == r)
        by_rule.append((r, bn, an, an - bn))
    by_rule.sort(key=lambda x: (x[1] - x[2], -x[2]), reverse=True)

    all_files = set(i.get("file_path") for i in earlier.get("issues", [])) | \
                set(i.get("file_path") for i in later.get("issues", []))
    by_file = []
    for f in sorted(all_files):
        bn = sum(1 for i in earlier.get("issues", []) if i.get("file_path") == f)
        an = sum(1 for i in later.get("issues", []) if i.get("file_path") == f)
        by_file.append((f, bn, an, an - bn))
    by_file.sort(key=lambda x: abs(x[3]), reverse=True)

    name_e = (p_e.get("project_name") or "").strip().lower()
    name_l = (p_l.get("project_name") or "").strip().lower()
    same_proj = (name_e == name_l) and bool(name_e)
    tone = "good" if delta > 0 else ("bad" if delta < 0 else "info")

    if delta == 0 and not fixed and not new and crs_b == crs_a:
        headline = "No changes between these two audits."
    else:
        sign = "+" if delta > 0 else ""
        headline = (f"CRS {crs_b} -> {crs_a} ({sign}{delta}). {band_b[0]} -> {band_a[0]}. "
                    f"{len(fixed)} findings fixed, {len(new)} new, {len(remaining)} remaining.")

    return {
        "crs_before": crs_b, "crs_after": crs_a, "delta": delta,
        "band_before": band_b, "band_after": band_a,
        "severity_before": sev_b, "severity_after": sev_a,
        "fixed": fixed, "new": new, "remaining": remaining,
        "by_rule": by_rule, "by_file": by_file,
        "files_delta": int(p_l.get("total_files") or 0) - int(p_e.get("total_files") or 0),
        "functions_delta": int(p_l.get("total_functions") or 0) - int(p_e.get("total_functions") or 0),
        "same_project": same_proj, "tone": tone, "headline": headline,
    }
