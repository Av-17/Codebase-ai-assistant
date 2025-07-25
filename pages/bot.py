import streamlit as st
import asyncio
from load import fetch_github, chunk_splitter
from Agent import app  


st.set_page_config(page_title="Codebase QA Assistant", layout="centered",initial_sidebar_state="collapsed")
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
st.title("🧑‍💻 Codebase QA Assistant")

if "access_token" not in st.session_state or "username" not in st.session_state:
    st.warning("🔒 You must log in first.")
    st.switch_page("login.py") 


st.write(f"Welcome, **{st.session_state['username']}**")
st.page_link("pages/logout.py", label="🚪 Logout")
st.info("Plzz dont repload the page it will get redirect to login page again")
st.session_state.setdefault("repo_name", "")
st.session_state.setdefault("chunks", None)

st.subheader("📂 Enter GitHub Repository URL")
st.session_state.repo_name = st.text_input(
    "Repository URL (e.g., https://github.com/user/repo)",
    value=st.session_state.repo_name
)

col1, col2 = st.columns(2)


@st.cache_resource(show_spinner="📂 Fetching repo...")
def get_code(repo, token):
    return asyncio.run(fetch_github(repo, token))

with col1:
    if st.button("📥 Fetch Repository"):
        repo = st.session_state.repo_name.strip()
        if not repo:
            st.warning("⚠️ Please enter a repository URL.")
        else:
            try:
                code = get_code(repo, st.session_state["access_token"])
                if not code:
                    st.markdown(
                        """<div style="border-left: 6px solid #ffc107; padding: 10px; background-color: #fff3cd;">
                        ⚠️ <strong>No files found.</strong> Add at least one file like <code>README.md</code>.
                        </div>""",
                        unsafe_allow_html=True
                    )
                else:
                    if len(code) > 100:
                        st.warning("Repo has too many files. Showing first 100.")
                        code = dict(list(code.items())[:100])
                    st.success(f"✅ Fetched {len(code)} files")
                    st.session_state.chunks = chunk_splitter(code)
                    st.session_state.api_key_required = False
            except Exception as e:
                err = str(e).lower()
                if "may be private" in err:
                    st.session_state.api_key_required = True
                    st.session_state.error_message = "🔐 Repo may be private. Please enter a valid GitHub token."
                    st.rerun()
                elif "may be empty" in err:
                    st.markdown(
                        """<div style="border-left: 6px solid #ffa500; padding: 10px; background-color: #fff3cd;">
                        ⚠️ <strong>Empty repository</strong>. Please add at least one file.
                        </div>""",
                        unsafe_allow_html=True
                    )
                elif "403" in err:
                    st.markdown(
                        """<div style="border-left: 6px solid #dc3545; padding: 10px; background-color: #f8d7da;">
                        🔐 <strong>Access Denied (403)</strong>. Check token permissions.
                        </div>""",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""<div style="border-left: 6px solid #dc3545; padding: 10px; background-color: #f8d7da;">
                        ❌ <strong>Error</strong><br><code>{e}</code>
                        </div>""",
                        unsafe_allow_html=True
                    )

with col2:
    if st.button("🔄 Refresh"):
        st.cache_resource.clear()
        for key in ["repo_name", "chunks"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()


st.subheader("❓ Ask a Question")
question = st.text_input("Your Question About the Codebase")

if st.button("✨ Get Answer"):
    if not question:
        st.warning("⚠️ Enter a question.")
    elif not st.session_state.chunks:
        st.warning("⚠️ Fetch the repository first.")
    else:
        with st.spinner("💭 Thinking..."):
            try:
                response = app.invoke({
                    "question": question,
                    "chunks": st.session_state.chunks
                })
                st.subheader("💡 AI Response")
                st.info(response.get("answer", "No answer returned."))
            except Exception as e:
                st.error(f"❌ Error: {e}")
