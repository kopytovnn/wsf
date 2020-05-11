import datetime
import os
import flask

from flask import Flask, render_template, request, url_for, make_response, jsonify
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm

from werkzeug.utils import redirect
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

import products_api
from data import db_session
from data.Admins import Admins
from data.Products import Products
from data.db_session import global_init

from mail import send
from vk import postVK

UPLOAD_FOLDER = 'static/img/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)


global_init("db/blogs.sqlite")
session = db_session.create_session()
app.register_blueprint(products_api.blueprint)


@app.route('/')
@app.route('/home')
def home():
    a_p = [[]]
    for prod in session.query(Products).all():
        if len(a_p[-1]) < 3:
            a_p[-1].append(prod)
        else:
            a_p.append([prod])

    return render_template('home.html', all_products=a_p)


class LoginForm(FlaskForm):
    email = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


def adding_the_product(title, information, cost, filename):
    prod = Products()
    prod.title = title
    prod.information = information
    prod.cost = cost
    prod.photos = filename
    session.add(prod)
    session.commit()
    postVK(text=title + "\n" + information + "\n" + cost, photo=UPLOAD_FOLDER + filename)
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
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('add_product.html')

    elif request.method == 'POST':

        title = request.form['title']
        info = request.form['info']
        cost = request.form['cost']

        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = title.replace(" ", "").replace("/", "") + ".png"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        adding_the_product(title, info, cost, filename)

        return render_template('home.html')

    # return render_template('login.html', title='Авторизация', form=form)


@app.route('/admin')
def admin():
    if current_user.is_authenticated:
        return render_template('admin.html', name=current_user.fullname)

    return redirect(url_for('login'))


@app.route('/home/product/<number>')
def product(number):
    prod = session.query(Products).filter(Products.id == number).first()
    print(prod.photos)
    return render_template('product.html', product=prod)


@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect("/")


@app.route('/json')
def json():
    return render_template('json.html')


@app.route('/add_in_favourites/<w>')
def add_in_favourites(w):
    flask.session.permanent = True
    if 'chosen' in flask.session:
        flask.session['chosen'] = flask.session['chosen'] + ' ' + str(w)
        print(flask.session['chosen'])
    else:
        flask.session['chosen'] = ''
    return "nothing"


@app.route('/dell_from_favourites/<w>')
def dell_from_favourites(w):
    flask.session.permanent = True
    if 'chosen' in flask.session:
        flask.session['chosen'] = flask.session['chosen'].replace(str(w), "")
        print(flask.session['chosen'])
    else:
        flask.session['chosen'] = ''
    return ""


@app.route('/favorite')
def favorite():
    a_p = [[]]
    if flask.session:
        l1 = [int(i) for i in flask.session['chosen'].split()]
        for prod in session.query(Products):
            if prod.id in l1:
                if len(a_p[-1]) < 3:
                    a_p[-1].append(prod)
                else:
                    a_p.append([prod])

    return render_template('favourites.html', all_products=a_p)


@app.route('/test')
def test():
    return render_template('test.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


from flask import send_from_directory


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/checkout/<id>', methods=['GET', 'POST'])
def checkout(id):
    if request.method == 'GET':
        product = session.query(Products). \
            filter(Products.id == id).first()
        return render_template("checkout.html", product=product)
    elif request.method == 'POST':
        print(request.form['tel'])
        tel = request.form['tel']
        send(tel=tel, id=id)
        return redirect("https://money.yandex.ru/quickpay/confirm.xml")


@app.route('/aboutus')
def aboutus():
    return render_template("aboutus.html")


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
