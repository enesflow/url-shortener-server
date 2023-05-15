from flask import Flask, request, render_template, send_file, redirect, url_for
from flask_cors import CORS
import sqlite3
import random
import os
app = Flask(__name__)
CORS(app)

base_url = "http://go.kavcakar.com.tr"
#base_url = os.environ.get("BASE_URL", "http://localhost:5000")
print(base_url)

with sqlite3.connect("database.sqlite") as conn:
    c = conn.cursor()
    c.execute(
        "CREATE TABLE IF NOT EXISTS urls (url TEXT, short TEXT, visits INTEGER DEFAULT 0)"
    )
    conn.commit()


def random_uuid(length=4):
    return "".join(
        random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
        for _ in range(length)
    )


def _create_url(url, short):
    with sqlite3.connect("database.sqlite") as conn:
        c = conn.cursor()
        if short == "":
            short = random_uuid()
        #  check if short already exists
        c.execute("SELECT url FROM urls WHERE short=?", (short,))
        already_exists = c.fetchone()
        if already_exists:
            return {"short": "", "error": "already exists"}, 400
        # insert url
        c.execute(
            "INSERT INTO urls (url, short, visits) VALUES (?, ?, ?)", (url, short, 0)
        )
        conn.commit()
        # return json
        return {"short": base_url + "/" + short, "error": None}, 200


@app.route("/create", methods=["POST"])
def create_url():
    url = request.json["url"]
    short = request.json["short"]
    return _create_url(url, short)


@app.route("/<string:short>", methods=["GET"])
def get_url(short):
    #  print ip
    print(request.remote_addr)
    with sqlite3.connect("database.sqlite") as conn:
        c = conn.cursor()
        c.execute("SELECT url FROM urls WHERE short=?", (short,))
        url = c.fetchone()
        if url:
            #  increment visits
            c.execute("UPDATE urls SET visits = visits + 1 WHERE short=?", (short,))
            conn.commit()
            #  redirect
            return redirect(url[0], code=302)
        else:
            return "Not found", 404


@app.route("/stats/<string:short>", methods=["GET"])
def get_stats(short):
    with sqlite3.connect("database.sqlite") as conn:
        c = conn.cursor()
        c.execute("SELECT url, visits FROM urls WHERE short=?", (short,))
        url = c.fetchone()
        if url:
            return {"url": url[0], "visits": url[1]}, 200
        else:
            return "Not found", 404


@app.route("/file/<string:filename>", methods=["GET"])
def get_file(filename):
    return send_file("files/" + filename)


@app.route("/upload", methods=["POST"])
def upload_file():
    short = request.form["short"]

    # check if already exists
    with sqlite3.connect("database.sqlite") as conn:
        c = conn.cursor()
        c.execute("SELECT url FROM urls WHERE short=?", (short,))
        already_exists = c.fetchone()
        if already_exists:
            return {"short": "", "error": "already exists"}, 400

    file = request.files["file"]
    uuid = random_uuid(length=32)
    file.save("files/" + uuid + "-" + file.filename)
    return _create_url(base_url + "/file/" + uuid + "-" + file.filename, short)


# @app.route("/", methods=["GET"])
# def index():
#     return render_template("Create.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
