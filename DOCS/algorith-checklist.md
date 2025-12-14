# 📘 Library Management System: Detailed Execution Algorithm

## 🛠 Phase 1: The Foundation (Database & Setup)
**Focus:** Creating the persistent storage and connecting Python to SQLite.

- [ ] **Step 1.1: Project Skeleton**
    - **File:** (Folder Creation)
    - **Task:** Create `Library_Project/` folder and empty files: `main.py`, `database.py`, `models.py`.
    - **Syllabus:** [File Handling], [Modules].
- [ ] **Step 1.2: Database Connection**
    - **File:** `database.py`
    - **Task:** Create a class or function `initialize_db()` that connects to `library.db`.
    - **Syllabus:** [SQLite Integration], [Functions].
- [ ] **Step 1.3: Creating the Tables (Schema)**
    - **File:** `database.py`
    - **Task:** Execute SQL `CREATE TABLE IF NOT EXISTS` for:
        1. `books` (id, title, author, status)
        2. `members` (id, name, phone)
        3. `loans` (id, book_id, member_id, issue_date, return_date)
    - **Syllabus:** [SQLite Integration], [Data Structures].

---

## 🏗 Phase 2: The Backend Logic (OOP Models)
**Focus:** Writing the Python classes that handle data (CRUD).

- [ ] **Step 2.1: The Book Model**
    - **File:** `models.py`
    - **Task:** Create `class Book`.
        - Method `add_book(title, author)`: Runs SQL `INSERT`.
        - Method `get_all_books()`: Runs SQL `SELECT *`.
    - **Syllabus:** [OOPS], [Lists/Tuples].
- [ ] **Step 2.2: The Member Model**
    - **File:** `models.py`
    - **Task:** Create `class Member`.
        - Method `add_member(name, phone)`: Runs SQL `INSERT`.
    - **Syllabus:** [OOPS], [Exception Handling].

---

## 🔄 Phase 3: Transaction Logic (The "Hard" Part)
**Focus:** Handling the relationship between Books and Members (Issuing/Returning).

- [ ] **Step 3.1: Issue Book Algorithm**
    - **File:** `models.py`
    - **Task:** Create function `issue_book(book_id, member_id)`.
        1. **Check:** Is book status 'Available'? (If no, return False).
        2. **Action:** SQL `INSERT` into `loans` (use `datetime.now()` for date).
        3. **Update:** SQL `UPDATE books SET status = 'Issued'`.
    - **Syllabus:** [Control Structures], [Modules: datetime].
- [ ] **Step 3.2: Return Book Algorithm**
    - **File:** `models.py`
    - **Task:** Create function `return_book(book_id)`.
        1. **Update:** SQL `UPDATE loans SET return_date = ?` where book_id matches.
        2. **Update:** SQL `UPDATE books SET status = 'Available'`.
    - **Syllabus:** [SQLite Integration], [Variables].

---

## 🖥 Phase 4: The Interface (CLI)
**Focus:** Tying it all together for the user (The Visuals).

- [ ] **Step 4.1: The Librarian Dashboard**
    - **File:** `main.py`
    - **Task:** Create a menu loop for Admins:
        - `1. Add Book` -> Calls `Book.add_book()`
        - `2. View Books` -> Loops through list and prints formatted rows.
        - `3. Issue Book` -> Asks for IDs -> Calls `issue_book()`.
    - **Syllabus:** [While Loops], [Input/Output].
- [ ] **Step 4.2: Data Formatting**
    - **File:** `main.py`
    - **Task:** Use F-Strings to make columns align perfectly.
    - **Example:** `print(f"{id:<5} | {title:<20} | {status}")`
    - **Syllabus:** [String Manipulation].

---

## 🔐 Phase 5: Authentication & User Views
**Focus:** Meeting the "Two User Types" requirement.

- [ ] **Step 5.1: The Login Gateway**
    - **File:** `main.py`
    - **Task:** Create the first screen asking: "1. Librarian / 2. Student".
    - **Logic:**
        - If 1: Ask for Password -> Go to Admin Menu.
        - If 2: Ask for Member ID -> Go to Student Menu.
    - **Syllabus:** [Control Structures (Nested If)].
- [ ] **Step 5.2: The Student Dashboard (Read-Only)**
    - **File:** `main.py`
    - **Task:** Create a simplified menu for Students:
        - `1. My Books` -> Queries `loans` table for their ID only.
        - `2. Search` -> Filters books by name.

---

## 🚀 Phase 6: Innovation & Final Polish
**Focus:** Extra marks for logic and presentation.

- [ ] **Step 6.1: Overdue Fine Calculator**
    - **File:** `models.py`
    - **Task:** In `return_book()`:
        - Calculate `delta = current_date - issue_date`.
        - If `delta.days > 7`, print `Fine Amount: ${delta.days * 1}`.
    - **Syllabus:** [Modules: datetime], [Arithmetic Operators].
- [ ] **Step 6.2: Documentation**
    - **File:** `README.md`
    - **Task:** Write instructions: "Run `python main.py`. Admin Pass: admin123".
- [ ] **Step 6.3: Code Cleanup**
    - **Task:** Add comments like `# This connects to DB` above your functions.