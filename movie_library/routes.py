from dataclasses import asdict
import uuid
from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    request,
    current_app,
    url_for,
)
from movie_library.forms import MovieForm
from movie_library.models import Movie


pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)


@pages.route("/")
def index():
    movie_data = current_app.db.movie.find({})
    movies = [Movie(**movie) for movie in movie_data]
    return render_template("index.html", title="Movie Watchlist", movies_data=movies)


@pages.route("/add/", methods=["GET", "POST"])
def add_movie():
    form = MovieForm()

    if form.validate_on_submit():
        _movie = Movie(
            _id=uuid.uuid4().hex,
            title=form.title.data,
            director=form.director.data,
            year=form.year.data,
        )

        current_app.db.movie.insert_one(asdict(_movie))

        return redirect(url_for(".index"))

    return render_template(
        "new_movie.html", title="Movies Watchlist - Add Movie", form=form
    )


@pages.get("/movie/<string:_id>")
def movie(_id: str):
    _movie = Movie(**current_app.db.movie.find_one({"_id": _id}))
    return render_template("movie_details.html", movie=_movie)


@pages.get("/toggle-theme/")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"

    return redirect(request.args.get("current_page"))
