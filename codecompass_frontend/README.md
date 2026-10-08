# CodeCompass frontend (Streamlit)

Drop these files into your existing `frontend/` folder, next to `auth_service.py`
(back up your old `app.py` and `styles.py` first; the new ones replace them).

    pip install -r requirements.txt
    uvicorn main:app --port 8000      # backend, unchanged
    streamlit run app.py              # frontend, port 8501

## File map (every file is under 150 lines)

| File | Job |
|---|---|
| app.py | Entry point. Routes landing / auth / dashboard from `st.session_state["_page"]` |
| config.py | Constants: CRS bands, severity weights, palette, built-in filter list |
| state.py | Session-state schema and navigation callbacks |
| api_client.py | The four REST calls from section 6. Returns `(data, error)` |
| auth_bridge.py | Thin adapter that calls your `auth_service.py` + Developer Offline Mode |
| styles.py, styles_cards.py | Design system (tokens, widget overrides, component classes) |
| views/landing.py, auth.py, dashboard.py | The three pages |
| components/navbar.py | Top bar, backend health, settings |
| components/scan_form.py | Inputs and the scan pipeline with progress status |
| components/hero.py | CRS ring (green / amber / red) and KPI bento |
| components/findings.py | Finding cards with Viva Defense Tips |
| components/graph_data.py | Edge resolution, built-in filter, degree, top-K hubs, module colours |
| components/graph_view.py | agraph rendering, physics / layout config, node detail panel |
| components/architecture.py | Stack, request lifecycle and rules table for evaluators |

## If login fails with "none of (...)"
Open `auth_bridge.py` and edit `FUNCTION_NAMES` so it lists your real function names
in `auth_service.py`. Nothing else needs to change.
