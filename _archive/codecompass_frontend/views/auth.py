"""Login, sign-up, password reset and the Developer Offline Mode toggle."""
import streamlit as st
import auth_bridge
from components import navbar


def _sync_offline():
    st.session_state["offline_mode"] = st.session_state["_offline_widget"]


def _credentials_form(name, button, action):
    with st.form(name, border=False):
        email = st.text_input("Email", key=f"{name}_email", placeholder="you@college.edu")
        password = st.text_input("Password", type="password", key=f"{name}_pw")
        submitted = st.form_submit_button(button, type="primary", width="stretch")
    if submitted:
        if not email or not password:
            st.warning("Enter your email and password.")
            return
        ok, message = action(email, password)
        if ok:
            st.rerun()
        st.error(message)


def _reset_form():
    with st.form("reset", border=False):
        email = st.text_input("Email", key="reset_email", placeholder="you@college.edu")
        submitted = st.form_submit_button("Send reset link", type="primary", width="stretch")
    if submitted and email:
        ok, message = auth_bridge.reset_password(email)
        st.success("Reset link sent. Check your inbox.") if ok else st.error(message)


def render():
    navbar.render("auth")
    with st.container(key="card_auth"):
        st.html('<p class="cc-h2" style="font-size:1.4rem">Welcome to CodeCompass</p>'
                '<p class="cc-muted">Sign in to save audits and open them later.</p>')
        st.toggle("Developer offline mode", value=st.session_state["offline_mode"],
                  key="_offline_widget", on_change=_sync_offline,
                  help="Skips Firebase entirely so you can demo without a network.")
        if st.session_state["offline_mode"]:
            st.info("Offline mode is on. No network calls are made to Firebase.")
            st.button("Enter dashboard", type="primary", width="stretch", key="enter_offline",
                      on_click=auth_bridge.enter_offline)
            return
        tab_in, tab_up, tab_reset = st.tabs(["Sign in", "Create account", "Reset password"])
        with tab_in:
            _credentials_form("signin", "Sign in", auth_bridge.sign_in)
        with tab_up:
            _credentials_form("signup", "Create account", auth_bridge.sign_up)
        with tab_reset:
            _reset_form()
