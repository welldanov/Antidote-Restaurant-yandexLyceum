import datetime
import sqlalchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    review = orm.relation("Help", back_populates='user')
    reservation = orm.relation("Reservation", back_populates="user")

    def __repr__(self):
        return "<User(email='%s')>" % (
            self.email)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class Help(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'help'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')

    def __repr__(self):
        return "<Help(title='%s', content='%s', created_date='%s', user_id='%s')>" % (
            self.title, self.content, self.created_date, self.user_id)


class Reservation(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'reservation'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    table_number = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    count = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')

    def __repr__(self):
        return "<Reservation(email='%s', created_date='%s', user_id='%s', table_number='%s', count='%s')>" % (
            self.email, self.created_date, self.user_id, self.table_number, self.count)


class RegisterForm(FlaskForm):
    email = EmailField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    password_again = PasswordField(validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class HelpForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание", validators=[DataRequired()])
    submit = SubmitField('Отправить')


class ReservationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    res = SelectField('Select', choices=[
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
        ("6 VIP", "6 VIP"),
        ("7", "7"),
        ("8", "8"),
        ("9 VIP", "9 VIP"),
        ("10", "10")])
    count_of_people = SelectField('Select', default="4", choices=[
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
        ("6", "6")])
    submit = SubmitField('Отправить')
