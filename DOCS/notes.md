## JOIN 

### JOIN keyword in sql

```
  

def view_loans_with_names():

    # 1. Select the specific columns you want (loans.date AND books.title)

    # 2. FROM the main table (loans)

    # 3. JOIN the secondary table (books)

    # 4. ON the matching keys (loans.book_id = books.book_id)

    query = """

        SELECT

            loans.loan_id,

            books.title,       -- Getting Title from Books table

            books.author,      -- Getting Author from Books table

            loans.issue_date,

            loans.return_date

        FROM loans

        JOIN books ON loans.book_id = books.book_id

    """

    cursor.execute(query)

    results = cursor.fetchall()

    # Now loop and print

    # Row index: 0=LoanID, 1=Title, 2=Author, 3=IssueDate...

    for row in results:

        print(f"Loan #{row[0]}: '{row[1]}' by {row[2]} (Issued: {row[3]})")
```

### For using dynamic user_id
```
query = """
        SELECT 
            books.title, 
            books.author, 
            loans.issue_date, 
            loans.return_date
        FROM loans
        JOIN books ON loans.book_id = books.book_id
        WHERE loans.user_id = ?  -- This filters for the specific user
    """
    
    # 2. Execute with the user_id tuple
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()
```
---

## FILTER partial match

```
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
```