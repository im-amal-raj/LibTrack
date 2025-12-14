import sqlite3

import os

from tabulate import tabulate

from datetime import date, timedelta, datetime


# connect database and create cursor

conn = sqlite3.connect("Library.db")

cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")


# define variable with default value

user_role = "student"


# tabulate table styles

rounded = "rounded_outline"

fancy = "fancy_grid"


# function to create databse first time


def initialize_db():

    cursor.execute(
        """

        CREATE TABLE IF NOT EXISTS books (

            book_id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            author TEXT NOT NULL,

            status TEXT NOT NULL

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

            role TEXT NOT NULL

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

            FOREIGN KEY (book_id) REFERENCES books (book_id),

            FOREIGN KEY (user_id) REFERENCES users (user_id)

        );

        """
    )

    conn.commit()


initialize_db()

# -------------------------------------------------------------------------


# clear screen util function


def clear_screen():

    # For Windows

    if os.name == "nt":

        os.system("cls")

    # For macOS and Linux (posix)

    else:

        os.system("clear")


# ------------------ VALIDATION HELPER FUNCTIONS ------------------


def get_valid_string(prompt):

    while True:

        value = input(prompt).strip()

        if value:

            return value

        else:

            print("Error input cannot be empty please try again.")


def get_valid_int(prompt):

    while True:

        value = input(prompt).strip()

        try:

            return int(value)

        except ValueError:

            print("Error invalid input. Please enter a numeric value.")


def get_valid_choice(prompt, options):

    while True:

        value = input(prompt).strip().lower()

        if value in options:

            return value

        else:

            print(f"Error invalid choice, Please pick one from {options}")


# -------------------------------------------------------------------------


# -------------------------------------------------------------------------


# ------------------------  USER TABLE CRUD   -----------------------------------


# ADD USER FUNCTION


def register():

    clear_screen()

    print("\n---------- Register ----------\n")

    name = get_valid_string("Enter user's name: ")

    username = get_valid_string("Enter user's username(lowercase): ").lower()

    phone = get_valid_string("Enter user's phone number: ")

    password = get_valid_string("Enter user's password: ")

    print("--------------------------\n")

    try:

        cursor.execute(
            "INSERT INTO users (name, username, phone, password, role) VALUES (?, ?, ?, ?, ?)",
            (name, username, phone, password, user_role),
        )

        conn.commit()

        print(f"user {name} registered successfully")

    except sqlite3.IntegrityError:

        print("Error , That username exists . Pick a new username.")


# LOGIN FUNCTION


def login():

    clear_screen()

    global logged_in_user_id

    global logged_in_username

    print("\n---------- Login ----------\n")

    username = get_valid_string("Enter your username: ").lower()

    password = get_valid_string("Enter your password: ")

    result = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password =  ?; ",
        (username, password),
    ).fetchone()

    if result:

        logged_in_user_id = result[0]

        logged_in_username = result[2]

        print(f"Logged in as {result[2]}")

        print("\n---------------------------\n")

    else:

        print("Invalid name or password")

        print("\n---------------------------\n")


# USER REMOVE FUNCTION


def remove_user():

    clear_screen()

    print("\n----------- Delete user ----------")

    username = get_valid_string(
        "Enter the username(lowercase) of the user you want to delete: "
    ).lower()

    if username:

        result = cursor.execute(
            "SELECT * FROM users WHERE username = ?;", (username,)
        ).fetchone()

        if result:

            cursor.execute("DELETE FROM users WHERE username = ?;", (username,))

            print(f"User {result[2]} deleted successfully!!!")

            conn.commit()

        else:

            print("Username not found")


# USER UPDATE FUNCTION


def update_user():

    clear_screen()

    # change name , username , phone , password , role

    username = get_valid_string("Enter your username: ").lower()

    if username:

        user = cursor.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user:

            name = get_valid_string("Enter new name for user: ").strip()

            u_name = get_valid_string("Enter new username for user(lower): ").lower()

            phone = get_valid_string("Enter your phone number: ").strip()

            password = get_valid_string("Enter new password for user: ").strip()

            role = get_valid_choice(
                "Enter new role for user(lower): ", ["student", "admin"]
            ).lower()

            if name and u_name and phone and password and role:

                if role not in ["student", "admin"]:

                    print("Invalid role")

                else:

                    cursor.execute(
                        "UPDATE users SET name = ?, username = ?, phone = ?, password = ?, role =? WHERE user_id = ?",
                        (name, u_name, phone, password, role, user[0]),
                    ).fetchone()

                    conn.commit()

                    print("Updated details successfully")

            else:

                print("Invalid credentials")

        else:

            print("User not found")

    else:

        print("Username cannot be empty")


# USER READ FUNCTION TO LIST ALL USERS


def list_all_users():

    clear_screen()

    print("----------- User List ----------")

    all_users = cursor.execute(
        "SELECT user_id, name, username, phone, role FROM users"
    ).fetchall()

    headers = ["User-ID", "Name", "Username", "Phone", "Role"]

    print(
        tabulate(
            all_users,
            headers=headers,
            tablefmt=fancy,
            showindex=range(1, len(all_users) + 1),
        )
    )


# USER READ FUNCTION TO LIST A SINGLE USER


def user_info():

    clear_screen()

    print("-------------------------------------------------------------")

    username = get_valid_string(
        "Enter the username of the user you want to get the details of: "
    )

    if username:

        user = cursor.execute(
            "SELECT user_id, name, username, phone, role FROM users WHERE username = ? ;",
            (username,),
        ).fetchone()

        if user:

            print("----------- User Info ----------")

            display_data = [user]

            headers = ["User-ID", "Name", "User-Name", "Phone", "Role"]

            print(
                tabulate(
                    display_data,
                    headers=headers,
                    tablefmt=rounded,
                    colalign=["center", "center", "center", "center", "center"],
                )
            )

        else:

            print("User not found")

    else:

        print("Username cannot be empty")


def get_user_details(identifier):

    username = isinstance(identifier, str)

    if username:

        u_name = identifier.strip().lower()

        query = "SELECT * FROM users WHERE username= ?;"

        parameter = (identifier,)

    else:

        try:

            user_id = int(identifier)

        except ValueError:

            print("Invalid user identifier. Please enter a numeric value.")

            return None

        query = "SELECT * FROM users WHERE user_id = ?;"

        parameter = (user_id,)

    user_data = cursor.execute(query, parameter).fetchone()

    if user_data:

        return {
            "id": user_data[0],
            "name": user_data[1],
            "username": user_data[2],
            "phone": user_data[3],
            "password": user_data[4],
            "role": user_data[5].strip().lower(),
        }

    else:

        print(f"User not found {identifier}")

        return None

    # -------------------------------------------------------------------------


# --------------------------   BOOK TABLE CRUD OPERATIONS  ------------------------------------


# BOOK CREATE FUNCTION


def add_book():

    title = get_valid_string("Enter book title: ")

    author = get_valid_string("Enter book author: ")

    if title and author:

        cursor.execute(
            "INSERT INTO books (title, author, status) VALUES (?, ?, ?)",
            (title, author, "available"),
        )

        conn.commit()

        print(f"The Book {title} by {author} is added successfully")

    else:

        print("Title and Author cannot be empty.")


# BOOK READ FUNCTION TO LIST ALL BOOKS


def list_all_books():

    all_books = cursor.execute("SELECT * FROM books").fetchall()

    if all_books:

        headers = ["Id", "Title", "Author", "Status"]

        print(
            tabulate(
                all_books,
                headers=headers,
                tablefmt=fancy,
                colalign=["center", "center", "center", "center"],
            )
        )

    else:

        print("There are no books to display, Add one.")


# BOOK UPDATE FUNCTION TO UPDATE THE DETAILS OF THE BOOK


def update_book():

    clear_screen()

    # change name , username , phone , password , role

    id = get_valid_int("Enter book Id: ")

    if id:

        book = cursor.execute("SELECT * FROM books WHERE book_id = ?", (id,)).fetchone()

        if book:

            header = ["ID", "Title", "Author", "Status"]

            print("\n---------- EXISTING VALUES IN THE DATABASE ----------\n")

            print(tabulate([book], headers=header, tablefmt=rounded))

            title = get_valid_string("\nEnter new title for book: ").strip()

            author = get_valid_string("Enter new author ").strip()

            status = get_valid_choice(
                "Enter book status: ", ["available", "issued"]
            ).strip()

            if title and author and status:

                if status not in ["available", "issued"]:

                    print("Invalid status")

                else:

                    cursor.execute(
                        "UPDATE books SET title = ?, author = ?, status = ? WHERE book_id = ?",
                        (title, author, status, book[0]),
                    ).fetchone()

                    conn.commit()

                    print("Updated details successfully")

            else:

                print("Invalid credentials")

        else:

            print("Book not found")

    else:

        print("Id cannot be empty")


# BOOK DELETE FUNCTION


def remove_book():

    clear_screen()

    print("\n----------- Delete Book ----------")

    book_id = get_valid_int("Enter the ID of the book you want to delete: ")

    if book_id:

        book = cursor.execute(
            "SELECT * FROM books WHERE book_id = ?;", (book_id,)
        ).fetchone()

        header = ["ID", "Title", "Author", "Status"]

        print(tabulate([book], headers=header, tablefmt=rounded))

        if book:

            cursor.execute("DELETE FROM books WHERE book_id = ?;", (book_id,))

            print(f"Book {book[1]} deleted successfully!!!")

            conn.commit()

        else:

            print("Book not found")

    else:

        print("Invalid book id")


# HELPER FUNCTION FOR ISSUE BOOK AND RETURN BOOK FUNCTIONS


def update_book_status(book_id, new_status):

    valid_status = ["available", "issued"]

    new_status = new_status.strip().lower()

    if new_status not in valid_status:

        print(f"invalid status , use one of {valid_status}")

        return False

    try:

        cursor.execute(
            "UPDATE books SET status = ? WHERE book_id = ?;", (new_status, book_id)
        )

        conn.commit()

        return True

    except sqlite3.Error as e:

        print(f"Database error updating status {e}")

        return False


def get_book_details(book_id):

    book_data = cursor.execute(
        "SELECT * FROM books WHERE book_id = ?;", (book_id,)
    ).fetchone()

    if book_data:

        return {
            "id": book_data[0],
            "title": book_data[1],
            "author": book_data[2],
            "status": book_data[3].strip().lower(),
        }

    else:

        print(f"Book with id {book_id} not found.")

        return None


def search_books():

    clear_screen()

    print("\n----------- Search Books ----------")

    keyword = get_valid_string("Enter title or author keyword: ").lower()

    # SQL query using LIKE for partial matching

    query = "SELECT * FROM books WHERE lower(title) LIKE ? OR lower(author) LIKE ?"

    # Add % wildcards for partial match

    results = cursor.execute(query, (f"%{keyword}%", f"%{keyword}%")).fetchall()

    if results:

        headers = ["ID", "Title", "Author", "Status"]

        print(tabulate(results, headers=headers, tablefmt=fancy))

    else:

        print("No books found matching that keyword.")

    input("\nPress Enter to continue...")


# TO DO , VERIFY THE NEED OF CREATING HELPER FUNCTIONS TO CONDUCT USER AND BOOK VALIDATION AND CHECK FOR WAYS TO REDUCE THE NEED FOR INPUT VALIDATION BY CREATING SOME REUSABLE VALIDATION FUNCTIONS OR OTHER METHODS


def issue_book():

    clear_screen()

    print("\n----------- Issue Book ----------")

    book_id = get_valid_int("Enter the id of the book to issue: ")

    user_id = get_valid_int("Enter the id of the user you want to issue the book to: ")

    book = get_book_details(book_id)

    if not book:

        return

    user = get_user_details(user_id)

    if not user:

        return

    if book["status"] != "available":

        print(f"error book{book['title']} (ID {book['id']}) is not available.")

        input("Press Enter to continue...")

        return

    else:

        try:

            today = date.today()

            # ADD 14 days to today

            due_date = today + timedelta(days=14)

            # Convert to string for sqlite

            issue_str = today.strftime("%Y-%m-%d")

            due_str = due_date.strftime("%Y-%m-%d")

            cursor.execute(
                "INSERT INTO loans (book_id, user_id, issue_date, due_date, return_date) VALUES (?, ?, ?, ?, ?)",
                (book["id"], user["id"], issue_str, due_str, ""),
            )

            if not update_book_status(book_id, "issued"):

                conn.rollback()  # undo loan insertion if status update fails

                print("Error: failed to update book status")

                input("Press Enter to continue")

                return

            else:

                print(
                    f"Success book {book['title']} issued to {user['name']} (username: {user['username']} , userId : {user['user_id']})"
                )

                print(f"Deadline:{due_str} (14 Days)")

        except sqlite3.Error as e:

            conn.rollback()

            print(f"Issue failed : database error {e}")

        except Exception as e:

            conn.rollback()

            print(f"Issue failed : {e}")


def calculate_fine(due_date_str):

    try:

        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()

        today = date.today()

        data = (today - due_date).days

        if data > 0:

            fine = data * 1.0

            return fine, data

        else:

            return 0.0, 0

    except ValueError:

        return 0.0, 0


def return_book():

    clear_screen()

    print("\n----------- Return Book ----------")

    book_id = get_valid_int("Enter the ID of the book to return: ")

    book = get_book_details(book_id)

    if not book:

        input("Press enter to continue")

        return

    if book["status"] == "available":

        print("This book is already in the library .")

        input("Press enter to continue")

        return

    active_loan = cursor.execute(
        "SELECT loan_id, user_id, due_date FROM loans WHERE book_id = ? AND return_date = ''",
        (book_id,),
    ).fetchone()

    if not active_loan:

        print("Could not find an active loan record for this book")

        input("Press enter to continue")

        return

    loan_id, user_id, due_date_str = active_loan

    fine_amount, overdue_days = calculate_fine(due_date_str)

    try:

        today = date.today().strftime("%Y-%m-%d")

        cursor.execute(
            "UPDATE loans SET return_date = ? WHERE loan_id =?", (today, loan_id)
        )

        if update_book_status(book_id, "available"):

            conn.commit()

            print(f"Book {book['title']} returned successfully.")

            print(f"Loan closed for user_id {user_id}")

            if fine_amount > 0:

                print(f"Overdue : Book is {overdue_days} days late.")

                print(f"Fine amount : {fine_amount:.2f}")

            else:

                print("Returned on time . No fine.")

        else:

            conn.rollback()

            print("Error updating book status")

    except sqlite3.Error as e:

        conn.rollback()

        print(f"Database error {e}")

    input("Press enter to continue")


def list_all_loans():

    clear_screen()

    print("----------- All Active Loans ----------")

    loans = cursor.execute("SELECT * FROM loans")

    if loans:

        header = ["LOAN-ID", "BOOK-ID", "USER-ID", "ISSUE-DATE", "RETURN-DATE"]

        print(tabulate(loans, headers=header, tablefmt=fancy))


def view_my_loans():

    query = """

        SELECT

            books.title,

            books.author,

            loans.issue_date,

            loans.return_date

        FROM loans

        JOIN books ON loans.book_id = books.book_id

        WHERE loans.user_id = ?

    """

    results = cursor.execute(query, (logged_in_user_id,)).fetchall()

    if results:

        headers = ["Book Title", "Author", "Borrowed On", "Returned On"]

        print(tabulate(results, headers=headers, tablefmt=fancy))

    else:

        print("No loan found for this user.")


def delete_loan():

    clear_screen()

    print("\n----------- ⚠️  DELETE LOAN RECORD (ADMIN) ----------")

    list_all_loans()

    print("-" * 80)

    loan_id = get_valid_int("Enter loan id of the loan you want to delete: ")

    loan = cursor.execute(
        "SELECT book_id, return_date FROM loans WHERE loan_id = ?", (loan_id,)
    ).fetchone()

    if not loan:

        print(f"Error : No loans found for loan id : {loan_id}")

        input("Press enter to continue.....")

        return

    book_id, return_date = loan

    book = get_book_details(book_id)

    if return_date == "" or return_date is None:

        print("You are deleting an active loan")

        print(
            f"Book {book['title']} at book id : ({book['id']}) is currently marked as issued"
        )

        print("Deleting this will mark the book as available.")

        confirm = input("Are you sure you want to proceed (yes/no): ").strip().lower()

        if confirm != "yes":

            print("Deletion cancelled.")

            input("Press Enter.....")

            return

        update_book_status(book_id, "available")

        try:

            cursor.execute("DELETE FROM loans WHERE loan_id = ?", (loan_id,))

            conn.commit()

            print(f"Loan record #{loan_id}has been permenently deleted.")

        except sqlite3.Error as e:

            conn.rollback()

            print(f"Database Error {e}")

        input("Press Enter to continue.....")
