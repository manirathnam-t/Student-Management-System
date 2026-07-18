from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from .forms import LoginForm
from .models import User
from app.extensions import db
from .extensions import bcrypt

auth = Blueprint("auth", __name__)
@auth.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        print("Form submitted")

        email = form.email.data.strip().lower()

        print("Entered Email:", email)

        print("All Users:")

        for u in User.query.all():
            print(f"{u.email} | {u.role}")

        user = User.query.filter(
            db.func.lower(User.email) == email
        ).first()

        if user:

            print("User found:", user.email)

            if bcrypt.check_password_hash(user.password, form.password.data):

                login_user(user)

                flash("Login Successful!", "success")

                if user.role == "Admin":
                    return redirect(url_for("main.admin_dashboard"))

                elif user.role == "Teacher":
                    return redirect(url_for("main.teacher_dashboard"))

                elif user.role == "Student":
                    return redirect(url_for("main.student_dashboard"))

            else:
                print("Wrong Password")
                flash("Invalid password", "danger")

        else:
            print("User NOT found")
            flash("User not found", "danger")

    return render_template("auth/login.html", form=form)

@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully!", "success")

    return redirect(url_for("auth.login"))