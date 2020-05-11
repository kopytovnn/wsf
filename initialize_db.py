from data.db_session import global_init, create_session


global_init("db/base.sqlite")
session = create_session()
