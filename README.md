# CodeCompass

Navigate your code. Defend your logic.

## Configuration & Environment Variables

- `CODECOMPASS_API_KEY`: API key for communicating with the backend FastAPI service.
- `CODECOMPASS_BACKEND_URL`: URL of the FastAPI backend (defaults to `http://127.0.0.1:8000`).
- `CODECOMPASS_OFFLINE_TOKEN`: Optional override token for Developer Offline Mode.

### Frontend Secrets
Copy `frontend/.streamlit/secrets.toml.example` to `frontend/.streamlit/secrets.toml` and set your `FIREBASE_API_KEY`.

