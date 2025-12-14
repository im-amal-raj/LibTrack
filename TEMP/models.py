import sqlite3
import TEMP.database as database


conn = sqlite3.connect("Library.db")
cursor = conn.cursor()


class Book:
    def __init__(self, book_id, title, author, status):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.status = status

    def add_book(self):

        cursor.execute(
            "INSERT INTO books (title, author, status) VALUES (?, ?, ?)",
            (self.title, self.author, self.status),
        )

        conn.commit()


class Member:
    def __init__(self, member_id, name, phone):
        self.member_id = member_id
        self.name = name
        self.phone = phone


def get_all_books():
    conn = sqlite3.connect("Library.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()

    conn.close()

    return rows


def issue_book(book_id, member_id):
    conn = sqlite3.connect("Library.db")
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM books WHERE book_id = ?", (book_id,))
    result = cursor.fetchone()
    if result == None or result[0] != "Available":
        conn.close()
        return False
    else:
        cursor.execute(
            "UPDATE books SET status = ? WHERE book_id = ?", ("Issued", book_id)
        )
        cursor.execute(
            "INSERT INTO loans (book_id, member_id, issue_date, return_date) VALUES (?, ?, ?, ?)",
            (book_id, member_id, "04-12-2025", "10-12-2025"),
        )
        conn.commit()
        conn.close()
        return True
