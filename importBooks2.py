import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))

db = scoped_session(sessionmaker(bind=engine))


def main():
    f = open("books.csv")

    reader = csv.reader(f, doublequote=True, quoting=csv.QUOTE_ALL, escapechar='\\')
    count = 0
    for isbn, title, author, year in reader:
        myMap = {"isbn": isbn, "title": title, "author": author, "year": year}
        db.execute("INSERT INTO books(isbn, title, author, year) VALUES  (:isbn, :title, :author, :year)", myMap)
        db.commit()


if __name__ == "__main__":
    main()
