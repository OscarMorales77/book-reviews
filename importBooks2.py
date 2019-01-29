import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def mainN():
    f = open("books.csv")

    reader = csv.reader(f, doublequote=True, quoting=csv.QUOTE_ALL, escapechar='\\')
    count = 0
    for isbn, title, author, year in reader:
        myMap = {"isbn": isbn, "title": title, "author": author, "year": year}
        db.execute("INSERT INTO books(isbn, title, author, year) VALUES  (:isbn, :title, :author, :year)", myMap)
        db.commit()

def mainOther():
    username="BOb"
    password="PAsS1v"
    sql_command=f"select username, password from users where LOWER(username)=LOWER('{username}') AND LOWER(password)=LOWER('{password}')"
    values = db.execute(sql_command).fetchall()
    print("the size of values is " + str(len(values)))
    print(values[0][0])
    print(values[0][1])

def main():
    values=db.execute("select * from books where title  ~* 'dEAd' limit 7").fetchall()
    #values2=db.execute("select * from books where LOWER(title) like LOWER('%dead%') ").fetchall()
    results=""
    for row in values:
        results=results+"\n"+f"{row[0]} | {row[1]} | {row.author} | {row.year}"
        #print(f"{row[0]}% --{row[1]}---{row.author}--{row.year}")

    print(results)
def some_fun():
    values=db.execute("select * from books where isbn='ss'").fetchall()
    print((values))
    return print("----------yheeee--------")

def mainGGG():
    query=185798809488
    values = db.execute(f"select * from books where isbn like '{query}%' ").fetchall()

if __name__ == "__main__":
    some_fun()
