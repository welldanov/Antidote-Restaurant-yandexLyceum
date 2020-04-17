import os
from os import abort

from sqlalchemy.orm.exc import DetachedInstanceError

from api_directory.api_search import check
from api_directory.api_main import map_photo
import sqlite3
from flask import Flask, render_template, request, make_response, jsonify
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.utils import redirect
from data import db_session
from data.users import User, RegisterForm, LoginForm, HelpForm, Help, ReservationForm, Reservation, RequestForm, Request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/blogs.sqlite")

login_manager = LoginManager()
login_manager.init_app(app)
session_for_api = db_session.create_session()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/main')
def main():
    return render_template('main.html')


@app.route('/reservation', methods=['GET', 'POST'])
def some_reservation():
    form = ReservationForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        print(User.email)
        print(form.email.data)
        if session.query(User).filter(User.email != form.email.data).first():
            print("ok")
            return render_template('reservation.html',
                                   form=form,
                                   message="Неправильный или незарегистрированный логин")
        elif session.query(User).filter(User.id == Reservation.user_id).first():
            print("not")
            return render_template('reservation.html',
                                   form=form,
                                   message="Вы уже забронировали стол")
        class_review = Reservation()
        class_review.table_number = form.res.data
        class_review.count = form.res.data
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


@app.route('/api', methods=['GET', 'POST'])
@login_required
def api():
    place_name = None
    form = RequestForm()
    if form.validate_on_submit():
        try:
            global session_for_api
            session = session_for_api
            class_request = Request()
            session_id = current_user.email

            if session.query(User).filter(User.id).first().email == session_id:
                with sqlite3.connect('db/blogs.sqlite') as con:
                    cur = con.cursor()
                    result = cur.execute(f"""DELETE from request WHERE user_id = {current_user.id}""")
                    cur.close()

            class_request.place = form.place.data
            current_user.request.append(class_request)
            session.merge(current_user)
            session.commit()

            with sqlite3.connect('db/blogs.sqlite') as con:
                cur = con.cursor()
                result = cur.execute("""SELECT * FROM request""").fetchall()
                place_result = cur.execute(f"""SELECT place FROM request WHERE user_id = {current_user.id}""")

            for i in place_result:
                place_name = i[0]

            cur.close()
            print(place_name)

            try:
                # отправляем название города в api_search.py
                coordinates = check(place_name)
                # Урррааа! Идем создавать картинку
                if map_photo(coordinates):
                    map_photo(coordinates)
                    return render_template("api.html", form=form, title="Города | API", message="")
                else:
                    return render_template("api.html", form=form, title="Города | API",
                                           message="Упс. Произошла какая то ошибка. "
                                                   "Попробуйте еще раз!")
            except IndexError:
                return render_template("api.html", title='Города | API', form=form,
                                       message="Название введено не корректно"
                                               " или такого города не существует!")
        except DetachedInstanceError:
            return render_template('error.html')

    return render_template('api.html', title='Города | API',
                           form=form, message="")


def main():
    db_session.global_init("db/blogs.sqlite")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()

# Сделать кнопку выхода для api.html
# Выбрать уже иконку для сайта
# Залить сайт(по возможности)
