from models import LibraryManager

db = LibraryManager()
print("Creating Admin Account...")
name = input("Name: ")
username = input("Username: ")
password = input("Password: ")
db.cursor.execute(
    "INSERT INTO users (name, username, password, phone, role) VALUES (?, ?, ?, '1234567891', 'admin')",
    (name, username, password),
)
db.conn.commit()
print("Admin created! Run main.py now.")
