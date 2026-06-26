"""
TaskLedger — a small full-stack task management web app.

Run locally:
    pip install -r requirements.txt
    python app.py

Then open http://127.0.0.1:5000
"""
import os
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import (
    LoginManager, login_user, login_required, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Task
from api import api_bp

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        BASE_DIR, "instance", "taskledger.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)
        db.create_all()

    # ---------- Pages ----------

    @app.route("/")
    @login_required
    def dashboard():
        return render_template("dashboard.html", user=current_user)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            if not username or not email or not password:
                flash("All fields are required.", "error")
                return render_template("register.html")

            if User.query.filter(
                (User.username == username) | (User.email == email)
            ).first():
                flash("That username or email is already taken.", "error")
                return render_template("register.html")

            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                created_at=datetime.utcnow(),
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Account created. Welcome aboard.", "success")
            return redirect(url_for("dashboard"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            user = User.query.filter_by(email=email).first()

            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for("dashboard"))

            flash("Incorrect email or password.", "error")

        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
