import os

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# import importBooks2
app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['JSON_SORT_KEYS'] = False

Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# A global variable for the current session to track user
current_user = None


@app.route("/")
def index():
    # importBooks2.some_fun()
    return render_template("index.html")


def query_results(query, m_type):
    if m_type == "isbn" or m_type == "author":
        print("-------calling isbn/author function " + m_type)
        # something to consider is the performance of LOWER on a large database
        values = db.execute(f"select * from books where LOWER({m_type}) like LOWER('{query}%')").fetchall()
        if len(values) == 0:
            return "Sorry no Results!"

        results = ""
        for row in values:
            # different methods to get columns  either by "[i]" or the ".colName"
            results = results + "\n" + f"{row[0]} | {row[1]} | {row.author} | {row.year}"

        return results
    else:
        print("-------calling author function " + m_type)
        values = db.execute(f"select * from books where title  ~* '{query}' ").fetchall()
        print(len(values))
        if len(values) == 0:
            return "Sorry no Results!"

        results = ""
        for row in values:
            # different methods to get columns  either by "[i]" or the ".colName"
            results = results + "\n" + f"{row[0]} | {row[1]} | {row.author} | {row.year}"

        return results


@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        isbn = request.form.get("isbn")
        title = request.form.get("title")
        author = request.form.get("author")
        if isbn is not None and len(isbn) != 0:

            return query_results(isbn, "isbn")
        elif title is not None and len(title) != 0:

            return query_results(title, "title")
        elif author is not None and len(author) != 0:

            return query_results(author, "author")
        else:
            return "No Results, sorry!"

    return render_template("search.html")


@app.route("/register", methods=["POST"])
def hello():
    first = request.form.get("firstName")
    last = request.form.get("lastName")
    myMap = {"first": first, "last": last}
    db.execute("INSERT INTO users(username, password) VALUES  (:first, :last)", myMap)
    return "You typed " + first + " " + last


@app.route("/verify", methods=["POST"])
def verify():
    username = request.form.get("username")
    password = request.form.get("password")
    sql_command = f"select username, password from users where LOWER(username)=LOWER('{username}') AND LOWER(password)=LOWER('{password}')"
    values = db.execute(sql_command).fetchall()
    # values is a "list/array" of sqlAl objects
    # each sqlAlchemy object can be accessed with [i]
    # actually, I don't need username and password because the sql query is already performing those boolean checks
    if len(values) == 1 and username == values[0][0] and password == values[0][1]:
        session[username] = True
        return "You are logged in!"

    return "You are not registered"


@app.route("/secret")
def secret():
    # global variable is the "session" that is a map/dict, i'm using the list function to get a list of the keys in the map
    # as that is the only way one can index the keys; the register maps the username to a boolean true which i check below
    if len(session) != 0 and session[list(session)[0]]:
        return "Secrete Page"
    return "Not logged-in!"


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()  # remove all keys from the map named "session" that is a global variable
    return "logged out!"


@app.route("/api/<string:isbn>")
def api_request(isbn):
    values = db.execute(f" select title, author, year,ratings.isbn, count(rating), avg(rating) from ratings join books "
                        f"on ratings.isbn=books.isbn GROUP BY  title, author, year, ratings.isbn having ratings.isbn='{isbn}'; ").fetchall()
    if len(values) == 0:  # no results found
        return jsonify({"error": "Invalid isbn"}), 404
    some_map={"title": values[0][0], "author": values[0][1], "year": values[0][2], "isbn": isbn,
                    "review_count": values[0][4], "average_score": float(values[0][5])}

    return jsonify(some_map)
