from models import LibraryManager
from utils import clear_screen, get_valid_choice
import views
import sys


def main(app):
    

    while True:
        clear_screen()

        # --- LOGIN SCREEN ---
        if not app.current_user_id:
            print("\n=== 📚 LIBTRACK SYSTEM ===")
            print("1. Login")
            print("2. Register (Student)")
            print("3. Exit")
            choice = get_valid_choice("Choice: ", ["1", "2", "3"])

            if choice == "1":
                app.login()
            elif choice == "2":
                app.register_user()
            elif choice == "3":
                break

        # --- ADMIN MENU ---
        # --- ADMIN MENU ---
        elif app.current_user_role == "admin":

            # 1. GENERATE ALERTS (Runs silently)
            app.generate_daily_alerts()

            # 2. FETCH BADGE COUNT
            # FIX: Added .fetchone()[0] to get the actual integer
            unread_count = app.cursor.execute(
                "SELECT COUNT(*) FROM notifications WHERE status='unread'"
            ).fetchone()[0]
            badge = f"({unread_count} NEW)" if unread_count > 0 else ""

            # 3. DISPLAY MENU
            print(f"\n=== ADMIN MENU ({app.current_user_name}) {badge} ===")
            print("1. Manage Books (Add/Update/Delete/List)")
            print("2. Manage Users (List/Update/Delete)")
            print("3. Issue Book")
            print("4. Return Book")
            print("5. View All Loans")
            print("6. Delete Loan Record")
            print("7. Manual Loan Update")
            print(f"8. 🔔 Notifications {badge}")  # Added Option 8
            print("9. 🔍 Smart Search")
            print("0. Logout")

            # 4. GET INPUT
            choice = input("\nChoice: ")

            # 5. HANDLE CHOICES
            if choice == "1":
                views.manage_books_menu(app)

            elif choice == "2":
                views.manage_users_menu(app)

            elif choice == "3":
                app.issue_book()
            elif choice == "4":
                app.return_book()
            elif choice == "5":
                app.list_all_loans()
            elif choice == "6":
                app.delete_loan()
            elif choice == "7":
                app.update_loan()
            elif choice == "8":
                app.view_notifications()  # FIX: Added logic here
            elif choice == "9":
                views.show_smart_search(app)
            elif choice == "0":
                app.logout()

        # --- STUDENT MENU ---
        elif app.current_user_role == "student":
            print(f"\n=== STUDENT MENU ({app.current_user_name}) ===")
            print("1. View All Books")
            print("2. Search Books")
            print("3. My Borrowed Books")
            print("0. Logout")

            choice = input("\nChoice: ")

            if choice == "1":
                app.list_all_books()
            elif choice == "2":
                app.search_books()
            elif choice == "3":
                app.view_my_loans()
            elif choice == "0":
                app.logout()



#  Update the Execution Block
if __name__ == "__main__":
    # Initialize the Manager HERE (Global Scope)
    app = LibraryManager()
    
    try:
        # Pass the app instance into main
        main(app)

    except KeyboardInterrupt:
        # This catches Ctrl+C
        print("\n\n⚠️  Keyboard Interrupt Detected. Exiting safely...")

    finally:
        # Now 'app' is visible here, so we can close the connection
        if 'app' in locals():
            print("🔒 Closing database connection...")
            app.conn.close()
            print("👋 Goodbye!")