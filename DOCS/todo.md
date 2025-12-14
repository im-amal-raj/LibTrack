# PROJECT LIBTRACK

### UI

1. - [] OPTIMIZE FRAMES 

FRAMES [>>>](/ui-frames.md)

## Phase 1: The Foundation (Target: Finish by Dec 5)
### Goal: Have the database ready and proven to work for "Review 1".

### Module 1: Project Setup & Database Creation

[ ] Task 1.1: Create the folder structure (main.py, database.py, models.py).

[ ] Task 1.2: Write database.py with the initialize_db() function.

[ ] Task 1.3: Write the SQL CREATE TABLE queries for books, members, and loans.

[ ] Task 1.4: Run the script and confirm library.db is created.

[ ] Milestone: You can open your database and show the mentor: "Here is my schema with 3 normalized tables."

## Phase 2: Core Admin Features (Target: Finish by Dec 8)
### Goal: Demonstrate basic CRUD (Add/Read/Delete) for "Review 2".

## Module 2: The Data Logic (Backend)

[ ] Task 2.1: In models.py, create the Book class.

[ ] Task 2.2: Write the add_book() function (SQL INSERT).

[ ] Task 2.3: Write the get_all_books() function (SQL SELECT).

[ ] Task 2.4: In models.py, create the Member class and add_member() function.

Module 3: The Admin CLI (Frontend)

[ ] Task 3.1: In main.py, build the "Librarian Menu" (Screen 2 from our design).

[ ] Task 3.2: Connect the menu inputs to your models.py functions.

[ ] Milestone: You can demonstrate adding a book and seeing it appear in the list. This satisfies the "Functionality (30%)" requirement for basic CRUD.

## 📅 Phase 3: Transactions & User Logic
### Target Date: Dec 10 (Before Review 3) Goal: Handle the "Relationships" (Loans) and Student View.

[ ] Task 3.1: Issue Book Logic

Check if Book Status is 'Available'.

If yes, INSERT row into loans table.

UPDATE books status to 'Issued'.

[ ] Task 3.2: Return Book Logic

UPDATE loans table with return_date.

UPDATE books status back to 'Available'.

[ ] Task 3.3: Login Gateway

In main.py, add the "Login Screen" (1. Librarian / 2. Student).

[ ] Task 3.4: Student View

Implement get_my_loans(member_id) in models.py.

Create the Read-Only "Student Dashboard" in main.py.

## 📅 Phase 4: Innovation & Polish
### Target Date: Dec 12 (Before Review 4) Goal: Add "Extra Features" for higher marks.

[ ] Task 4.1: Overdue Fine Calculator

Calculate days between issue_date and today.

If days > 7, print "Fine: $X".

 [ x ] Task 4.2: Input Validation

Add try/except blocks to prevent crashing on invalid ID inputs.

[ ] Task 4.3: Search Feature

Add ability to filter books by Name/Author.

[ ] Task 4.4: Documentation

Add comments to all functions.

Complete the README.md.