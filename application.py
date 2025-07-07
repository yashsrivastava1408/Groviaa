from flask import Flask
import os


from flask_bootstrap import Bootstrap
from flask_restful import Api

current_dir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = 'static/assets/'

app = Flask(__name__, static_url_path='/static')

# API setup
from api import CategoryAPI, ProductAPI

api = Api(app)
api.add_resource(CategoryAPI, '/api/category', '/api/category/<int:category_id>')
api.add_resource(ProductAPI, '/api/product', '/api/product/<int:product_id>')

# Configurations
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Routes
from authentication import *
from admin_routes import *
from user_routes import *

# Main
if __name__ == '__main__':
    Bootstrap(app)
    app.run(host='0.0.0.0', port=5001, debug=True)