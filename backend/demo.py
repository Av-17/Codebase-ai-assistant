from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
import os, requests
from urllib.parse import urlencode
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(dotenv_path="../.env")

load_dotenv()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI") 

@app.get("/login")
def login():
    if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
        return JSONResponse({"error": "Missing GitHub OAuth configuration"}, status_code=500)

    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "repo read:user",
        # "prompt": "consent"
    }
    github_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    return RedirectResponse(github_url)

@app.get("/callback")
def callback(code: str):
    if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
        return JSONResponse({"error": "Missing GitHub OAuth configuration"}, status_code=500)

    # Exchange code for access token
    token_res = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI
        }
    )
    token_data = token_res.json()
    token = token_data.get("access_token")

    if not token:
        print(f"Failed to retrieve access token: {token_data}")
        return JSONResponse({"error": "Failed to retrieve access token", "details": token_data.get("error_description", token_data.get("error"))}, status_code=400)

    
    user_res = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {token}"}
    )
    user_data = user_res.json()
    username = user_data.get("login", "unknown")

    if not username:
        print(f"Failed to retrieve username: {user_data}") 
        username = "unknown"
    # print(token,"\n", username)
    # # Set cookies and redirect
    # res = RedirectResponse(url=f"http://localhost:8501/login?token={token}&username={username}")  # <-- redirect to app.py
    # res.set_cookie(key="access_token", value=token, max_age=86400, path="/")
    # res.set_cookie(key="username", value=username, max_age=86400, path="/")
    return RedirectResponse(url=f"http://localhost:8501/?token={token}&username={username}") 