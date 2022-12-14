import datetime
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
    flash,
)
from movie_library.forms import ExtendedMovieForm, MovieForm, RegisterForm, LoginForm
from movie_library.models import Movie, User
from passlib.hash import pbkdf2_sha256


pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)


@pages.route("/")
def index():
    movie_data = current_app.db.movie.find({})
    movies = [Movie(**movie) for movie in movie_data]
    return render_template("index.html", title="Movie Watchlist", movies_data=movies)


@pages.route("/register/", methods=["GET", "POST"])
def register():
    if session.get("email"):
        return redirect(url_for(".index"))

    form = RegisterForm()

    if form.validate_on_submit():
        user = User(
            _id=uuid.uuid4().hex,
            email=form.email.data,
            password=pbkdf2_sha256.hash(form.password.data),
        )

        current_app.db.user.insert_one(asdict(user))

        flash("User registered successfully", "success")

        return redirect(url_for(".index"))

    return render_template(
        "register.html",
        title="Movies Watchlist - Register",
        form=form,
    )


@pages.route("/login/", methods=["GET", "POST"])
def login():
    if session.get("email"):
        return redirect(url_for(".index"))

    form = LoginForm()

    if form.validate_on_submit():
        user_data = current_app.db.user.find_one({"email": form.email_data})
        if not user_data:
            flash("Login credentials not correct", category="danger")
            return redirect(url_for(".login"))
        user = User(**user_data)

        if user and pbkdf2_sha256.verify(form.password, user.password):
            session["user_id"] = user._id
            session["email"] = user.email

            return redirect(url_for(".index"))

    return render_template("login.html", title="Movie Watchlist - Login", form=form)


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


@pages.route("/edit/<string:_id>", methods=["GET", "POST"])
def edit_movie(_id: str):
    _movie = Movie(**current_app.db.movie.find_one({"_id": _id}))
    form = ExtendedMovieForm(obj=_movie)
    if form.validate_on_submit():
        _movie.cast = form.cast.data
        _movie.series = form.series.data
        _movie.tags = form.tags.data
        _movie.description = form.description.data
        _movie.video_link = form.video_link.data

        current_app.db.movie.update_one({"_id": _movie._id}, {"$set": asdict(_movie)})
        return redirect(url_for(".movie", _id=_movie._id))
    return render_template("movie_form.html", movie=_movie, form=form)


@pages.get("/movie/<string:_id>")
def movie(_id: str):
    _movie = Movie(**current_app.db.movie.find_one({"_id": _id}))
    return render_template("movie_details.html", movie=_movie)


@pages.get("/movie/<string:_id>/rate/")
def rate_movie(_id):
    rating = int(request.args.get("rating"))
    current_app.db.movie.update_one({"_id": _id}, {"$set": {"rating": rating}})

    return redirect(url_for(".movie", _id=_id))


@pages.get("/movie/<string:_id>/watch")
def watch_today(_id):
    current_app.db.movie.update_one(
        {"_id": _id}, {"$set": {"last_watched": datetime.datetime.today()}}
    )

    return redirect(url_for(".movie", _id=id))


@pages.get("/toggle-theme/")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"

    return redirect(request.args.get("current_page"))
