import sqlite3

conn = sqlite3.connect("Library.db")
cursor = conn.cursor()


def initialize_db():

    print("Database connected successfully")

    cursor.execute(
        """ 
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            status TEXT
)
"""
    )
    cursor.execute(
        """ 
        CREATE TABLE IF NOT EXISTS members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT
)
"""
    )
    cursor.execute(
        """ 
        CREATE TABLE IF NOT EXISTS loans (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            member_id INTEGER,
            FOREIGN KEY (book_id) REFERENCES books (book_id),
            FOREIGN KEY (member_id) REFERENCES members (member_id),
            issue_date TEXT,
            return_date TEXT
)
"""
    )
    conn.commit()
    conn.close()
