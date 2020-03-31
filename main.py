from os import abort

from flask import Flask, render_template, request, make_response, jsonify
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.utils import redirect

import api_blueprint
from data import db_session
from data.users import User, RegisterForm, LoginForm, HelpForm, Help, ReservationForm, Reservation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/blogs.sqlite")

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/reservation', methods=['GET', 'POST'])
def some_reservation():
    form = ReservationForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        if session.query(User).filter(User.email != form.email.data).first():
            return render_template('reservation.html',
                                   form=form,
                                   message="Неправильный или незарегистрированный логин")
        if session.query(User).filter(User.id == Reservation.user_id).first():
            return render_template('reservation.html',
                                   form=form,
                                   message="Вы уже забронировали стол")
        class_review = Reservation()
        class_review.table_number = form.res.data
        current_user.reservation.append(class_review)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('reservation.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/reviews', methods=['GET', 'POST'])
@login_required
def add_reviews():
    form = HelpForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        class_review = Help()
        class_review.title = form.title.data
        class_review.content = form.content.data
        current_user.review.append(class_review)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('reviews.html', title='Antidote',
                           form=form)


def main():
    db_session.global_init("db/blogs.sqlite")
    app.register_blueprint(api_blueprint.blueprint)
    app.run(debug=True)


if __name__ == '__main__':
    main()
