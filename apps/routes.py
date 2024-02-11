from datetime import datetime

from apps import app, db
from flask import render_template, flash, redirect, url_for, request
from apps.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from apps.models import Post
from flask_login import current_user, login_user, logout_user, login_required
# from werkzeug.urls import url_parse
from urllib.parse import urlparse


from apps.models import User


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
# @app.route('/about')
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post is active!")
        return redirect(url_for('index'))

    # posts = current_user.followed_post().all()
    page = request.args.get('page', 1, type=int)
    # posts = current_user.followed_post().paginate(page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None

    return render_template("index.html", title='Home page', posts=posts.items, form=form,
                           next_url=next_url, prev_url=prev_url)

    # posts = [
    #     {
    #         'author': {'username': 'David'},
    #         'body': 'Good sunny day!'
    #     },
    #     {
    #         'author': {'username': 'John'},
    #         'body': 'Bad foggy day!'
    #     }
    # ]


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


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page=page, per_page=app.config['POSTS_PER_PAGE'],
                                                                error_out=False)

    next_url = url_for('user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) if posts.has_prev else None

    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        print(datetime.utcnow())
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your data changed and save!")
        return redirect(url_for('edit_profile'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title="Edit Title", form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f"User {username} not found!")
        return redirect(url_for('index'))
    if user == current_user:
        flash(f"You cannot follow yourself!")
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f"You are following {username}!")
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f"User {username} not found!")
        return redirect(url_for('index'))
    if user == current_user:
        flash(f"You cannot unfollow yourself!")
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f"You aren't following {username}!")
    return redirect(url_for('user', username=username))


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', title="Explore", posts=posts.items, next_url=next_url, prev_url=prev_url)
