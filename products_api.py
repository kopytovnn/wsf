import flask
from flask import jsonify, Flask

from data import db_session
from data.Products import Products

blueprint = flask.Blueprint('products_api', __name__,
                            template_folder='templates')


app = Flask(__name__)


@blueprint.route('/api/products')
def get_products():
    session = db_session.create_session()
    products = session.query(Products).all()
    return jsonify(
        {

            'products':
                [item.to_dict(only=('title', 'cost')) for item in products]
        }
    )

