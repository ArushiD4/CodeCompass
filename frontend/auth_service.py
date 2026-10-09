import requests
import streamlit as st

# Fetch the API key from secrets.toml if present; fall back to empty string
# so the module can be imported safely in environments without a secrets file
# (e.g. pytest / AppTest). The bypass logic below already handles empty keys.
try:
    FIREBASE_API_KEY = st.secrets.get("FIREBASE_API_KEY", "")
except FileNotFoundError:
    FIREBASE_API_KEY = ""

def login_with_third_party(email: str, password: str) -> dict:
    """
    Authenticates a user against the external identity provider (Firebase).
    
    Provides a fallback bypass for local development if the API key is absent 
    or matches a known placeholder.
    
    Args:
        email (str): The user's email address.
        password (str): The user's plaintext password.
        
    Returns:
        dict: A dictionary containing a boolean 'success' flag. On success, includes 
              'token' and 'user_id'. On failure, includes an 'error' string.
    """
    if FIREBASE_API_KEY.startswith("AIzaSyB0DPf0g1uVRSqP9gJrg5G7yN-NF90suMs") or not FIREBASE_API_KEY:
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
    """
    Registers a new user account with the external identity provider (Firebase).
    
    Provides a fallback bypass for local development if the API key is absent 
    or matches a known placeholder.
    
    Args:
        email (str): The new user's email address.
        password (str): The new user's plaintext password.
        
    Returns:
        dict: A dictionary containing a boolean 'success' flag. On failure, includes 
              an 'error' string.
    """
    if FIREBASE_API_KEY.startswith("AIzaSyB0DPf0g1uVRSqP9gJrg5G7yN-NF90suMs") or not FIREBASE_API_KEY:
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
    Initiates a password reset flow via the external identity provider (Firebase).
    
    Sends an out-of-band (OOB) password reset link to the specified email address.
    
    Args:
        email (str): The user's email address.
        
    Returns:
        dict: A dictionary containing a boolean 'success' flag. On failure, includes 
              an 'error' string.
    """
    if FIREBASE_API_KEY.startswith("AIzaSyB0DPf0g1uVRSqP9gJrg5G7yN-NF90suMs") or not FIREBASE_API_KEY:
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
