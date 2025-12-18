import os
from datetime import date, datetime


# ========================== SYSTEM UTILITIES ==========================

def clear_screen():
    # Clears terminal for Windows/Mac/Linux
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


# ========================== INPUT HANDLING ==========================

def get_valid_string(prompt):
    # Enforces non-empty string input
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("❌ Error: Input cannot be empty.")


def get_valid_int(prompt):
    # Enforces integer input
    while True:
        value = input(prompt).strip()
        try:
            return int(value)
        except ValueError:
            print("❌ Error: Please enter a valid number.")


def get_valid_choice(prompt, options):
    # Restricts input to specific options
    while True:
        value = input(prompt).strip().lower()
        if value in options:
            return value
        print(f"❌ Error: Invalid choice. Choose from {options}")


def get_validated_input(prompt, validator_func):
    # Generic validator using a custom function
    while True:
        value = input(prompt).strip()
        
        result = validator_func(value)
        
        if result is True:
            return value
        else:
            print(f"❌ Error: {result}")

def validate_phone_format(text):
    # Checks for exactly 10 digits
    if not text.isdigit():
        return "Invalid format! Numbers only."
    
    if len(text) != 10:
        return "Invalid length! Must be exactly 10 digits."
        
    return True

# ========================== BUSINESS LOGIC & RULES ==========================

def validate_username_format(text):
    # Checks length and characters
    if len(text) < 3:
        return "Too short! Must be at least 3 chars."
    
    if not text.isalnum():
        return "Invalid format! Letters and numbers only (no spaces)."
    
    return True


def calculate_fine(due_date_str):
    # Calculates 1.00 fine per day overdue
    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        today = date.today()
        
        days_overdue = (today - due_date).days

        if days_overdue > 0:
            return days_overdue * 1.0, days_overdue
        
        return 0.0, 0
    except ValueError:
        return 0.0, 0