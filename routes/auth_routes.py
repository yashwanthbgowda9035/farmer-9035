from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models.database import db
from models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
        
    if request.method == "POST":
        username_or_email = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))
        else:
            flash("Invalid username/email or password.", "danger")
            
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
        
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        language = request.form.get("preferred_language", "en")
        location = request.form.get("location", "Bengaluru, Karnataka").strip()
        
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")
            
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html")
            
        if User.query.filter_by(username=username).first():
            flash("Username already taken. Please pick another.", "danger")
            return render_template("register.html")
            
        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please login.", "danger")
            return render_template("register.html")
            
        # First registered user can be made admin or regular farmer
        is_first = User.query.count() == 0
        role = "admin" if is_first else "farmer"
        
        new_user = User(
            username=username,
            email=email,
            role=role,
            preferred_language=language,
            state_district=location
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        flash(f"Registration successful! Welcome to KrishiMitra AI, {username}.", "success")
        return redirect(url_for("main.dashboard"))
        
    return render_template("register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out safely.", "info")
    return redirect(url_for("main.index"))
