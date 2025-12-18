import sqlite3
from models import LibraryManager


def create_admin_account():
    # Helper script to manually create an Admin user
    db = LibraryManager()
    print("\n--- 🛡️  ADMIN BOOTSTRAP ---")
    print("Creating the first Super User...")

    name = input("Name: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    # Default placeholder phone
    default_phone = "0000000000"

    try:
        # Force 'admin' role directly into DB
        db.cursor.execute(
            "INSERT INTO users (name, username, password, phone, role) VALUES (?, ?, ?, ?, 'admin')",
            (name, username, password, default_phone),
        )
        db.conn.commit()
        print(f"\n✅ Success! Admin '{username}' created.")
        print("You may now run 'main.py' and log in.")

    except sqlite3.IntegrityError:
        print(f"\n❌ Error: The username '{username}' is already taken.")
        print("Please choose a different username.")
    
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")


if __name__ == "__main__":
    create_admin_account()