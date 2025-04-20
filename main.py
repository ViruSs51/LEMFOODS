from flask import Flask
from flask import render_template


app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template('main/home.html')

@app.route('/catalog')
def catalog():
    return render_template('main/catalog.html')
