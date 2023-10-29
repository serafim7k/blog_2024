from apps import app, db
from flask import render_template, flash, redirect, url_for, request
from apps.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
# from werkzeug.urls import url_parse
from urllib.parse import urlparse

from apps.models import User


@app.route('/')
@app.route('/index')
# @app.route('/about')
@login_required
def index():
    # user = {'username': 'Yurii'}
    posts = [
        {
            'author': {'username': 'David'},
            'body': 'Good sunny day!'
        },
        {
            'author': {'username': 'John'},
            'body': 'Bad foggy day!'
        }
    ]
    return render_template("index.html", title='Home page', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password!")
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        # print(next_page)
        # print(urlparse(next_page).netloc)
        # print(not next_page)
        if not next_page or urlparse(next_page).netloc != '':
            # print(next_page)
            next_page = url_for('index')
            # print(next_page.netloc)
        return redirect(next_page)

        # flash(f"User!!!! {user}!")
        # flash(f"Login requested for user{form.username.data}, remember_me{form.remember_me.data}, password{form.password.data}")
        # flash("All GOOD!")
        # return redirect(url_for('index'))
    return render_template('login.html', title="Sign In", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# @app.route('/log')
# def log():
#     return render_template('base.html', title="LOG")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are REGISTERED!!!')
        return redirect(url_for('login'))

    return render_template('register.html', title="Register", form=form)


