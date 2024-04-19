from flask import Flask, request, jsonify, render_template
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return render_template("Home.html")

@app.route('/answers', methods=['GET', 'POST'])
def answers():
    return render_template("Answers.html")

if __name__ == '__main__':
    app.run(debug=True, port=5000)