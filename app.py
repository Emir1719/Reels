from flask import Flask
from reels.reels_module import reels

app = Flask(__name__)

app.register_blueprint(reels)

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
