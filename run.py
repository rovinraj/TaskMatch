from flask import Flask

app = Flask(__name__)

app.config['SECRET_KEY'] = 'dev_key_change_later'


@app.route('/')
def home():
    return "Flask app is running"


if __name__ == '__main__':
    app.run(debug=True)