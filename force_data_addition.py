from data import db_session
from data.Admins import Admins
from data.Products import Products
from data.db_session import global_init, create_session


def main():
    global_init("db/base.sqlite")
    session = create_session()
    # admin = Admins()
    # admin.fullname = "Копытов Н. Н"
    # admin.email = "kopytov@yandex.ru"
    # admin.set_password("qwerty123")
    # session.add(admin)
    # session.commit()

    for admin in session.query(Admins).all():
        print(admin)


if __name__ == "__main__":
    main()
