import os, requests

from flask import Flask, session, render_template, request, jsonify, redirect, url_for

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
    return render_template("index.html")


def query_results(query, m_type):
    if m_type == "isbn" or m_type == "author":
        print("-------calling isbn/author function " + m_type)
        # something to consider is the performance of LOWER on a large database
        values = db.execute(f"select * from books where LOWER({m_type}) like LOWER('{query}%')").fetchall()

        return render_template("results.html", num_results=len(values), values=values, user_name=session["user"])
    else:
        values = db.execute(f"select * from books where title  ~* '{query}' ").fetchall()

        return render_template("results.html", num_results=len(values), values=values, user_name=session["user"])


# @app.route("/verify", methods=["GET"])
@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        isbn = request.form.get("isbn")
        title = request.form.get("title")
        author = request.form.get("author")

        if len(isbn) != 0 and len(title) == 0 and len(author) == 0:
            print("isb search")
            return query_results(isbn, "isbn")
        elif len(title) != 0 and (len(author) == 0 and len(isbn) == 0):
            print("title search")
            return query_results(title, "title")
        elif len(author) != 0 and (len(title) == 0 and len(isbn) == 0):
            print("author search")
            return query_results(author, "author")
        else:
            return "Sorry, only one input field must be submitted"
    elif request.method == "GET" and "user" in session.keys() and session[session["user"]]:
        return render_template("search.html", user_name=session["user"])
    else:
        return render_template("404.html", logOut=False)


@app.route("/register", methods=["POST"])
def hello():
    first = request.form.get("firstName")
    last = request.form.get("lastName")
    myMap = {"first": first, "last": last}
    db.execute("INSERT INTO users(username, password) VALUES  (:first, :last)", myMap)
    db.commit()
    return render_template("confirm.html")


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
        session["user"] = username
        # return render_template("search.html", user_name=username)
        return redirect(url_for('search'))

    return render_template("404.html", logOut=True)


@app.route("/secret")
def secret():
    # global variable is the "session" that is a map/dict, i'm using the list function to get a list of the keys in the map
    # as that is the only way one can index the keys; the register maps the username to a boolean true which i check below
    if len(session) != 0 and session[list(session)[0]]:
        return "Secrete Page"
    return render_template("404.html", logOut=False)


@app.route("/logout", methods=["POST"])
def logout():
    name = session["user"]
    session.clear()  # remove all keys from the map named "session" that is a global variable
    return render_template("logout.html", user_name=name)


@app.route("/api/<string:isbn>")
def api_request(isbn):
    values = db.execute(f"select title, author, year,books.isbn, count(rating), avg(rating) from books left join ratings on ratings.isbn=books.isbn GROUP BY  title, author, year, books.isbn having books.isbn='{isbn}'").fetchall()
    print(values)
    if len(values) == 0:  # no results found
        return jsonify({"error": "Invalid isbn"}), 404
    average=values[0][5]
    if values[0][5] is None:
        average=0
    some_map = {"title": values[0][0], "author": values[0][1], "year": values[0][2], "isbn": isbn,
                "review_count": values[0][4], "average_score": float(average)}

    return jsonify(some_map)


@app.route("/books/<string:isbn>")
def book_page(isbn):
    values = db.execute(
        f" select title, author, year, comments,rating from ratings right join books on ratings.isbn=books.isbn where books.isbn='{isbn}'; ").fetchall()
    # print(values[0])
    # print(len(values))
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "DYmLgmG4nZ3cduTe4NgFg", "isbns": isbn})
    data = res.json()
    print(res.status_code)
    print(values)
    get_more = False
    if len(values) > 1:
        get_more = True

    return render_template("bookpage.html", row=values[0], results=values, isbn=isbn, get_more=get_more,
                           status_code=res.status_code, api=data["books"][0], user_name=session["user"])


@app.route("/review", methods=["POST"])
def review_page():
    comments = request.form.get("comments")
    rating = request.form.get("rating")
    isbn = request.form.get("isbn")
    print(f"select * from books where isbn='{isbn}' and username='{session['user']}'")
    value = db.execute(f"select * from ratings where isbn='{isbn}' and username='{session['user']}'").fetchall()
    print(value)
    if len(value) == 1:
        return render_template("searhConfirm.html", user_name=session["user"], num_results=len(value))
    print(
        f"INSERT INTO ratings (rating, isbn, username, comments) VALUES ({rating},'{isbn}','{session['user']}', '{comments}')")
    db.execute(
        f"INSERT INTO ratings (rating, isbn, username, comments) VALUES ({rating},'{isbn}','{session['user']}', '{comments}')")
    db.commit()
    return render_template("searhConfirm.html", user_name=session["user"])
