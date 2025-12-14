import os
from datetime import date, datetime


def clear_screen():
    """Clears the terminal screen."""
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def get_valid_string(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Error: Input cannot be empty.")


def get_valid_int(prompt):
    while True:
        value = input(prompt).strip()
        try:
            return int(value)
        except ValueError:
            print("Error: Please enter a valid number.")


def get_valid_choice(prompt, options):
    while True:
        value = input(prompt).strip().lower()
        if value in options:
            return value
        print(f"Error: Invalid choice. Choose from {options}")


def calculate_fine(due_date_str):
    """Calculates $1 fine per day overdue."""
    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        today = date.today()
        days_overdue = (today - due_date).days

        if days_overdue > 0:
            return days_overdue * 1.0, days_overdue
        return 0.0, 0
    except ValueError:
        return 0.0, 0

# The Rules Engine
def validate_username_format(text):
    if len(text) < 3:
        return "Too short! Must be at least 3 chars."
    if not text.isalnum():
        return "Invalid format! Letters and numbers only (no spaces)."
    return True # True means it passed

# The Updated Input Helper
def get_validated_input(prompt, validator_func):
    while True:
        value = input(prompt).strip()
        
        # Run the validation function
        result = validator_func(value)
        
        if result == True:
            return value
        else:
            print(f"Error: {result}") # Print the specific error message