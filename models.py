import sqlite3
from datetime import date, timedelta, datetime
import time
from tabulate import tabulate
from utils import (
    clear_screen,
    get_valid_string,
    get_valid_int,
    get_valid_choice,
    validate_phone_format,
    calculate_fine,
    get_validated_input,
    validate_username_format
)

class LibraryManager:
    # Initialize connection
    def __init__(self, db_name="test.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")

        # Session State
        self.current_user_id = None
        self.current_user_role = None
        self.current_user_name = None

        self.initialize_db()

    # Create tables if missing
    def initialize_db(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                total_copies INTEGER DEFAULT 1,    
                available_copies INTEGER DEFAULT 1 
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
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                loan_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT DEFAULT 'unread',
                created_at TEXT NOT NULL,
                FOREIGN KEY (loan_id) REFERENCES loans (loan_id)
            );
        """
        )
        self.conn.commit()

    # ========================== USER MANAGEMENT ==========================

    # Handle Login
    def login(self):
        clear_screen()
        print("\n---------- 🔐 Login ----------")
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
            print(f"✅ Logged in as {user[2]}")
            time.sleep(3)
            return True
        else:
            print("❌ Invalid credentials.")
            input("Press Enter...")
            return False

    # Handle Logout
    def logout(self):
        self.current_user_id = None
        self.current_user_role = None
        self.current_user_name = None

    # Register new student
    def register_user(self):
        clear_screen()
        print("\n---------- 👤 Register User ----------")
        name = get_valid_string("Name: ")
        username = get_validated_input("Enter Username: ", validate_username_format)
        phone = get_validated_input("Phone (10 digits): ", validate_phone_format)
        password = get_valid_string("Password: ")

        try:
            self.cursor.execute(
                "INSERT INTO users (name, username, phone, password, role) VALUES (?, ?, ?, ?, 'student')",
                (name, username, phone, password),
            )
            self.conn.commit()
            print(f"✨ User {name} registered successfully.")
        except sqlite3.IntegrityError:
            print("❌ Error: Username already exists.")
        input("Press Enter...")

    # List users table
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

    # Update user details
    def update_user(self, prefilled_username=None):
        clear_screen()
        print("\n---------- ✏️  Update User ----------")

        if prefilled_username:
            target_username = prefilled_username
            print(f"Updating User: {target_username}")
        else:
            target_username = get_valid_string("Enter username to update: ").lower()

        user = self.cursor.execute(
            "SELECT * FROM users WHERE username=?", (target_username,)
        ).fetchone()

        if not user:
            print(f"❌ User '{target_username}' not found.")
            input("Press Enter...")
            return

        u_id, u_name, u_username, u_phone, u_pass, u_role = user

        print(f"\nUpdating: {u_name} ({u_role})")
        print("(Press Enter to keep current value)")

        new_name = input(f"New Name [{u_name}]: ").strip() or u_name
        new_username = input(f"New Username [{u_username}]: ").strip().lower() or u_username
        print(f"Current Phone: {u_phone}")
        while True:
            p_input = input(f"New Phone (Leave empty to keep current): ").strip()
            if not p_input:
                new_phone = u_phone
                break
            
            validation_msg = validate_phone_format(p_input)
            if validation_msg is True:
                new_phone = p_input
                break
            else:
                print(f"Error: {validation_msg}")
        
        new_pass = input(f"New Password [{u_pass}]: ").strip() or u_pass

        print(f"Current Role: {u_role}")
        new_role = input(f"New Role (student/admin) [{u_role}]: ").strip().lower()

        if not new_role:
            new_role = u_role

        if new_role not in ['student', 'admin']:
            print("Invalid role. Keeping old role.")
            new_role = u_role

        # Prevent removing last admin
        if u_role == 'admin' and new_role == 'student':
            admin_count = self.cursor.execute(
                "SELECT COUNT(*) FROM users WHERE role='admin'"
            ).fetchone()[0]

            if admin_count <= 1:
                print("\n❌ CRITICAL: You cannot downgrade the last Administrator.")
                input("Press Enter to cancel...")
                return

        try:
            self.cursor.execute(
                "UPDATE users SET name=?, username=?, phone=?, password=?, role=? WHERE user_id=?",
                (new_name, new_username, new_phone, new_pass, new_role, u_id),
            )
            self.conn.commit()
            print("✅ User updated successfully.")

            if u_id == self.current_user_id and new_role == 'student':
                print("⚠️ You have downgraded your own account. Logging out...")
                self.logout()

        except sqlite3.IntegrityError:
            print("❌ Error: Username taken.")

        input("Press Enter...")

    # Delete user account
    def remove_user(self):
        clear_screen()
        print("\n---------- 🗑️  Delete User ----------")
        username = get_valid_string("Enter username to delete: ").lower()

        user = self.cursor.execute(
            "SELECT user_id, role FROM users WHERE username=?", (username,)
        ).fetchone()

        if not user:
            print("❌ User not found.")
            input("Press Enter...")
            return

        target_user_id, target_user_role = user

        if target_user_id == self.current_user_id:
            print("❌ Error: You cannot delete your own account while logged in.")
            input("Press Enter...")
            return

        if target_user_role == 'admin':
            admin_count = self.cursor.execute(
                "SELECT COUNT(*) FROM users WHERE role='admin'"
            ).fetchone()[0]

            if admin_count <= 1:
                print("❌ Error: Cannot delete the last Administrator.")
                input("Press Enter...")
                return

        active_loans = self.cursor.execute(
            "SELECT COUNT(*) FROM loans WHERE user_id=? AND (return_date='' OR return_date IS NULL)",
            (target_user_id,)
        ).fetchone()[0]

        if active_loans > 0:
            print(f"❌ Error: This user has {active_loans} active loan(s).")
            print("They must return all books before deletion.")
            input("Press Enter...")
            return

        confirm = input(f"⚠️ Are you sure you want to delete {username}? (yes/no): ")
        if confirm.lower() == "yes":
            self.cursor.execute("DELETE FROM loans WHERE user_id=?", (target_user_id,))
            self.cursor.execute("DELETE FROM users WHERE user_id=?", (target_user_id,))
            self.conn.commit()
            print("✅ User deleted successfully.")
        else:
            print("Operation cancelled.")

        input("Press Enter...")

    # Student change password
    def change_own_password(self, current_user_id):
        print("\n--- 🔐 Change Password ---")
        
        old_password = input("Enter your CURRENT password: ").strip()
        
        self.cursor.execute("SELECT password FROM users WHERE user_id = ?", (current_user_id,))
        stored_password = self.cursor.fetchone()
        
        if stored_password is None:
            print("Error: User record not found.")
            input("Press Enter...")
            return

        if old_password == stored_password[0]:
            new_password = input("Enter NEW password: ").strip()
            confirm_password = input("Confirm NEW password: ").strip()
            
            if new_password == confirm_password:
                if new_password:
                    try:
                        self.cursor.execute("UPDATE users SET password = ? WHERE user_id = ?", (new_password, current_user_id))
                        self.conn.commit()
                        print("✅ Password updated successfully!")
                        input("Press Enter...")
                    except sqlite3.Error as e:
                        print(f"Database error: {e}")
                        input("Press Enter...")
                else:
                    print("❌ Password cannot be empty.")
                    input("Press Enter...")
            else:
                print("❌ New passwords do not match.")
                input("Press Enter...")
        else:
            print("❌ Incorrect current password.")
            input("Press Enter...")

    # ========================== BOOK OPERATIONS ==========================

    # Add book to inventory
    def add_book(self):
        clear_screen()
        print("\n---------- 📖 Add Book ----------")
        title = get_valid_string("Title: ")
        author = get_valid_string("Author: ")
        
        qty = get_valid_int("Total Quantity: ")

        try:
            self.cursor.execute(
                "INSERT INTO books (title, author, total_copies, available_copies) VALUES (?, ?, ?, ?)",
                (title, author, qty, qty),
            )
            self.conn.commit()
            print(f"✨ Success! Added {qty} copies of '{title}'.")
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
        
        input("Press Enter...")

    # List all books
    def list_all_books(self):
        clear_screen()
        books = self.cursor.execute("SELECT * FROM books").fetchall()
        
        if books:
            print(
                tabulate(
                    books,
                    headers=["ID", "Title", "Author", "Total", "Available"],
                    tablefmt="fancy_grid",
                )
            )
        else:
            print("No books found.")
        input("Press Enter...")

    # Search logic
    def search_books(self):
        clear_screen()
        print("\n---------- 🔍 Search Books ----------")
        kw = get_valid_string("Enter keyword: ").lower()
        books = self.cursor.execute(
            "SELECT * FROM books WHERE lower(title) LIKE ? OR lower(author) LIKE ?",
            (f"%{kw}%", f"%{kw}%"),
        ).fetchall()
        if books:
            print(
                tabulate(
                    books,
                    headers=["ID", "Title", "Author", "Total", "Available"],
                    tablefmt="fancy_grid",
                )
            )
        else:
            print("No matches found.")
        input("Press Enter...")

    # Update book details
    def update_book(self, prefilled_book_id=None):
        clear_screen()
        print("\n---------- ✏️  Update Book ----------")
        
        if prefilled_book_id:
            book_id = prefilled_book_id
            print(f"Editing Book ID: {book_id}")
        else:
            book_id = get_valid_int("Book ID: ")

        book = self.cursor.execute(
            "SELECT * FROM books WHERE book_id=?", (book_id,)
        ).fetchone()

        if not book:
            print("❌ Book not found.")
            input("Press Enter...")
            return

        curr_title, curr_author, curr_total, curr_avail = book[1], book[2], book[3], book[4]

        print(f"Current Title: {curr_title}")
        new_title = input(f"New Title (Press Enter to keep): ").strip()
        if not new_title:
            new_title = curr_title

        print(f"Current Author: {curr_author}")
        new_author = input(f"New Author (Press Enter to keep): ").strip()
        if not new_author:
            new_author = curr_author
        
        print(f"Current Stock: {curr_total} (Available: {curr_avail})")
        new_total_str = input(f"New Total Quantity [{curr_total}]: ").strip()
        
        if new_total_str:
            try:
                new_total = int(new_total_str)
                issued_count = curr_total - curr_avail
                if new_total < issued_count:
                    print(f"❌ Error: Cannot reduce total below currently issued count ({issued_count}).")
                    input("Press Enter...")
                    return
                
                diff = new_total - curr_total
                new_avail = curr_avail + diff
            except ValueError:
                print("Invalid number. Keeping old quantity.")
                new_total = curr_total
                new_avail = curr_avail
        else:
            new_total = curr_total
            new_avail = curr_avail

        try:
            self.cursor.execute(
                "UPDATE books SET title=?, author=?, total_copies=?, available_copies=? WHERE book_id=?",
                (new_title, new_author, new_total, new_avail, book_id),
            )
            self.conn.commit()
            print("✅ Book details updated successfully.")
        except Exception as e:
            print(f"❌ Database Error: {e}")
            
        input("Press Enter...")

    # Remove book
    def remove_book(self, prefilled_book_id=None):
        clear_screen()
        print("\n---------- 🗑️  Delete Book ----------")
        
        if prefilled_book_id:
            book_id = prefilled_book_id
            print(f"Deleting Book ID: {book_id}")
        else:
            book_id = get_valid_int("Book ID to delete: ")

        book = self.cursor.execute(
            "SELECT title, total_copies, available_copies FROM books WHERE book_id = ?", (book_id,)
        ).fetchone()
        
        if not book:
            print("❌ Book not found")
            input("Press Enter...")
            return

        title, total, avail = book

        if total != avail:
            issued = total - avail
            print(f"❌ Error: Cannot delete '{title}'.")
            print(f"There are still {issued} copy(s) issued to students.")
            input("Press Enter...")
            return

        history_count = self.cursor.execute(
            "SELECT COUNT(*) FROM loans WHERE book_id = ?", (book_id,)
        ).fetchone()[0]

        if history_count > 0:
            print(f"⚠️  This book has {history_count} past loan records.")
            print("Deleting it will erase this history forever.")
            confirm = input("Are you sure? (yes/no): ").strip().lower()

            if confirm != "yes":
                print("Deletion cancelled.")
                input("Press Enter...")
                return
            
            self.cursor.execute("DELETE FROM loans WHERE book_id = ?", (book_id,))

        try:
            self.cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
            self.conn.commit()
            print(f"✅ Book '{title}' deleted successfully.")
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error: {e}")

        input("Press Enter...")

    # ========================== LOAN OPERATIONS ==========================

    # Issue book to student
    def issue_book(self, prefilled_book_id=None):
        clear_screen()
        print("\n---------- 📚 Issue Book ----------")
        
        if prefilled_book_id:
            book_id = prefilled_book_id
            print(f"Selected Book ID: {book_id}")
        else:
            book_id = get_valid_int("Book ID: ")
        
        user_id = get_valid_int("User ID: ")

        book = self.cursor.execute(
            "SELECT title, available_copies FROM books WHERE book_id=?", (book_id,)
        ).fetchone()
        
        if not book:
            print("❌ Error: Book not found.")
            input("Press Enter...")
            return
            
        if book[1] <= 0:
            print(f"❌ Error: '{book[0]}' is out of stock.")
            input("Press Enter...")
            return

        user = self.cursor.execute(
            "SELECT name FROM users WHERE user_id=?", (user_id,)
        ).fetchone()
        
        if not user:
            print("❌ Error: User not found.")
            input("Press Enter...")
            return  

        try:
            today = date.today()
            due = today + timedelta(days=14)

            self.cursor.execute(
                "UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?", 
                (book_id,)
            )
            
            self.cursor.execute(
                "INSERT INTO loans (book_id, user_id, issue_date, due_date, return_date) VALUES (?, ?, ?, ?, '')",
                (book_id, user_id, today.strftime("%Y-%m-%d"), due.strftime("%Y-%m-%d")),
            )
            
            self.conn.commit()
            print(f"✅ Success! Book issued to {user[0]}. Remaining Stock: {book[1] - 1}")
            
        except Exception as e:
            self.conn.rollback()
            print(f"Database Error: {e}")
            
        input("Press Enter...")

    # Return book from student
    def return_book(self):
        clear_screen()
        print("\n---------- 📥 Return Book ----------")
        book_id = get_valid_int("Book ID to return: ")

        loan = self.cursor.execute(
            "SELECT loan_id, due_date, user_id FROM loans WHERE book_id=? AND (return_date='' OR return_date IS NULL)",
            (book_id,),
        ).fetchone()

        if not loan:
            print("❌ No active loan found for this book ID.")
            input("Press Enter...")
            return

        loan_id, due_date, user_id = loan
        fine, days = calculate_fine(due_date)

        try:
            self.cursor.execute(
                "UPDATE loans SET return_date=? WHERE loan_id=?",
                (date.today().strftime("%Y-%m-%d"), loan_id),
            )
            self.cursor.execute(
                "UPDATE books SET available_copies = available_copies + 1 WHERE book_id=?", 
                (book_id,)
            )
            self.cursor.execute(
                "UPDATE notifications SET status = 'resolved' WHERE loan_id = ?",
                (loan_id,)
            )
            
            self.conn.commit()
            print("✅ Book returned successfully.")
                
            if fine > 0:
                print(f"⚠️  OVERDUE by {days} days. Fine: ${fine:.2f}")
            else:
                print("Returned on time. No fine.")

        except Exception as e:
            self.conn.rollback()
            print(f"Error during return: {e}")
            
        input("Press Enter...")

    # Show new arrivals
    def list_new_arrivals(self):
        clear_screen()
        print("\n--- ✨ NEW ARRIVALS ---")
        books = self.cursor.execute("SELECT * FROM books ORDER BY book_id DESC LIMIT 5").fetchall()
        print(tabulate(books, headers=["ID", "Title", "Author", "Total", "Available"], tablefmt="fancy_grid"))
        input("Press Enter...")

    # List all loans (Admin)
    def list_all_loans(self):
        clear_screen()
        print("\n----------- All Loan Records ----------")

        query = """
            SELECT 
                l.loan_id, 
                b.title, 
                u.name, 
                l.issue_date, 
                l.due_date, 
                l.return_date 
            FROM loans l
            JOIN books b ON l.book_id = b.book_id
            JOIN users u ON l.user_id = u.user_id
        """

        loans = self.cursor.execute(query).fetchall()

        if loans:
            headers = ["ID", "Book Title", "Student Name", "Issued", "Due", "Returned"]
            print(tabulate(
                loans,
                headers=headers,
                tablefmt="fancy_grid",
                maxcolwidths=[None, 25, 20, None, None, None]
            ))
        else:
            print("No loan records found.")

        input("Press Enter...")

    # View personal loans
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

    # Manually update loan
    def update_loan(self):
        clear_screen()
        print("\n---------- ✏️  Update Loan Record ----------")

        self.list_all_loans()
        print("-" * 50)
        loan_id = get_valid_int("Enter Loan ID to update: ")

        loan = self.cursor.execute(
            "SELECT due_date, return_date, book_id FROM loans WHERE loan_id = ?", (loan_id,)
        ).fetchone()

        if not loan:
            print("❌ Error: Loan ID not found.")
            input("Press Enter...")
            return

        current_due, current_return, book_id = loan
        print(f"\nUpdating Loan #{loan_id}")
        print("(Press Enter to keep current values)")

        new_due_input = input(f"New Due Date (YYYY-MM-DD) [{current_due}]: ").strip()
        
        if not new_due_input:
            final_due_date = current_due
        else:
            try:
                dt_obj = datetime.strptime(new_due_input, "%Y-%m-%d")
                final_due_date = dt_obj.strftime("%Y-%m-%d")
            except ValueError:
                print("❌ Error: Invalid date format. Use YYYY-MM-DD.")
                input("Press Enter...")
                return

        display_ret = current_return if current_return else "Active/Empty"
        new_ret_input = input(f"New Return Date (YYYY-MM-DD) [{display_ret}]: ").strip()

        final_return_date = current_return 

        if new_ret_input.lower() == "clear":
            final_return_date = ""
        elif new_ret_input:
            try:
                dt_ret = datetime.strptime(new_ret_input, "%Y-%m-%d")
                final_return_date = dt_ret.strftime("%Y-%m-%d")
            except ValueError:
                print("❌ Error: Invalid return date format.")
                input("Press Enter...")
                return

        is_unreturning = (final_return_date == "" and current_return)
        
        # Check stock before removing return date
        if is_unreturning:
            current_avail = self.cursor.execute(
                "SELECT available_copies FROM books WHERE book_id=?", (book_id,)
            ).fetchone()[0]
            
            if current_avail <= 0:
                print(f"❌ Error: Cannot mark as borrowed. Book stock is 0.")
                input("Press Enter to cancel...")
                return

        try:
            self.cursor.execute(
                "UPDATE loans SET due_date = ?, return_date = ? WHERE loan_id = ?",
                (final_due_date, final_return_date, loan_id),
            )
            
            if is_unreturning:
                self.cursor.execute(
                    "UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?", 
                    (book_id,)
                )
                print("Note: Book count adjusted (Stock -1).")

            self.conn.commit()
            print(f"✅ Loan updated. New Due Date: {final_due_date}")

            self.cursor.execute(
                "UPDATE notifications SET status = 'resolved' WHERE loan_id = ?",
                (loan_id,)
            )
            self.conn.commit()
            self.generate_daily_alerts()

        except Exception as e:
            self.conn.rollback()
            print(f"Database Error: {e}")

        input("Press Enter...")

    # Delete loan (Admin only)
    def delete_loan(self):
        clear_screen()
        print("\n---------- 🗑️  DELETE LOAN (ADMIN) ----------")
        loan_id = get_valid_int("Loan ID to delete: ")

        loan = self.cursor.execute(
            "SELECT book_id, return_date FROM loans WHERE loan_id=?", (loan_id,)
        ).fetchone()
        if not loan:
            print("Loan not found.")
            input("Press Enter...")
            return

        book_id, return_date = loan

        if return_date == "" or return_date is None:
            print("⚠️  WARNING: This is an ACTIVE loan.")
            conf = input(
                "Deleting this will reset the book to 'Available'. Proceed? (yes/no): "
            )
            if conf.lower() != "yes":
                return
            
            self.cursor.execute(
                "UPDATE books SET available_copies = available_copies + 1 WHERE book_id = ?", 
                (book_id,)
            )

        self.cursor.execute("DELETE FROM loans WHERE loan_id=?", (loan_id,))
        self.conn.commit()
        print("✅ Loan deleted.")
        input("Press Enter...")
        
    # ========================== NOTIFICATIONS & UTILS ==========================

    # Create daily alerts
    def generate_daily_alerts(self):
        today = date.today().strftime("%Y-%m-%d")
        
        query = """
        SELECT l.loan_id, b.title, u.name 
        FROM loans l 
        JOIN books b ON l.book_id = b.book_id 
        JOIN users u ON l.user_id = u.user_id 
        WHERE l.due_date = ? AND (l.return_date = '' OR l.return_date IS NULL)
        """

        due_loans = self.cursor.execute(query, (today,)).fetchall()

        count_new = 0
        for loan in due_loans:
            loan_id, title, user_name = loan

            exists = self.cursor.execute(
                "SELECT 1 FROM notifications WHERE loan_id = ? AND type = 'DUE_TODAY' AND status != 'resolved'",
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

    # View alerts inbox
    def view_notifications(self):
        clear_screen()
        print("\n=== 🔔 NOTIFICATION CENTER ===")

        alerts = self.cursor.execute(
            "SELECT id, created_at, message, status FROM notifications WHERE status != 'resolved'"
        ).fetchall()

        if not alerts:
            print("No active notifications.")
            input("Press Enter...")
            return

        table_data = []
        for row in alerts:
            n_id, created, msg, status = row
            icon = "🔴" if status == 'unread' else "⚪"
            table_data.append([n_id, created, icon, msg])

        print(tabulate(
            table_data, 
            headers=["ID", "Date", "Stat", "Message"], 
            tablefmt="fancy_grid"
        ))

        print("\nOptions:")
        print(" [ID]   -> Mark read")
        print(" 'all'  -> Mark ALL read")
        print(" 'd ID' -> Dismiss/Resolve (e.g., 'd 5')")
        print(" [Enter]-> Back")

        choice = input("\nAction: ").strip().lower()

        if choice == 'all':
            self.cursor.execute("UPDATE notifications SET status = 'read' WHERE status = 'unread'")
            self.conn.commit()
            print("All notifications marked as read.")
        
        elif choice.isdigit():
            self.cursor.execute("UPDATE notifications SET status = 'read' WHERE id = ?", (choice,))
            self.conn.commit()
            print(f"Notification #{choice} marked as read.")

        elif choice.startswith('d '):
            try:
                _, target_id = choice.split(maxsplit=1)
                if target_id.isdigit():
                    self.cursor.execute("UPDATE notifications SET status = 'resolved' WHERE id = ?", (target_id,))
                    self.conn.commit()
                    print(f"Notification #{target_id} dismissed.")
                else:
                    print("Error: Invalid ID.")
            except ValueError:
                print("Error: Use 'd <ID>'.")
        
        if choice: 
            input("Press Enter...")

    # Data for autocomplete search
    def get_all_search_data(self):
        search_list = []
        books = self.cursor.execute("SELECT book_id, title, author FROM books").fetchall()
        for b in books:
            label = f"📖 Book: {b[1]} ({b[2]}) | ID: {b[0]}"
            search_list.append(label)
            
        if self.current_user_role == 'admin':
            users = self.cursor.execute("SELECT user_id, name, username FROM users").fetchall()
            for u in users:
                label = f"👤 User: {u[1]} (@{u[2]}) | ID: {u[0]}"
                search_list.append(label)

        return search_list