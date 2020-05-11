from flask import Flask
from flask_mail import Mail
from flask_mail import Message
from data import db_session
from data.db_session import global_init

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['MAIL_SERVER'] = 'smtp.yandex.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'ncopitovflaskmail'
app.config['MAIL_PASSWORD'] = 'flaskmailpassword'


mail = Mail(app)

global_init("db/base.sqlite")
session = db_session.create_session()

# administrator list
ADMINS = ['ncopitovflaskmail@yandex.ru']


def send(id, tel):
    if not tel:
        return "Error"
    msg = Message('Покупатель {tel} приобрел {id}'.format(
                  tel=str(tel),
                  id=str(id)),
                  sender=ADMINS[0],
                  recipients=ADMINS)
    with app.app_context():
        mail.send(msg)
    return "success"
