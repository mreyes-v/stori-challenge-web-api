from flask import Flask
from routes.transactions import transactions

app = Flask(__name__)

app.register_blueprint(transactions, url_prefix='/transactions')

app.config["JSON_SORT_KEYS"] = False


@app.route("/")
def hello_world():
    return "Server is up", 200


if __name__ == "__main__":
    app.run(host='0.0.0.0')
