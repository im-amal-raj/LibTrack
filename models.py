import sqlite3
from datetime import date, timedelta, datetime
from tabulate import tabulate
import questionary
from utils import (
    clear_screen,
    get_valid_string,
    get_valid_int,
    get_valid_choice,
    calculate_fine,
    get_validated_input,
    validate_username_format
    
)


class LibraryManager:
    def __init__(self, db_name="test.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")

        # STATE: Tracks who is logged in
        self.current_user_id = None
        self.current_user_role = None
        self.current_user_name = None

        self.initialize_db()

    def initialize_db(self):
        """Creates tables if they don't exist."""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                status TEXT NOT NULL
            )"""
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )"""
        )
        self.cursor.execute(
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
            )"""
        )
        # NOTIFICATIONS TABLE (The "Inbox")
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                loan_id INTEGER NOT NULL,
                type TEXT NOT NULL,          -- e.g., 'DUE_TODAY', 'OVERDUE'
                message TEXT NOT NULL,
                status TEXT DEFAULT 'unread', -- 'unread', 'read', 'resolved'
                created_at TEXT NOT NULL,
                FOREIGN KEY (loan_id) REFERENCES loans (loan_id)
            );
        """
        )

        self.conn.commit()

    # ========================== USER MANAGEMENT ==========================

    def login(self):
        clear_screen()
        print("\n---------- Login ----------")
        username = get_valid_string("Username: ").lower()
        password = get_valid_string("Password: ")

        user = self.cursor.execute(
            "SELECT user_id, role, name FROM users WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()

        if user:
            self.current_user_id = user[0]
            self.current_user_role = user[1]
            self.current_user_name = user[2]
            print(f"Logged in as {user[2]}")
            return True
        else:
            print("Invalid credentials.")
            input("Press Enter...")
            return False

    def logout(self):
        self.current_user_id = None
        self.current_user_role = None
        self.current_user_name = None

    def register_user(self):
        clear_screen()
        print("\n---------- Register User ----------")
        name = get_valid_string("Name: ")
        username = get_validated_input("Enter Username: ", validate_username_format)
        phone = get_valid_string("Phone: ")
        password = get_valid_string("Password: ")

        try:
            self.cursor.execute(
                "INSERT INTO users (name, username, phone, password, role) VALUES (?, ?, ?, ?, 'student')",
                (name, username, phone, password),
            )
            self.conn.commit()
            print(f"User {name} registered successfully.")
        except sqlite3.IntegrityError:
            print("Error: Username already exists.")
        input("Press Enter...")

    def list_all_users(self):
        clear_screen()
        users = self.cursor.execute(
            "SELECT user_id, name, username, phone, role FROM users"
        ).fetchall()
        print(
            tabulate(
                users,
                headers=["ID", "Name", "Username", "Phone", "Role"],
                tablefmt="fancy_grid",
            )
        )
        input("Press Enter...")

    def update_user(self, prefilled_username=None):
        clear_screen()
        print("\n---------- Update User ----------")
        
        # 1. Determine which username to look up
        if prefilled_username:
            target_username = prefilled_username
            print(f"Updating User: {target_username}")
        else:
            target_username = get_valid_string("Enter username to update: ").lower()

        # 2. FETCH DATA (Runs for BOTH cases now)
        user = self.cursor.execute(
            "SELECT * FROM users WHERE username=?", (target_username,)
        ).fetchone()

        if not user:
            print(f"User '{target_username}' not found.")
            input("Press Enter...")
            return

        # Unpack current values
        # Schema: (user_id, name, username, phone, password, role)
        u_id, u_name, u_username, u_phone, u_pass, u_role = user

        print(f"\nUpdating: {u_name} ({u_role})")
        print("(Press Enter to keep current value)")

        # 2. Get Inputs (unchanged logic)
        new_name = input(f"New Name [{u_name}]: ").strip() or u_name
        new_username = input(f"New Username [{u_username}]: ").strip().lower() or u_username
        new_phone = input(f"New Phone [{u_phone}]: ").strip() or u_phone
        new_pass = input(f"New Password [{u_pass}]: ").strip() or u_pass
            
        # 3. ROLE UPDATE - CRITICAL SECURITY CHECK
        print(f"Current Role: {u_role}")
        new_role = input(f"New Role (student/admin) [{u_role}]: ").strip().lower()
            
        if not new_role:
            new_role = u_role # Keep existing if empty

        if new_role not in ['student', 'admin']:
            print("Invalid role. Keeping old role.")
            new_role = u_role

        # --- GUARDRAIL: LAST ADMIN CHECK ---
        # If we are changing an 'admin' to 'student', check if they are the LAST one.
        if u_role == 'admin' and new_role == 'student':
            admin_count = self.cursor.execute(
                "SELECT COUNT(*) FROM users WHERE role='admin'"
            ).fetchone()[0]
                
            if admin_count <= 1:
                print("\n❌ CRITICAL ERROR: You cannot downgrade the last Administrator.")
                print("Create another Admin account first before demoting this one.")
                input("Press Enter to cancel...")
                return

        # 4. Perform Update
        try:
            self.cursor.execute(
                "UPDATE users SET name=?, username=?, phone=?, password=?, role=? WHERE user_id=?",
                (new_name, new_username, new_phone, new_pass, new_role, u_id),
            )
            self.conn.commit()
            print("User updated successfully.")
                
            # Special Case: If you downgraded YOURSELF, you should probably be logged out
            if u_id == self.current_user_id and new_role == 'student':
                print("⚠️ You have downgraded your own account.")
                print("You will now be logged out to apply permissions.")
                self.logout()
                    
        except sqlite3.IntegrityError:
            print("Error: Username taken.")
                
        input("Press Enter...")

    def remove_user(self):
        clear_screen()
        print("\n---------- Delete User ----------")
        username = get_valid_string("Enter username to delete: ").lower()

        # 1. FETCH TARGET USER DETAILS
        # We need their ID and Role to check rules
        user = self.cursor.execute(
            "SELECT user_id, role FROM users WHERE username=?", (username,)
        ).fetchone()

        if not user:
            print("User not found.")
            input("Press Enter...")
            return

        target_user_id, target_user_role = user

        # --- GUARDRAIL 1: PREVENT SELF-DELETION ---
        if target_user_id == self.current_user_id:
            print("❌ Error: You cannot delete your own account while logged in.")
            input("Press Enter...")
            return

        # --- GUARDRAIL 2: PREVENT DELETING LAST ADMIN ---
        if target_user_role == 'admin':
            admin_count = self.cursor.execute(
                "SELECT COUNT(*) FROM users WHERE role='admin'"
            ).fetchone()[0]
            
            if admin_count <= 1:
                print("❌ Error: Safety Lock. You cannot delete the last Administrator.")
                input("Press Enter...")
                return

        # --- GUARDRAIL 3: PREVENT DELETING USER WITH BOOKS ---
        # Check if they have loans where return_date is empty/active
        active_loans = self.cursor.execute(
            "SELECT COUNT(*) FROM loans WHERE user_id=? AND return_date=''", 
            (target_user_id,)
        ).fetchone()[0]

        if active_loans > 0:
            print(f"❌ Error: This user has {active_loans} active loan(s).")
            print("They must return all books before their account can be deleted.")
            input("Press Enter...")
            return

        # --- IF ALL CHECKS PASS, EXECUTE DELETE ---
        confirm = input(f"⚠️ Are you sure you want to delete {username}? (yes/no): ")
        if confirm.lower() == "yes":
            # Optional: Delete their history (closed loans) or keep it anonymized?
            # For this project, we delete their history to keep the DB clean.
            self.cursor.execute("DELETE FROM loans WHERE user_id=?", (target_user_id,))
            self.cursor.execute("DELETE FROM users WHERE user_id=?", (target_user_id,))
            self.conn.commit()
            print("User deleted successfully.")
        else:
            print("Operation cancelled.")
            
        input("Press Enter...")

    # ========================== BOOK OPERATIONS ==========================

    def add_book(self):
        clear_screen()
        print("\n---------- Add Book ----------")
        title = get_valid_string("Title: ")
        author = get_valid_string("Author: ")
        self.cursor.execute(
            "INSERT INTO books (title, author, status) VALUES (?, ?, 'available')",
            (title, author),
        )
        self.conn.commit()
        print("Book added successfully.")
        input("Press Enter...")

    def list_all_books(self):
        clear_screen()
        books = self.cursor.execute("SELECT * FROM books").fetchall()
        if books:
            print(
                tabulate(
                    books,
                    headers=["ID", "Title", "Author", "Status"],
                    tablefmt="fancy_grid",
                )
            )
        else:
            print("No books found.")
        input("Press Enter...")

    def search_books(self):
        clear_screen()
        print("\n---------- Search Books ----------")
        kw = get_valid_string("Enter keyword: ").lower()
        books = self.cursor.execute(
            "SELECT * FROM books WHERE lower(title) LIKE ? OR lower(author) LIKE ?",
            (f"%{kw}%", f"%{kw}%"),
        ).fetchall()
        if books:
            print(
                tabulate(
                    books,
                    headers=["ID", "Title", "Author", "Status"],
                    tablefmt="fancy_grid",
                )
            )
        else:
            print("No matches found.")
        input("Press Enter...")

    def update_book(self, prefilled_book_id=None):
        clear_screen()
        print("\n---------- Update Book ----------")
        if prefilled_book_id:
            book_id = prefilled_book_id
            print(f"Editing Book ID: {book_id}")
        else:
            book_id = get_valid_int("Book ID: ")
            book = self.cursor.execute(
                "SELECT * FROM books WHERE book_id=?", (book_id,)
            ).fetchone()

            if not book:
                print("Book not found.")
                input("Press Enter...")
                return

            title = get_valid_string(f"New Title [{book[1]}]: ")
            author = get_valid_string(f"New Author [{book[2]}]: ")
            status = get_valid_choice(
                f"New Status [{book[3]}] (available/issued): ", ["available", "issued"]
            )

            self.cursor.execute(
                "UPDATE books SET title=?, author=?, status=? WHERE book_id=?",
                (title, author, status, book_id),
            )
            self.conn.commit()
            print("Book updated.")
            input("Press Enter...")

    def remove_book(self, prefilled_book_id=None):
        clear_screen()
        print("\n---------- Delete Book ----------")
        if prefilled_book_id:
            book_id = prefilled_book_id
            print(f"Deleting Book ID: {book_id}")
        else:
            book_id = get_valid_int("Book ID to delete: ")

        book = self.cursor.execute(
            "SELECT title, status FROM books WHERE book_id = ?;", (book_id,)
        ).fetchone()
        if not book:
            print("Book not found")
            input("Press Enter to continue.....")
            return

        title, status = book

        if status == "issued":
            print(f"Error cannot delete {title} , because the book is already issued.")
            print("The book must be returned before you can delete it.")
            input("Press Enter.....")
            return

        history_count = self.cursor.execute(
            "SELECT COUNT(*) FROM loans WHERE book_id = ?;", (book_id,)
        ).fetchone()[0]

        if history_count > 0:
            print(f"This book has {history_count} past loan records.")
            print("Deleting this book will permanantly erase its entire loan history.")
            confirm = input("Are you sure? (yes/no): ").strip().lower()

            if confirm != "yes":
                print("Deletion cancelled.")
                input("Press Enter.....")
                return

            try:
                self.cursor.execute("DELETE FROM loans WHERE book_id = ?", (book_id,))
                print(f"History cleared ({history_count} records).")
            except sqlite3.Error as e:
                print(f"Error clearing history: {e}")
                input("Press Enter.....")
                return
            try:
                self.cursor.execute("DELETE FROM books WHERE book_id = ?;", (book_id,))
                print(f"Book deleted successfully.")
                self.conn.commit()
            except sqlite3.Error as e:
                self.conn.rollback()
                print(f"Error deleting book: {e}")
                input("Press Enter.....")

            input("Press Enter.....")

    # ========================== LOAN OPERATIONS ==========================

    def _update_book_status(self, book_id, status):
        try:
            self.cursor.execute(
                "UPDATE books SET status=? WHERE book_id=?", (status, book_id)
            )
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def issue_book(self, prefilled_book_id=None):
        clear_screen()
        print("\n---------- Issue Book ----------")
        # If ID was passed from Search, use it. Otherwise, ask user.
        if prefilled_book_id:
            book_id = prefilled_book_id
            print(f"Selected Book ID: {book_id}")
        else:
            book_id = get_valid_int("Book ID: ")
            user_id = get_valid_int("User ID: ")

            # Validate Book
            book = self.cursor.execute(
                "SELECT title, status FROM books WHERE book_id=?", (book_id,)
            ).fetchone()
            if not book:
                return print("Book not found.") or input()
            if book[1] != "available":
                return print("Book is not available.") or input()

            # Validate User
            user = self.cursor.execute(
                "SELECT name FROM users WHERE user_id=?", (user_id,)
            ).fetchone()
            if not user:
                return print("User not found.") or input()

            try:
                today = date.today()
                due = today + timedelta(days=14)

                self.cursor.execute(
                    "INSERT INTO loans (book_id, user_id, issue_date, due_date, return_date) VALUES (?, ?, ?, ?, '')",
                    (
                        book_id,
                        user_id,
                        today.strftime("%Y-%m-%d"),
                        due.strftime("%Y-%m-%d"),
                    ),
                )

                if self._update_book_status(book_id, "issued"):
                    print(f"Book '{book[0]}' issued to {user[0]}. Due: {due}")
                else:
                    self.conn.rollback()
                    print("Error updating status.")
            except Exception as e:
                self.conn.rollback()
                print(f"Error: {e}")
            input("Press Enter...")

    def return_book(self):
        clear_screen()
        print("\n---------- Return Book ----------")
        book_id = get_valid_int("Book ID to return: ")

        loan = self.cursor.execute(
            "SELECT loan_id, due_date, user_id FROM loans WHERE book_id=? AND return_date=''",
            (book_id,),
        ).fetchone()

        if not loan:
            print("No active loan found for this book.")
            input("Press Enter...")
            return

        loan_id, due_date, user_id = loan
        fine, days = calculate_fine(due_date)

        try:
            self.cursor.execute(
                "UPDATE loans SET return_date=? WHERE loan_id=?",
                (date.today().strftime("%Y-%m-%d"), loan_id),
            )
            if self._update_book_status(book_id, "available"):

                self.cursor.execute(
                    "UPDATE notifications SET status = 'resolved' WHERE loan_id = ?",
                    (loan_id,),
                )
                self.conn.commit()
                print("Book returned successfully.")
                if fine > 0:
                    print(f"⚠️  OVERDUE by {days} days. Fine: ${fine}")
                else:
                    print("Returned on time.")
            else:
                self.conn.rollback()
        except Exception as e:
            self.conn.rollback()
            print(f"Error: {e}")
        input("Press Enter...")

    def list_all_loans(self):
        clear_screen()
        print("\n----------- All Loan Records ----------")

        # WE UPDATED THIS QUERY:
        # Instead of 'SELECT *', we select specific columns from 3 different tables
        query = """
            SELECT 
                l.loan_id, 
                b.title,      -- Get Title from Books table
                u.name,       -- Get Name from Users table
                l.issue_date, 
                l.due_date, 
                l.return_date 
            FROM loans l
            JOIN books b ON l.book_id = b.book_id  -- Connect Loans to Books
            JOIN users u ON l.user_id = u.user_id  -- Connect Loans to Users
        """
        
        loans = self.cursor.execute(query).fetchall()

        if loans:
            # We updated headers to match the new data
            headers = ["ID", "Book Title", "Student Name", "Issued", "Due", "Returned"]
            
            print(tabulate(
                loans, 
                headers=headers, 
                tablefmt="fancy_grid",
                maxcolwidths=[None, 25, 20, None, None, None] # Optional: Prevents long titles from breaking layout
            ))
        else:
            print("No loan records found.")
            
        input("Press Enter...")

    def view_my_loans(self):
        clear_screen()
        if not self.current_user_id:
            return

        query = """
            SELECT b.title, b.author, l.issue_date, l.due_date, l.return_date 
            FROM loans l 
            JOIN books b ON l.book_id = b.book_id 
            WHERE l.user_id = ?
        """
        loans = self.cursor.execute(query, (self.current_user_id,)).fetchall()
        if loans:
            print(
                tabulate(
                    loans,
                    headers=["Title", "Author", "Borrowed", "Due", "Returned"],
                    tablefmt="fancy_grid",
                )
            )
        else:
            print("No loans found.")
        input("Press Enter...")

    # Add this to the LOAN OPERATIONS section in models.py

    def update_loan(self):
        clear_screen()
        print("\n---------- Update Loan Record ----------")

        # 1. Select the Loan
        self.list_all_loans()
        print("-" * 50)
        loan_id = get_valid_int("Enter Loan ID to update: ")

        # 2. Fetch Current Data
        loan = self.cursor.execute(
            "SELECT due_date, return_date FROM loans WHERE loan_id = ?", (loan_id,)
        ).fetchone()

        if not loan:
            print("Error: Loan ID not found.")
            input("Press Enter...")
            return

        current_due, current_return = loan
        print(f"\nUpdating Loan #{loan_id}")
        print("(Press Enter to keep current values)")

        # 3. Update Due Date (Logic: Renewals)
        new_due = input(f"New Due Date (YYYY-MM-DD) [{current_due}]: ").strip()
        if not new_due:
            new_due = current_due  # Keep old if empty

        # 4. Update Return Date (Logic: Corrections)
        # Display 'None' if it's currently empty
        display_ret = current_return if current_return else "Active/Empty"
        new_ret = input(f"New Return Date (YYYY-MM-DD) [{display_ret}]: ").strip()

        if not new_ret:
            # If user pressed enter, keep it as is (Active or Closed)
            new_ret = current_return
        elif new_ret.lower() == "clear":
            # Special command to re-open a closed loan
            new_ret = ""

        # 5. Perform Update
        try:
            # Validate Date Formats (Simple check)
            datetime.strptime(new_due, "%Y-%m-%d")
            if new_ret:
                datetime.strptime(new_ret, "%Y-%m-%d")

            self.cursor.execute(
                "UPDATE loans SET due_date = ?, return_date = ? WHERE loan_id = ?",
                (new_due, new_ret, loan_id),
            )
            self.conn.commit()
            print("Loan updated successfully.")

            # Logic Check: If we cleared the return date, ensure book is marked 'issued'
            if new_ret == "":
                # We need to find the book_id for this loan to fix the status
                book_id = self.cursor.execute(
                    "SELECT book_id FROM loans WHERE loan_id=?", (loan_id,)
                ).fetchone()[0]
                self._update_book_status(book_id, "issued")
                print("Note: Book status reset to 'Issued'.")

        except ValueError:
            print("Error: Invalid date format. Use YYYY-MM-DD.")
        except Exception as e:
            print(f"Database Error: {e}")

        input("Press Enter...")

    def delete_loan(self):
        clear_screen()
        print("\n---------- DELETE LOAN (ADMIN) ----------")
        loan_id = get_valid_int("Loan ID to delete: ")

        loan = self.cursor.execute(
            "SELECT book_id, return_date FROM loans WHERE loan_id=?", (loan_id,)
        ).fetchone()
        if not loan:
            print("Loan not found.")
            input("Press Enter...")
            return

        book_id, return_date = loan

        # Check if active
        if return_date == "" or return_date is None:
            print("WARNING: This is an ACTIVE loan.")
            conf = input(
                "Deleting this will reset the book to 'Available'. Proceed? (yes/no): "
            )
            if conf.lower() != "yes":
                return
            self._update_book_status(book_id, "available")

        self.cursor.execute("DELETE FROM loans WHERE loan_id=?", (loan_id,))
        self.conn.commit()
        print("Loan deleted.")
        input("Press Enter...")

    def generate_daily_alerts(self):
        today = date.today().strftime("%Y-%m-%d")

        query = """
        SELECT l.loan_id, b.title, u.name 
        FROM loans l 
        JOIN books b ON l.book_id = b.book_id 
        JOIN users u ON l.user_id = u.user_id 
        WHERE l.due_date = ? AND l.return_date = ''
        """

        due_loans = self.cursor.execute(query, (today,)).fetchall()

        count_new = 0
        for loan in due_loans:
            loan_id, title, user_name = loan

            exists = self.cursor.execute(
                "SELECT 1 FROM notifications WHERE loan_id = ? AND type = 'DUE_TODAY'",
                (loan_id,),
            ).fetchone()

            if not exists:
                msg = f"Book '{title}' is expected today from {user_name}."
                self.cursor.execute(
                    "INSERT INTO notifications (loan_id, type, message, status, created_at) VALUES (?, 'DUE_TODAY', ?, 'unread', ?)",
                    (loan_id, msg, today),
                )
                count_new += 1

                self.conn.commit()
                if count_new > 0:
                    print(f"🔔 System generated {count_new} new notifications.")

    def view_notifications(self):
        clear_screen()
        print("\n=== 🔔 NOTIFICATION CENTER ===")

        alerts = self.cursor.execute(
            "SELECT id, created_at, message FROM notifications WHERE status != 'resolved'"
        ).fetchall()

        if alerts:
            print(
                tabulate(
                    alerts, headers=["ID", "Date", "Message"], tablefmt="fancy_grid"
                )
            )

            choice = input("Mark all as read? (y/n): ")
            if choice.lower() == "y":
                self.cursor.execute(
                    "UPDATE notifications SET status = 'read' WHERE status = 'unread'"
                )
                self.conn.commit()
                print("Notifications marked as read.")
            else:
                print("Alerts kept in inbox.")
            input("Press Enter.....")

    def get_all_search_data(self):
        """
        Fetches EVERY Book and User to power the Autocomplete UI.
        """
        search_list = []

        # 1. Get All Books
        books = self.cursor.execute("SELECT book_id, title, author, status FROM books").fetchall()
        for b in books:
            # Format: "Book: Title (Author)"
            label = f"📖 Book: {b[1]} ({b[2]}) | ID: {b[0]}"
            search_list.append(label)

        # 2. Get All Users
        users = self.cursor.execute("SELECT user_id, name, username FROM users").fetchall()
        for u in users:
            # Format: "User: Name (@username)"
            label = f"👤 User: {u[1]} (@{u[2]}) | ID: {u[0]}"
            search_list.append(label)

        return search_list
