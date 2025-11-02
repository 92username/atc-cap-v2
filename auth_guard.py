import streamlit as st


def require_login():
    """Ensure a user is logged in. If not, navigate to the login page.

    This helper assumes a Streamlit "login" page exists in `pages/login.py` or
    that the main app shows the login screen when `st.session_state['user']`
    is missing. We use `st.switch_page` for multi-page apps—if the app is
    single-file, `st.switch_page` will raise if the target doesn't exist; in
    that case this will fallback to `st.stop()` after rendering nothing.
    """

    if "user" not in st.session_state:
        try:
            st.switch_page("login")
        except Exception:
            # For single-page apps where `login` page is not defined,
            # just stop execution (the login UI should be rendered by the
            # main file when no user is present).
            st.stop()
