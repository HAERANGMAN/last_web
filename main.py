from flask import Flask, request, url_for, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as dbb
import pandas as pd
from module import query_sql, chart



app = Flask(__name__)
app.secret_key = 'super secret key'



@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login', methods=['POST'])
def login_():
    request.method = 'POST' 
    if request.form["id_"] == "asd" and request.form["pw_"] == "asd":
        return redirect(url_for("main"))
    else:
        return redirect(url_for("index"))


@app.route('/stock')
def main():
    return render_template("main.html")



if __name__ == '__main__':
    app.run(port=5000, debug=True) #post는 여기로 옴



