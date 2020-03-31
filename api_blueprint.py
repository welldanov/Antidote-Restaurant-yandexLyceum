import flask
from flask import jsonify, request
from flask import make_response

from data import db_session

blueprint = flask.Blueprint('api_blueprint', __name__,
                            template_folder='templates')