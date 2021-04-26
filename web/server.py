from flask import Flask, render_template, url_for, request, redirect
from data.login_form import LoginForm
from data import db_session
from data.users import User
from data.posts import Posts
from data.add_post_form import AddPostForm
from data.register import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    db_session.global_init('db/users_db.db')
    ses = db_session.create_session()
    posts = ses.query(Posts).all()
    users = ses.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    return render_template('index.html', posts=posts, names=names)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/a', methods=['GET', 'POST'])
@login_required
def a():
    db_session.global_init('db/users_db.db')
    ses = db_session.create_session()
    posts = ses.query(Posts).all()
    users = ses.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    numbers = {numbers.id: numbers.num_posts for numbers in users}
    add_form = AddPostForm()
    if add_form.validate_on_submit():
        db_session.global_init('db/users_db.db')
        db_sess = db_session.create_session()
        post = Posts(post=add_form.post.data, user_id=current_user.id)
        users = db_sess.query(User).all()
        users[current_user.id - 1].num_posts += 1
        db_sess.add(post)
        db_sess.commit()
        return redirect('/a')
    return render_template('a.html', form=add_form, posts=posts, names=names, numbers=numbers)


@app.route('/login', methods=['GET', 'POST'])
def login():
    db_session.global_init('db/users_db.db')
    ses = db_session.create_session()
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.hashed_password == form.password.data:
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register', form=form,
                                   message="Passwords don't match")
        db_session.global_init('db/users_db.db')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Register', form=form,
                                   message="This user already exists")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            hashed_password=form.password.data
        )
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
