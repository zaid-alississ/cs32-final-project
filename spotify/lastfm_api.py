import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_artist_listeners(artist_name):
    api_key = os.getenv("LASTFM_API_KEY")

    print("Last.fm API key loaded:", api_key is not None)

    params = {
        "method": "artist.getInfo",
        "artist": artist_name,
        "api_key": api_key,
        "format": "json"
    }

    res = requests.get(
        "https://ws.audioscrobbler.com/2.0/",
        params=params,
        timeout=10
    )

    print("Last.fm status:", res.status_code)
    print("Last.fm response:", res.text[:300])

    data = res.json()

    if "error" in data:
        return None

    return int(data["artist"]["stats"]["listeners"])
