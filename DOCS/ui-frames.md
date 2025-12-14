[Back >>>](./algorith-checklist.md)

Screen 0: The Login Gateway (The Entry Point)
This is the new "First Screen" of your application. It satisfies the "User Authentication" requirement.

```
=============================================
        📚 WELCOME TO LIBTRACK
=============================================
 Please select your role:
 
 1. 👮 Librarian (Admin Access)
 2. 🎓 Student (Member Access)
 
 0. Exit
=============================================
Enter choice: _
```
---

### **Path A: Librarian Login**
Action: If user selects 1.

Security: Ask for a password (you can hardcode this as admin123 for simplicity, or store it).

Destination: Goes to the Admin Dashboard (The screen I showed you previously: Manage Books, Issue, Return).

### **Path B: Student Login (The User View)**
Action: If user selects 2.

Security: Ask for their Member ID.

Logic: Check the members table. If the ID exists, let them in. If not, show "Access Denied."

---

## **Path A: Librarian Login**

```
=============================================
        📚 LIBTRACK: LIBRARY MANAGER
=============================================
 1. Manage Books (Add/Delete/List)
 2. Manage Members
 3. Issue Book (Loan)
 4. Return Book
 5. View Overdue Items
 ---------------------------------------------
 0. Exit System
=============================================
Enter your choice: _
```

---

Screen 2: Book Management Sub-Menu
If the user selects 1, they go here. Note the "Table Format" for listing books—this fulfills the "Read" part of CRUD.

```
--- 📖 BOOK MANAGEMENT ---

 1. Add New Book
 2. Delete Book
 3. View All Books
 4. Back to Main Menu

Enter choice: 3

[ID]   [Title]                  [Author]         [Status]
------------------------------------------------------------
101    Learn Python 3           Zed Shaw         Available
102    Clean Code               Robert Martin    ISSUED
103    The Pragmatic Programmer Andy Hunt        Available
------------------------------------------------------------
```
Tip for Coding: You will use Python f-strings to align these columns nicely (e.g., print(f"{id:<5} {title:<25}")).

---

Screen 3: The "Issue Book" Workflow (Transaction)
This is the most complex interaction. It involves validation steps.

```
--- 📤 ISSUE BOOK ---

Step 1: Identify Book
Enter Book ID: 102
> Error: Book 'Clean Code' is already ISSUED to Member #55.
> Try again? (y/n): y

Enter Book ID: 101
> Book Selected: 'Learn Python 3' (Available)

Step 2: Identify Member
Enter Member ID: 501
> Member Verified: Amal Raj

Step 3: Confirm
Issue 'Learn Python 3' to Amal Raj? (y/n): y

[SUCCESS] Transaction Recorded. Due Date: Dec 10, 2025.
Press Enter to continue...
```

---

Screen 4: The "Return Book" Workflow
This includes your "Innovation" feature (Fine Calculation).

```
--- 📥 RETURN BOOK ---

Enter Book ID: 102
> Returning: 'Clean Code'
> Borrowed by: John Doe on Nov 20, 2025
> Days Elapsed: 13 days

[!] ALERT: Book is OVERDUE by 6 days.
[!] FINE CALCULATED: $6.00

Confirm Return & Payment? (y/n): y
[SUCCESS] Book marked as Available.
```

---

Screen 5: Add New Member (Input Form)
A simple data entry screen.

```
--- 👤 REGISTER MEMBER ---

Enter Name: Sarah Smith
Enter Phone: 9876543210

Saving...
[SUCCESS] Member 'Sarah Smith' added with ID: 502

```

---

## **Screen B-1: The Student Dashboard**

```
=============================================
        🎓 STUDENT DASHBOARD: Amal Raj
=============================================
 1. 🔍 Search Books
 2. 📖 My Borrowed Books (Check Due Dates)
 3. 💲 Check My Fines
 ---------------------------------------------
 0. Logout
=============================================
Enter choice: _
```

---

Screen B-2: "My Borrowed Books" (Personalized Data)
This is the most useful screen for a user. It queries the loans table specifically for their ID.

```
--- 📖 MY ACTIVE LOANS ---

[Book Title]            [Borrowed On]   [Due Date]     [Status]
------------------------------------------------------------------
Clean Code              Nov 20          Nov 27         OVERDUE!
Intro to Algorithms     Dec 01          Dec 08         On Time
------------------------------------------------------------------
```
- Innovation Point: Highlighting "OVERDUE!" in red or capital letters here adds to the user experience.

---

Screen B-3: Search Books (Read-Only)
Students need to see what is available before asking a librarian.

```
--- 🔍 SEARCH LIBRARY ---

Enter Title or Author: Python

[Found 2 Results]
1. 'Learn Python 3' by Zed Shaw ...... [Available]
2. 'Python Crash Course' ............. [ISSUED - Back Dec 5]

```
