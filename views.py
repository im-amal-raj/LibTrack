# views.py
import questionary
from tabulate import tabulate
from utils import clear_screen

def manage_books_menu(app):
    while True:  # <--- The Loop
        clear_screen()
        print("--- MANAGE BOOKS ---")
        print("1. Add Book")
        print("2. Update Book")
        print("3. Remove BOOK")
        print("4. List All Book")
        print("0. Back")  # <--- The Escape Hatch
        
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
            return  # <--- Breaks loop, goes back to Admin Menu

def manage_users_menu(app):
    while True:  # <--- The Loop
        clear_screen()
        print("--- MANAGE USERS ---")
        print("1. List User")
        print("2. Update User")
        print("3. Delete User")
        print("0. Back")  # <--- The Escape Hatch
        
        choice = input("Choice: ")
        
        if choice == '1':
            app.list_all_users()
        elif choice == '2':
            app.update_user()
        elif choice == '3':
            app.remove_user()
        elif choice == '0':
            return  # <--- Breaks loop, goes back to Admin Menu

# Replace the existing show_smart_search in views.py

def show_smart_search(app_manager):
    clear_screen()
    print("--- 🔍 LIVE AUTOCOMPLETE SEARCH ---")
    print("Start typing to find Books or Students...")

    # 1. Get ALL data first (The "Cache")
    # This might take a split second, but it makes typing instant
    all_choices = app_manager.get_all_search_data()
    all_choices.append("Cancel")

    # 2. Show the Autocomplete Input
    # This replaces the simple 'input()'
    selection = questionary.autocomplete(
        "Search:",
        choices=all_choices,
        ignore_case=True,
        match_middle=True # Matches "Harry" even if you type "Potter"
    ).ask()

    if selection == "Cancel" or selection is None:
        return

    # 3. Parse the selection
    # We need to figure out if it's a Book or User based on the emoji/text
    # Format was: "📖 Book: Title... | ID: 101"
    
    try:
        # Split by the pipe '|' symbol to find ID
        part1, part2 = selection.split(" | ID: ")
        item_id = int(part2.strip())
        
        if "Book" in part1:
            _handle_book_action(app_manager, item_id)
        elif "User" in part1:
            _handle_user_action(app_manager, item_id)
            
    except ValueError:
        print("Error parsing selection.")
        input("Press Enter...")

# --- Helper Functions for Actions ---

def _handle_book_action(app, book_id):
    """Context menu for Books - Now strictly strictly directs to functions!"""
    print(f"\n📖 Selected Book ID: {book_id}")
    
    action = questionary.select(
        "Action:",
        choices=["Issue this Book", "View Details", "Update Book", "Delete Book", "Back"]
    ).ask()
    
    if action == "Issue this Book":
        # Direct call with the ID we found!
        app.issue_book(prefilled_book_id=book_id)
        
    elif action == "View Details":
        book = app.cursor.execute("SELECT * FROM books WHERE book_id=?", (book_id,)).fetchone()
        if book:
            # Simple detail view
            print("-" * 30)
            print(f"Title:  {book[1]}")
            print(f"Author: {book[2]}")
            print(f"Status: {book[3]}")
            print("-" * 30)
            input("Press Enter...")
    
    elif action == "Update Book":
        # Direct call
        app.update_book(prefilled_book_id=book_id)
    
    elif action == "Delete Book":
        # Direct call
        app.remove_book(prefilled_book_id=book_id)

def _handle_user_action(app, user_id):
    """Context menu for Users"""
    print(f"\n👤 Selected User ID: {user_id}")
    
    # We need the username for some admin functions
    user_data = app.cursor.execute("SELECT username, name, phone, role FROM users WHERE user_id=?", (user_id,)).fetchone()
    
    if not user_data:
        print("User not found.")
        input("Press Enter...")
        return

    username = user_data[0] # Extract username

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
        # Direct call using the username we fetched
        app.update_user(prefilled_username=username)
        
    elif action == "View Loans":
        # The 'Hack' to view another user's loans
        original_id = app.current_user_id
        app.current_user_id = user_id # Impersonate
        app.view_my_loans() 
        app.current_user_id = original_id # Switch back