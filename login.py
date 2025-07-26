import streamlit as st
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Login", layout="centered",initial_sidebar_state="collapsed")
streamlit_js_eval(js_expressions="null")



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
params = st.query_params
token = params.get("token", None)
username = params.get("username", None)
if token and username:
    st.session_state.access_token = token
    st.session_state.username = username
    # Clear token from URL
    st.query_params.clear()
    # print(token,username)
    st.success("🔓 Logged in successfully. Redirecting...")
    st.switch_page("pages/bot.py")



elif "access_token" in st.session_state:
    st.switch_page("pages/bot.py")

else:
    st.title("🔐 GitHub OAuth Login")
    login_url = "https://backend-for-codebase-1.onrender.com/login"
    st.markdown(f"""
    <a href="{login_url}" target="_self">
        <button style="padding: 10px 20px; font-size: 16px;">🔐 Login with GitHub</button>
    </a>
""", unsafe_allow_html=True)