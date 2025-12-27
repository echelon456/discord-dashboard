from flask import Flask, redirect, request
import os
import requests

app = Flask(__name__)

# Environment variables
CLIENT_ID = os.environ["DISCORD_CLIENT_ID"]
CLIENT_SECRET = os.environ["DISCORD_CLIENT_SECRET"]
REDIRECT_URI = os.environ["DISCORD_REDIRECT_URI"]

# ---------------- HOME ----------------
@app.route("/")
def home():
    return '<a href="/login">Login with Discord</a>'

# ---------------- LOGIN ----------------
@app.route("/login")
def login():
    return redirect(
        "https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        "&scope=identify guilds"
    )

# ---------------- CALLBACK ----------------
@app.route("/callback")
def callback():
    code = request.args.get("code")

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    r = requests.post(
        "https://discord.com/api/oauth2/token",
        data=data,
        headers=headers
    )

    token = r.json().get("access_token")

    # Fetch user info (confirms login)
    requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 👉 CHANGE IS HERE: redirect instead of success message
    return redirect("/dashboard")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    return """
    <h1>Dashboard</h1>
    <p>You are logged in successfully.</p>
    <a href="/invite">➕ Add bot to a server</a>
    """

# ---------------- BOT INVITE ----------------
@app.route("/invite")
def invite():
    permissions = "8"  # Admin (can reduce later)
    scopes = "bot%20applications.commands"

    invite_url = (
        "https://discord.com/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&permissions={permissions}"
        f"&scope={scopes}"
    )

    return redirect(invite_url)

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
