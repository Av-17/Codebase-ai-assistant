import streamlit as st
from Agent import app
import asyncio
from load import chunk_splitter, fetch_github
import os
from dotenv import load_dotenv

load_dotenv()
MY_GITHUB_TOKEN = st.secrets["MY_GITHUB_TOKEN"]
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
st.set_page_config(page_title="🧑‍💻 Codebase QA Assistant", layout="centered")
st.title("🧑‍💻 Codebase QA Assistant")

# Session state initialization
st.session_state.setdefault("chunks", None)
st.session_state.setdefault("repo_name", "")
st.session_state.setdefault("api_token", "")
st.session_state.setdefault("api_key_required", False)
st.session_state.setdefault("error_message", None)

st.subheader("🔗 GitHub Repository Details")

# Repo URL input
st.session_state.repo_name = st.text_input(
    "📁 Repository URL", value=st.session_state.repo_name
)

# Only show token input if access failed earlier
if st.session_state.api_key_required:
    st.warning(st.session_state.error_message or "🔐 Please enter your GitHub API token.")
    st.session_state.api_token = st.text_input(
        "🔑 GitHub API Token (required for private repos or rate limits)",
        type="password",
        value=st.session_state.api_token
    )

col1, col2 = st.columns(2)

# Cached GitHub fetcher
@st.cache_resource(show_spinner="🔍 Fetching repo...")
def get_code(repo, token):
    return asyncio.run(fetch_github(repo, token))

# Fetch repo button
with col1:
    if st.button("📂 Fetch Repository"):
        repo_name = st.session_state.repo_name.strip()

        if not repo_name:
            st.warning("⚠️ Please enter a repository URL.")
        else:
            try:
                token_to_use = st.session_state.api_token.strip() or MY_GITHUB_TOKEN
                code = get_code(repo_name, token_to_use)

                if not code:
                    st.warning("⚠️ No files found in the repository.")
                else:
                    if len(code) > 100:
                        st.warning(f"⚠️ Repo has {len(code)} files. Limiting to first 100.")
                        code = dict(list(code.items())[:100])
                    st.success(f"✅ Fetched {len(code)} files from {repo_name}")
                    st.session_state.chunks = chunk_splitter(code)
                    st.session_state.api_key_required = False
                    st.session_state.error_message = None

            except Exception as e:
                err = str(e).lower()
                if (
                    "403" in err or 
                    "access denied" in err or 
                    "rate limit" in err or 
                    "repo not found" in err or 
                    "404" in err
                ):
                    st.session_state.api_key_required = True
                    st.session_state.error_message = (
    "🔐 This repository may be private or you're rate-limited. "
    "Please enter a GitHub token with appropriate access. "
    "For fine-grained tokens, ensure it includes 'Contents: Read-only' permission for this repository."
)
                    st.rerun()
                else:
                    st.error(f"🚨 Unexpected error: {e}")

# Refresh button
with col2:
    if st.button("🔄 Refresh Repo"):
        st.cache_resource.clear()
        st.session_state.clear()
        st.success("🔁 Cache cleared. Please fetch the repo again.")
        st.rerun()

# Question input
st.subheader("❓ Ask a Question")
question = st.text_input("💬 Your Question About the Codebase")

# Invoke AI agent
if st.button("✨ AI Response"):
    if not question:
        st.warning("⚠️ Question cannot be blank.")
    elif st.session_state.chunks is None:
        st.warning("⚠️ Please fetch the repository first.")
    else:
        try:
            with st.spinner("💭 Thinking..."):
                response = app.invoke(
                    {"question": question, "chunks": st.session_state.chunks},
                    config={"configurable": {"thread_id": "user123-session1"}}
                )
                st.subheader("💡 AI Response")
                st.info(response.get("answer", "No answer returned."))
        except Exception as e:
            st.error(f"🚨 Error: {str(e)}")
