"""auth.py — Authentication View with split cinematic layout."""
import streamlit as st
import auth_bridge
from config import APP_NAME, TAGLINE
from components import navbar
from components.primitives import esc, footer
from entrypoints import entrypoint


@entrypoint()
def _sync_offline():
    st.session_state["offline_mode"] = st.session_state["_offline_widget"]


def _left_panel():
    return (
        f'<div class="cc-code-box">'
        f'<span style="color:var(--mute)"># AST Static Engine parsing in progress</span><br>'
        f'<span style="color:var(--info)">def</span> <span style="color:var(--good)">audit_codebase</span>(target_path):<br>'
        f'&nbsp;&nbsp;&nbsp;&nbsp;tree = ast.parse(source_code)<br>'
        f'&nbsp;&nbsp;&nbsp;&nbsp;visitor = CodeAuditor()<br>'
        f'&nbsp;&nbsp;&nbsp;&nbsp;visitor.visit(tree)<span class="cc-caret"></span>'
        f'<p class="cc-muted" style="margin-top:2rem;font-family:var(--font);font-size:.92rem">{esc(TAGLINE)}</p>'
        f'</div>'
    )


def _form(name, button, action):
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


def _forgot_password_view():
    st.html(f'<p class="cc-h2" style="font-size:1.2rem;margin-bottom:.4rem">Reset password</p>'
            f'<p class="cc-muted" style="margin-bottom:1rem">Enter your email to receive a password reset link.</p>')
    if st.session_state.get("offline_mode"):
        st.info("Not available in offline mode")
    else:
        with st.form("forgot_pw", border=False):
            email = st.text_input("Email", key="forgot_email", placeholder="you@college.edu")
            submitted = st.form_submit_button("Send reset link", type="primary", width="stretch")
        if submitted:
            if not email:
                st.warning("Enter your email address.")
            else:
                try:
                    ok, err = auth_bridge.reset_password(email)
                except (OSError, ValueError) as exc:
                    st.error(esc(f"Network error: {exc}"))
                    ok, err = False, ""
                if ok or (err and "EMAIL_NOT_FOUND" in err.upper()):
                    st.success("If an account exists for this email, a reset link has been sent.")
                elif err:
                    st.error(esc(f"Reset failed: {err}"))
    if st.button("← Back to sign in", key="btn_back_signin"):
        st.session_state["_auth_subview"] = "signin"
        st.rerun()


def _offline_section():
    st.toggle("Developer offline mode", value=st.session_state.get("offline_mode", False),
              key="_offline_widget", on_change=_sync_offline,
              help="Skips Firebase entirely so you can demo without a network.")
    if st.session_state.get("offline_mode"):
        st.html('<p class="cc-mono" style="color:var(--good);margin:.25rem 0 .75rem">'
                'network: bypassed</p>')
        st.button("Enter dashboard", type="primary", width="stretch", key="enter_offline",
                  on_click=auth_bridge.enter_offline)
        return True
    return False


def render():
    navbar.render("auth")
    st.write("")
    col_left, col_right = st.columns([1, 1], gap="large")
    with col_left:
        st.html(_left_panel())
    with col_right:
        with st.container(key="card_auth"):
            st.html(f'<p class="cc-h2" style="font-size:1.4rem">Welcome to {esc(APP_NAME)}</p>'
                    f'<p class="cc-muted" style="margin-bottom:1rem">Sign in to save audits and open them later.</p>')
            notice = st.session_state.get("auth_notice")
            if notice:
                st.info(notice)
            if st.session_state.get("_auth_subview") == "forgot":
                _forgot_password_view()
            elif not _offline_section():
                t_in, t_up = st.tabs(["Sign in", "Sign up"])
                with t_in:
                    _form("signin", "Sign in", auth_bridge.sign_in)
                    if st.button("Forgot password?", key="btn_forgot_pw"):
                        st.session_state["_auth_subview"] = "forgot"
                        st.rerun()
                with t_up:
                    _form("signup", "Create account", auth_bridge.sign_up)
    st.html(footer())

