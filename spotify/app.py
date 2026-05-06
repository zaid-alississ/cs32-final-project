from flask import Flask, redirect, request, session, url_for, render_template
from dotenv import load_dotenv
import os
import json
import requests
import urllib.parse
from dotenv import load_dotenv
from lastfm_api import get_artist_listeners

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPE = os.getenv("SCOPE")


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
            "Missing Spotify credentials. Set CLIENT_ID and "
            "CLIENT_SECRET in your terminal first."
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
        "https://api.spotify.com/v1/me/top/artists?limit=5&time_range=short_term",
        headers=headers,
        timeout=10,
    )

    if artists_res.status_code != 200:
        return f"Top artists request failed: {artists_res.text}"

    artists_data = artists_res.json()
    spotify_artists = artists_data.get("items", [])

    top_artists = [artist["name"] for artist in spotify_artists]

    artist_listener_data = []

    for artist in spotify_artists:
        name = artist["name"]
        listeners = get_artist_listeners(name)

        artist_listener_data.append({
            "name": name,
            "listeners": listeners
        })

    genre_counts = {}
    for artist in artists_data.get("items", []):
        for genre in artist.get("genres", []):
            genre_counts[genre] = genre_counts.get(genre, 0) + 1

    top_genres = sorted(genre_counts, key=genre_counts.get, reverse=True)[:5]

    profile_name = "Spotify Taste Profile"
    profile_description = "This is a first version of your Spotify taste profile based on your top artists and genres."

    tracks_res = requests.get(
        "https://api.spotify.com/v1/me/top/tracks?limit=5&time_range=short_term",
        headers=headers,
        timeout=10,
    )

    top_tracks = [track["name"] for track in tracks_res.json().get("items", [])]

    with open("sample_artists.json") as f:
        sample_artists = json.load(f)

    scores = {
    "Energy": 50,
    "Variety": 50,
    "Mainstream": 50,
    }

    return render_template(
        "results.html",
        profile_name=profile_name,
        profile_description=profile_description,
        top_artists=top_artists,
        top_tracks=top_tracks,
        top_genres=top_genres,
        artist_listener_data=artist_listener_data,
        scores=scores,
    )

if __name__ == "__main__":
    app.run(debug=True)
