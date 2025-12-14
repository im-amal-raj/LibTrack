import sqlite3
import os
from tabulate import tabulate
from datetime import date, timedelta, datetime

# connect database and create cursor
conn = sqlite3.connect("Library.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")


# tabulate table styles
rounded = "rounded_outline"
fancy = "fancy_grid"


def initialize_db():
    cursor.execute(
        """ 
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('available', 'issued')) 
            );
            """
    )
    conn.commit()
    cursor.execute(
        """ 
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('student', 'admin'))
            );
            """
    )
    conn.commit()
    cursor.execute(
        """ 
        CREATE TABLE IF NOT EXISTS loans (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            FOREIGN KEY (book_id) REFERENCES books (book_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()


initialize_db()
