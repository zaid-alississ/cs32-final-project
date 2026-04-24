from flask import Flask, redirect, request, session, url_for, render_template
import os
import requests
import urllib.parse

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "https://laughing-acorn-jr79v7wwv77f4xg-5000.app.github.dev/callback"
SCOPE = "user-top-read"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/login")
def login():
    if not CLIENT_ID or not CLIENT_SECRET:
        return (
            "Missing Spotify credentials. Set SPOTIFY_CLIENT_ID and "
            "SPOTIFY_CLIENT_SECRET in your terminal first."
        )

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
    }
    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)
    return redirect(auth_url)


@app.route("/callback")
def callback():
    error = request.args.get("error")
    if error:
        return f"Spotify returned an error: {error}"

    code = request.args.get("code")
    if not code:
        return "No authorization code was returned by Spotify."

    token_res = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=10,
    )

    if token_res.status_code != 200:
        return f"Token request failed: {token_res.text}"

    token_data = token_res.json()
    access_token = token_data.get("access_token")
    if not access_token:
        return f"No access token returned: {token_data}"

    session["access_token"] = access_token
    return redirect(url_for("results"))


@app.route("/results")
def results():
    token = session.get("access_token")
    if not token:
        return redirect(url_for("home"))

    headers = {"Authorization": f"Bearer {token}"}

    artists_res = requests.get(
        "https://api.spotify.com/v1/me/top/artists?limit=10",
        headers=headers,
        timeout=10,
    )

    if artists_res.status_code != 200:
        return f"Top artists request failed: {artists_res.text}"

    artists_data = artists_res.json()

    top_artists = [artist["name"] for artist in artists_data.get("items", [])]

    genre_counts = {}
    for artist in artists_data.get("items", []):
        for genre in artist.get("genres", []):
            genre_counts[genre] = genre_counts.get(genre, 0) + 1

    top_genres = sorted(genre_counts, key=genre_counts.get, reverse=True)[:5]

    profile_name = "Spotify Taste Profile"
    profile_description = "This is a first version of your Spotify taste profile based on your top artists and genres."

    scores = {
        "Energy": 75,
        "Variety": min(len(top_genres) * 15, 100),
        "Mainstream": 60,
    }

    return render_template(
        "results.html",
        profile_name=profile_name,
        profile_description=profile_description,
        top_artists=top_artists,
        top_genres=top_genres,
        scores=scores,
    )


if __name__ == "__main__":
    app.run(debug=True)
