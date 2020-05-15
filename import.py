import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from psycopg2.errors import UniqueViolation

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#0 query the current schema
def query_schema():
    schema_query = """SELECT *
    FROM
        pg_catalog.pg_tables
    WHERE
        schemaname != 'pg_catalog'
    AND schemaname != 'information_schema';"""
    tables = db.execute(schema_query)
    return tables.fetchall()
#1 Create table
def create_table():
    """
    This function looks if the table 'books'
        already exists in the schema, if not
        it creates it.
    """
    tables = query_schema()
    if any(["books" == x[1] for x in tables]):
         print("Table Already exist")
    else:
        q = """
        CREATE TABLE books (
        isbn VARCHAR PRIMARY KEY,
        title VARCHAR NOT NULL,
        author VARCHAR NOT NULL,
        year INTEGER NOT NULL
        );
        """
        engine.execute(q)
        print("Table books successfully created")

def main():
    """
    insert into table books all
        records form books.csv
    """
    with open("books.csv","r") as f:
        books = csv.reader(f,)
        books =[b for b in books]
        header = books.pop(0)
    errors = list()
    success = 0
    for book in books:
        isbn,title,author,year = book
        try:
            db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                        {"isbn":isbn, "title":title, "author":author, "year":year})
            print(f"added book with isbn {isbn}")
            success+=1
            db.commit()
        except Exception as UniqueViolation:
            print(f"Duplicate error on isbn {isbn}")
            errors.append(book)
    print(f"Added {success} records")
    print(f"During the upload {len(errors)} errors ocurred")
    return success,errors

def status():
    """
    Obtain number of records in db
    """
    c = db.execute("SELECT COUNT(*) FROM books")
    c = c.fetchall()[0][0]
    print(f"Currently the table books has {c} records")
if __name__=="__main__":
    create_table()
    success, errors = main()
    status()
