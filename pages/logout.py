import streamlit as st

st.set_page_config(page_title="Logout", layout="centered",initial_sidebar_state="collapsed")

hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="collapsedControl"] {
            display: none;
        }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)


for key in ["access_token", "username"]:
    if key in st.session_state:
        del st.session_state[key]

st.success("✅ Logged out successfully.")
st.switch_page("login.py")
