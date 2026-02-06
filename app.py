from flask import Flask, render_template, request, redirect, session
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

FILE_NAME = "accounts.json"
interest_default = 5

# Load or create accounts
if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        accounts = json.load(f)
else:
    accounts = {}
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=4)

def save_accounts():
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=4)

def format_date(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%B %d, %Y")

def days_since_creation(bank_id):
    created_str = accounts[bank_id][5]
    interest_rate = accounts[bank_id][6]
    deposit = accounts[bank_id][4]

    created_date = datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S")
    days_passed = (datetime.now() - created_date).days

    if days_passed > 0:
        interest = deposit * (interest_rate / 100) * days_passed
        deposit += interest
        accounts[bank_id][4] = deposit
        save_accounts()
    return deposit

# -------------------- ROUTES --------------------

@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        pin = request.form["pin"]
        age = int(request.form["age"])

        # Check existing username
        if any(data[2].lower() == username.lower() for data in accounts.values()):
            return "Username exists! <a href='/register'>Try again</a>"

        if len(pin) != 6 or not pin.isdigit():
            return "PIN must be 6 digits! <a href='/register'>Try again</a>"

        if age <= 12:
            return "Too young to register! <a href='/register'>Try again</a>"

        next_id = str(max([int(k) for k in accounts.keys()]+[0]) + 1).zfill(4)
        created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        accounts[next_id] = [500.0, int(pin), username, age, 0.0, created_date, interest_default]
        save_accounts()
        return f"Account Created! Bank ID: {next_id} <a href='/login'>Login</a>"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_input = request.form["user"]
        pin_input = int(request.form["pin"])
        for b_id, data in accounts.items():
            if (user_input == data[2] or user_input == b_id) and pin_input == data[1]:
                session["bank_id"] = b_id
                return redirect("/profile")
        return "Invalid login! <a href='/login'>Try again</a>"

    return render_template("login.html")

@app.route("/profile")
def profile():
    if "bank_id" not in session:
        return redirect("/login")

    bank_id = session["bank_id"]
    data = accounts[bank_id]
    deposit = days_since_creation(bank_id)

    return render_template(
        "profile.html",
        username=data[2],
        balance=data[0],
        age=data[3],
        deposit=deposit,
        interest=data[6],
        date_created=format_date(data[5])
    )

@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    if "bank_id" not in session:
        return redirect("/login")
    bank_id = session["bank_id"]
    if request.method == "POST":
        amount = float(request.form["amount"])
        if amount <= 0 or amount > accounts[bank_id][0]:
            return "Invalid deposit amount! <a href='/deposit'>Try again</a>"
        accounts[bank_id][0] -= amount
        accounts[bank_id][4] += amount
        save_accounts()
        return redirect("/profile")
    return render_template("deposit.html")

@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    if "bank_id" not in session:
        return redirect("/login")
    bank_id = session["bank_id"]
    if request.method == "POST":
        amount = float(request.form["amount"])
        if amount <= 0 or amount > accounts[bank_id][4]:
            return "Invalid withdraw amount! <a href='/withdraw'>Try again</a>"
        accounts[bank_id][4] -= amount
        accounts[bank_id][0] += amount
        save_accounts()
        return redirect("/profile")
    return render_template("withdraw.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# -------------------- RUN --------------------
if __name__ == "__main__":
    app.run(debug=True)
