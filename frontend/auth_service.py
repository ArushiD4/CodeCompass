import requests
import streamlit as st

# Fetch the API key from secrets.toml if present; fall back to empty string
# so the module can be imported safely in environments without a secrets file
# (e.g. pytest / AppTest). The bypass logic below already handles empty keys.
FIREBASE_API_KEY = st.secrets.get("FIREBASE_API_KEY", "")

def login_with_third_party(email: str, password: str) -> dict:
    """
    Current: Hits Firebase REST API.
    Future: Change URL to 'http://localhost:8000/api/login'
    """
    if FIREBASE_API_KEY.startswith("AIzaSyYourFirebaseApiKeyHere") or not FIREBASE_API_KEY:
        # Temporary bypass for local testing: allow login if email and password are provided
        if email and password:
            return {"success": True, "token": "dummy-token-12345", "user_id": "dummy-user-id"}
        return {"success": False, "error": "Email and Password are required"}

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {"success": True, "token": data["idToken"], "user_id": data["localId"]}
        else:
            error_msg = response.json().get("error", {}).get("message", "Login failed")
            return {"success": False, "error": error_msg}
    except Exception as e:
        return {"success": False, "error": f"Connection error: {str(e)}"}

def signup_with_third_party(email: str, password: str) -> dict:
    if FIREBASE_API_KEY.startswith("AIzaSyYourFirebaseApiKeyHere") or not FIREBASE_API_KEY:
        # Temporary bypass for local testing: allow signup
        if email and password:
            return {"success": True}
        return {"success": False, "error": "Email and Password are required"}

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            return {"success": True}
        else:
            error_msg = response.json().get("error", {}).get("message", "Signup failed")
            return {"success": False, "error": error_msg}
    except Exception as e:
        return {"success": False, "error": f"Connection error: {str(e)}"}

def reset_password_with_third_party(email: str) -> dict:
    """    
    Sends a password reset email using Firebase REST API.
    """
    if FIREBASE_API_KEY.startswith("AIzaSyYourFirebaseApiKeyHere") or not FIREBASE_API_KEY:
        # Temporary bypass for local testing: allow reset link send
        if email:
            return {"success": True}
        return {"success": False, "error": "Email is required"}

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            return {"success": True}
        else:
            error_msg = response.json().get("error", {}).get("message", "Failed to send reset link")
            return {"success": False, "error": error_msg}
    except Exception as e:
        return {"success": False, "error": f"Connection error: {str(e)}"}
