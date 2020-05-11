from flask import Flask, render_template, request
from flask_login import login_user, login_manager, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextField
from wtforms.validators import DataRequired, Required

from data import db_session
from data.Admins import Admins
from data.Products import Products
from data.db_session import global_init

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
global_init("db/base.sqlite")
session = db_session.create_session()


@app.route('/')
@app.route('/home')
def home():
    lp = session.query(Products).all()
    print(lp)
    return render_template('home.html', all_products=[[i for i in range(3)] for i in range(5)])


class LoginForm(FlaskForm):
    email = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


def adding_the_product(title, information, cost):
    prod = Products()
    prod.title = title
    prod.information = information
    prod.cost = cost
    session.add(prod)
    session.commit()
    lp = session.query(Products).all()


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(Admins).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = session.query(Admins).filter(Admins.email == form.email.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin, remember=form.remember_me.data)
            return redirect("/admin")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not current_user.is_authenticated:
        login()
    if request.method == 'GET':
        return render_template('add_product.html')
    elif request.method == 'POST':
        print(request.form['title'])
        print(request.form['cost'])
        print(request.form['info'])
        adding_the_product(request.form['title'], request.form['cost'], request.form['info'])
        for prod in session.query(Products).all():
            print(prod.title)
        return "success"
# return render_template('login.html', title='Авторизация', form=form)


@app.route('/admin')
def admin():
    if current_user.is_authenticated:
        return render_template('admin.html', name=current_user.fullname)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
