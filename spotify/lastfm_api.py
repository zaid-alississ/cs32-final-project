import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_artist_listeners(artist_name):
    params = {
        "method": "artist.getInfo",
        "artist": artist_name,
        "api_key": os.getenv("LASTFM_API_KEY"),
        "format": "json"
    }

    res = requests.get(
        "https://ws.audioscrobbler.com/2.0/",
        params=params,
        timeout=10
    )

    data = res.json()

    if "error" in data:
        print("Last.fm API error:", data)
        return None

    return int(data["artist"]["stats"]["listeners"])
