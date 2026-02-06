import json
import os
from datetime import datetime

FILE_NAME = "accounts.json"

attempts = 3

if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        accounts = json.load(f)
else:
    accounts = {
        "0000": [5100.0, 123456, "Frisk", 8, 0.0, "2026-02-05 00:00:00", 5],
        "1111": [5300.0, 246810, "Chara", 11, 0.0, "2026-02-05 00:00:00", 7],
        "2222": [5500.0, 122555, "Kris", 15, 0.0, "2026-02-05 00:00:00", 10],
        "3333": [6767.0, 123456, "Formie", 13, 0.0, "2026-02-05 00:00:00", 12]
    }
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=4)

choice = 0
balance = 0.0
logged_in = False
globalUser = ""
globalAge = 0
bank_ID = None
depositt = 0.0
interest = 5

print("\nWelcome to the ATM!")

def save():
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=4)

def get_bank_id_by_name(name):
    for bank_id, data in accounts.items():
        if data[2].lower() == name.lower():
            return bank_id
    return None

def days_since_creation():
    global balance, depositt, interest

    created_str = accounts[bank_ID][5]
    interest_rate = accounts[bank_ID][6]

    depositt = accounts[bank_ID][4]

    created_date = datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S")
    days_passed = (datetime.now() - created_date).days

    if days_passed > 0:
        interest = depositt * (interest_rate / 100) * days_passed
        depositt += interest

        accounts[bank_ID][4] = depositt
        save()

def caseSwitch():
    if choice == 1:
        registration_page()
    elif choice == 2:
        login_page()
    elif choice == 3:
        print("Goodbye!")
        exit()
    else:
        print("\nIndex out of range!\n")
        welcome_page()


def welcome_page():
    global choice
    print("\nOptions")
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    while True:
        try:
            choice = int(input("Enter index: "))
            caseSwitch()
            break
        except ValueError:
            print("\nPlease input an integer only!\n")

def login_page():
    global logged_in, globalUser, globalAge, balance, bank_ID, depositt, attempts
    print("\nLogin Page")
    userInput = input("Enter your username or bank ID: ")
    valid = False
    while True:
        try:
            passInput = int(input("Enter your PIN: "))
            break
        except ValueError:
            print("Please enter numbers only!")

    for b_id, data in accounts.items():
        if (userInput == data[2] or userInput == b_id) and passInput == data[1]:
            logged_in = True
            globalUser = data[2]
            globalAge = data[3]
            balance = float(data[0])
            depositt = float(data[4])
            bank_ID = b_id
            attempts = 3
            valid = True

    if valid:
        days_since_creation()
        profile()
    else:
        attempts -= 1
        print(f"\nIncorrect input! {attempts} attempts left.")
        if attempts == 0:
            print("Too many failed attempts. Exiting.")
            exit()
        login_page()

def format_date(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return f"{dt.strftime('%B')} {dt.day}, {dt.year}"

def profile():
    if bank_ID is None:
        welcome_page()
        return
    print(f"\nWelcome {globalUser}!\n")
    print(f"Wallet: ₱{balance:.2f}")
    print(f"Age: {globalAge}")
    print(f"Deposits: ₱{depositt:.2f}")
    print(f"Interest Rate: {accounts[bank_ID][6]}%")
    print("Date Created:", format_date(accounts[bank_ID][5]))
    print("Options")
    print("1. Pay Bills")
    print("2. Change details")
    print("3. Delete account")
    print("4. Deposit")
    print("5. Withdraw")
    print("6. Log-Out")
    print("7. Help")
    while True:
        try:
            userInput = int(input("Enter index: "))
            break
        except ValueError:
            print("\nPlease input an integer only!\n")

    if userInput == 1:
        pay_bills()
    elif userInput == 2:
        change_details()
    elif userInput == 3:
        delete_account()
    elif userInput == 4:
        deposit()
    elif userInput == 5:
        withdraw()
    elif userInput == 6:
        save()
        logged_in = False
        welcome_page()
    elif userInput == 7:
        help_sec()
    else:
        profile()

def help_sec():
    print("\nHelp Section\n")
    print("1. Deposit money to gain interest.")
    print("2. You can loan money but to make it not a hassle when its due, set autopay on and it automically pays every loan when due every time you log in! (Note that having insufficient balance will instead make autopay use your deposit which in turn deducts your interest.")
    profile()

def deposit():
    global balance, depositt
    while True:
        try:
            amount = float(input("Enter amount to deposit: "))
            if amount > balance:
                print("You can't deposit more than your wallet!")
            elif amount <= 0:
                print("Enter a positive amount!")
            else:
                break
        except ValueError:
            print("Enter a valid number!")

    balance -= amount
    depositt += amount
    accounts[bank_ID][0] = balance
    accounts[bank_ID][4] = depositt
    save()
    profile()

def withdraw():
    global balance, depositt
    while True:
        try:
            amount = float(input("Enter amount to withdraw: "))
            if amount > depositt:
                print("You can't withdraw more than your deposits!")
            elif amount <= 0:
                print("Enter a positive amount!")
            else:
                break
        except ValueError:
            print("Enter a valid number!")

    depositt -= amount
    balance += amount
    accounts[bank_ID][4] = depositt
    accounts[bank_ID][0] = balance
    save()
    profile()

def pay_bills():
    global balance
    print(f"Balance: ₱{balance:.2f}")
    print("Pay your bills for these options!")
    print("1. ZANECO (₱3500)")
    print("2. Water (₱500)")
    print("3. Groceries (₱2500)")
    print("4. PLDT (₱2000)")
    print("5. Withdraw")
    print("6. Deposit")
    while True:
        try:
            choice_bill = int(input("Enter index: "))
            break
        except ValueError:
            print("Please input an integer!")

    cost = 0
    if choice_bill == 1:
        cost = 3500.0
    elif choice_bill == 2:
        cost = 500.0
    elif choice_bill == 3:
        cost = 2500.0
    elif choice_bill == 4:
        cost = 2000.0
    elif choice_bill == 5:
        withdraw()
        return
    elif choice_bill == 6:
        deposit()
        return
    else:
        profile()
        return

    if balance >= cost:
        balance -= cost
        accounts[bank_ID][0] = balance
        save()
        print(f"Successfully paid! Your total balance is now ₱{balance:.2f}.")
    else:
        print("Insufficient balance!")
    profile()

def registration_page():
    global attempts
    attempts = 3

    username = input("Enter your username: ")
    if any(data[2].lower() == username.lower() for data in accounts.values()):
        print("Username already exists!")
        registration_page()
        return

    pinInput = input("Enter your PIN (6 digits): ")
    if not pinInput.isdigit() or len(pinInput) != 6:
        print("Invalid PIN!")
        registration_page()
        return

    while True:
        try:
            ageInput = int(input("Enter your age: "))
            break
        except ValueError:
            print("Enter an integer for age!")

    if ageInput <= 12:
        print("Your too young!")
        welcome_page()
        return

    next_id = str(max(int(k) for k in accounts.keys()) + 1).zfill(4)
    created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    interest_rate = interest

    accounts[next_id] = [
        500.0,
        int(pinInput),
        username,
        ageInput,
        0.0,
        created_date,
        interest_rate
    ]

    print(f"\nAccount Created!")
    print(f"Bank ID: {next_id}")
    print(f"Date Created: {format_date(created_date)}")
    print(f"Interest Rate: {interest_rate}%")

    save()
    welcome_page()

def change_details():
    global globalUser
    oldPin = input("Enter current PIN to proceed: ")
    if not oldPin.isdigit() or int(oldPin) != accounts[bank_ID][1]:
        print("Incorrect PIN!")
        profile()
        return

    newUser = input("Enter new username (skip to leave unchanged): ")
    if newUser != "":
        accounts[bank_ID][2] = newUser
        globalUser = newUser

    newAge = input("Enter new age (skip to leave unchanged): ")
    if newAge.isdigit():
        accounts[bank_ID][3] = int(newAge)

    newPin = input("Enter new PIN (6 digits, skip to leave unchanged): ")
    if newPin.isdigit() and len(newPin) == 6:
        accounts[bank_ID][1] = int(newPin)

    save()
    profile()

def delete_account():
    global logged_in, globalUser, globalAge, balance
    pinInput = input("Enter your PIN to confirm: ")
    if str(accounts[bank_ID][1]) == pinInput:
        del accounts[bank_ID]
        save()
        logged_in = False
        globalUser = ""
        globalAge = 0
        balance = 0.0
        print("Account deleted successfully.")
        welcome_page()
    else:
        print("Incorrect PIN!")
        profile()

def randomize_bank_id():
    last_id = max(accounts.keys())
    return str(int(last_id) + 1).zfill(4)

welcome_page()