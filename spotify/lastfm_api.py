import os
import requests

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

    if res.status_code != 200:
        print("Last.fm error:", res.text)
        return None

    data = res.json()

    try:
        return int(data["artist"]["stats"]["listeners"])
    except KeyError:
        return None
