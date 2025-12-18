import sqlite3
from models import LibraryManager

def seed_database():
    """
    Populates the 'books' table with initial data for testing purposes.
    This script inserts books directly into the database without requiring manual input,
    ensuring they are compatible with the existing Questionary UI.
    """
    # Initialize the manager to get the DB connection
    db = LibraryManager()
    print("--- 📚 SEEDING LIBRARY DATABASE ---")

    # List of books to add: (Title, Author, Quantity)
    # The script sets total_copies and available_copies to the same value initially.
    books_data = [
        ("The Great Gatsby", "F. Scott Fitzgerald", 5),
        ("To Kill a Mockingbird", "Harper Lee", 3),
        ("1984", "George Orwell", 10),
        ("Pride and Prejudice", "Jane Austen", 4),
        ("The Catcher in the Rye", "J.D. Salinger", 6),
        ("The Hobbit", "J.R.R. Tolkien", 8),
        ("Fahrenheit 451", "Ray Bradbury", 5),
        ("Moby Dick", "Herman Melville", 2),
        ("War and Peace", "Leo Tolstoy", 3),
        ("The Odyssey", "Homer", 4),
        ("Hamlet", "William Shakespeare", 7),
        ("The Divine Comedy", "Dante Alighieri", 2),
        ("Crime and Punishment", "Fyodor Dostoevsky", 4),
        ("The Brothers Karamazov", "Fyodor Dostoevsky", 3),
        ("Brave New World", "Aldous Huxley", 6)
    ]

    count = 0
    for title, author, qty in books_data:
        try:
            # We insert directly using SQL to bypass the input() prompts in add_book()
            db.cursor.execute(
                "INSERT INTO books (title, author, total_copies, available_copies) VALUES (?, ?, ?, ?)",
                (title, author, qty, qty)
            )
            count += 1
            print(f"Added: {title} (Qty: {qty})")
            
        except sqlite3.Error as e:
            print(f"Error adding '{title}': {e}")

    db.conn.commit()
    print("-" * 30)
    print(f"✅ Successfully added {count} books to the library.")
    print("You can now run 'main.py' and select 'List All Books' or 'Smart Search' to see them.")
    db.conn.close()

if __name__ == "__main__":
    seed_database()