from flask import Blueprint
from controllers.transactions import get, insert, upload

transactions = Blueprint('transaction_bp', __name__)

transactions.route('/get', methods=['GET'])(get)
transactions.route('/insert', methods=['POST'])(insert)
transactions.route('/upload', methods=['GET', 'POST'])(upload)
