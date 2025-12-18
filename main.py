import sys
from models import LibraryManager
import views
from utils import clear_screen, get_valid_choice


def main(app):
    # Main application loop handling state (Guest/Admin/Student)
    while True:
        clear_screen()

        # --- GUEST MENU ---
        if not app.current_user_id:
            print("\n=== 📚 LIBTRACK SYSTEM ===")
            print("1. 🔑 Login")
            print("2. 🚪 Exit")
            
            choice = get_valid_choice("Choice: ", ["1", "2"])

            if choice == "1":
                app.login()
            elif choice == "2":
                break

        # --- ADMIN MENU ---
        elif app.current_user_role == "admin":

            # Trigger daily checks
            app.generate_daily_alerts()

            # Get notification badge
            unread_count = app.cursor.execute(
                "SELECT COUNT(*) FROM notifications WHERE status='unread'"
            ).fetchone()[0]
            
            badge = f"({unread_count} NEW)" if unread_count > 0 else ""

            print(f"\n=== 🛡️  ADMIN MENU ({app.current_user_name}) {badge} ===")
            print("1. 📚 Manage Books (Add/Update/Delete/List)")
            print("2. 👥 Manage Users (Add/List/Update/Delete)")
            print("3. 🛠️  Manage Loans (Issue/Return/View-All)")
            print(f"4. 🔔 Notifications {badge}")
            print("5. 🔍 Smart Search")
            print("0. 🔓 Logout")

            choice = input("\nChoice: ").strip()

            if choice == "1":
                views.manage_books_menu(app)
            elif choice == "2":
                views.manage_users_menu(app)
            elif choice == "3":
                views.manage_loans_menu(app)
            elif choice == "4":
                app.view_notifications()
            elif choice == "5":
                views.show_smart_search(app)
            elif choice == "0":
                app.logout()

        # --- STUDENT MENU ---
        elif app.current_user_role == "student":
            print(f"\n=== 🎓 STUDENT MENU ({app.current_user_name}) ===")
            print("1. 📖 View All Books")
            print("2. 🔍 Search Books")
            print("3. 🎒 My Borrowed Books")
            print("4. ✨ Newly Arrived Books")
            print("5. 🔐 Change Password")
            print("0. 🔓 Logout")

            choice = input("\nChoice: ").strip()

            if choice == "1":
                app.list_all_books()
            elif choice == "2":
                views.show_smart_search(app)
            elif choice == "3":
                app.view_my_loans()
            elif choice == "4":
                app.list_new_arrivals()
            elif choice == "5": 
                app.change_own_password(app.current_user_id)
            elif choice == "0":
                app.logout()


if __name__ == "__main__":
    app = LibraryManager()
    
    try:
        main(app)

    except KeyboardInterrupt:
        print("\n\n⚠️  Exiting safely...")

    finally:
        if 'app' in locals():
            print("🔒 Closing database connection...")
            app.conn.close()
            print("👋 Goodbye!")