# views.py
import questionary
from tabulate import tabulate
from utils import clear_screen


# ========================== ADMIN MENUS ==========================

# Sub-menu for managing books
def manage_books_menu(app):
    while True:
        clear_screen()
        print("--- 📚 MANAGE BOOKS ---")
        print("1. Add Book")
        print("2. Update Book")
        print("3. Remove Book")
        print("4. List All Books")
        print("0. Back")

        choice = input("Choice: ")

        if choice == '1':
            app.add_book()
        elif choice == '2':
            app.update_book()
        elif choice == '3':
            app.remove_book()
        elif choice == '4':
            app.list_all_books()
        elif choice == '0':
            return

# Sub-menu for managing users
def manage_users_menu(app):
    while True:
        clear_screen()
        print("--- 👤 MANAGE USERS ---")
        print("1. Register (Student)")
        print("2. List Users")
        print("3. Update User")
        print("4. Delete User")
        print("0. Back")

        choice = input("Choice: ")

        if choice == "1":
            app.register_user()
        elif choice == '2':
            app.list_all_users()
        elif choice == '3':
            app.update_user()
        elif choice == '4':
            app.remove_user()
        elif choice == '0':
            return

# Sub-menu for loans
def manage_loans_menu(app):
    while True:
        clear_screen()
        print("--- 🛠️  MANAGE LOANS ---")
        print("1. Issue Book")
        print("2. Return Book")
        print("3. View All Loans")
        print("4. Delete Loan Record")
        print("5. Manual Loan Update")
        print("0. Back")

        choice = input("Choice: ")

        if choice == '1':
            app.issue_book()
        elif choice == '2':
            app.return_book()
        elif choice == '3':
            app.list_all_loans()
        elif choice == '4':
            app.delete_loan()
        elif choice == '5':
            app.update_loan()
        elif choice == '0':
            return


# ========================== SMART SEARCH SYSTEM ==========================

# Interactive Search UI
def show_smart_search(app_manager):
    clear_screen()
    print("--- 🔍 LIVE AUTOCOMPLETE SEARCH ---")
    print("Start typing to find Books or Students...")

    # Load data for autocomplete
    all_choices = app_manager.get_all_search_data()
    all_choices.append("Cancel")

    # Render menu
    selection = questionary.autocomplete(
        "Search:",
        choices=all_choices,
        ignore_case=True,
        match_middle=True 
    ).ask()

    if selection == "Cancel" or selection is None:
        return

    # Parse the selection string to get ID
    try:
        part1, part2 = selection.split(" | ID: ")
        item_id = int(part2.strip())

        # Route to correct handler
        if "Book" in part1:
            _handle_book_action(app_manager, item_id)
        elif "User" in part1:
            _handle_user_action(app_manager, item_id)

    except ValueError:
        print("Error parsing selection.")
        input("Press Enter...")


# ========================== SEARCH ACTION HANDLERS ==========================

# Actions when a book is selected
def _handle_book_action(app, book_id):
    print(f"\n📖 Selected Book ID: {book_id}")

    if app.current_user_role == 'admin':
        message = "Action:"
        choices=["Issue this Book", "View Details", "Update Book", "Delete Book", "Back"]
    else:
        message = "Action:"
        choices = ["View Details", "Back"]
    
    action = questionary.select(message, choices=choices).ask()

    if action == "Issue this Book":
        app.issue_book(prefilled_book_id=book_id)

    elif action == "View Details":
        book = app.cursor.execute(
            "SELECT * FROM books WHERE book_id=?", (book_id,)
        ).fetchone()
        
        if book:
            print("-" * 30)
            print(f"Title:  {book[1]}")
            print(f"Author: {book[2]}")
            print(f"Stock: {book[4]} available / {book[3]} total")
            print("-" * 30)
            input("Press Enter...")

    elif action == "Update Book":
        app.update_book(prefilled_book_id=book_id)

    elif action == "Delete Book":
        app.remove_book(prefilled_book_id=book_id)

# Actions when a user is selected
def _handle_user_action(app, user_id):
    print(f"\n👤 Selected User ID: {user_id}")

    user_data = app.cursor.execute(
        "SELECT username, name, phone, role FROM users WHERE user_id=?", (user_id,)
    ).fetchone()

    if not user_data:
        print("User not found.")
        input("Press Enter...")
        return

    username = user_data[0]

    action = questionary.select(
        "Action:",
        choices=["View Profile", "Update User", "View Loans", "Back"]
    ).ask()

    if action == "View Profile":
        print("-" * 30)
        print(f"Name:     {user_data[1]}")
        print(f"Username: {username}")
        print(f"Phone:    {user_data[2]}")
        print(f"Role:     {user_data[3]}")
        print("-" * 30)
        input("Press Enter...")

    elif action == "Update User":
        app.update_user(prefilled_username=username)

    elif action == "View Loans":
        # Impersonate user to view their loans
        original_id = app.current_user_id
        app.current_user_id = user_id
        
        app.view_my_loans()
        
        # Switch back to admin
        app.current_user_id = original_id