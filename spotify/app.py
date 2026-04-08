# Flask routes, login flow, calls helper functions, sends data to HTML templates
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/results")
def results():
    # Fake sample data for now
    profile_name = "The Genre Explorer"
    profile_description = (
        "You listen to a wide variety of music and do not stay in just one lane. "
        "Your taste shows curiosity, balance, and a willingness to explore different sounds."
    )

    top_artists = ["Taylor Swift", "Frank Ocean", "SZA", "Drake", "Lana Del Rey"]
    top_genres = ["pop", "r&b", "indie pop", "hip hop", "alternative"]

    scores = {
        "Energy": 72,
        "Danceability": 66,
        "Positivity": 48,
        "Acousticness": 39,
        "Variety": 88
    }

    return render_template(
        "results.html",
        profile_name=profile_name,
        profile_description=profile_description,
        top_artists=top_artists,
        top_genres=top_genres,
        scores=scores
    )

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
