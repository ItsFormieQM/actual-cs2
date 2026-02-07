from flask import Flask, render_template, request, redirect, session
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

FILE_NAME = "accounts.json"
interest_default = 5


# -------------------- JSON HELPERS --------------------

def load_accounts():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)
        return {}

    with open(FILE_NAME, "r", encoding="utf-8") as f:
        return json.load(f)


def save_accounts(accounts):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=4)


def format_date(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%B %d, %Y")


def days_since_creation(accounts, bank_id):
    created_str = accounts[bank_id][5]
    interest_rate = accounts[bank_id][6]
    deposit = accounts[bank_id][4]

    created_date = datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S")
    days_passed = (datetime.now() - created_date).days

    if days_passed > 0:
        interest = deposit * (interest_rate / 100) * days_passed
        accounts[bank_id][4] += interest
        save_accounts(accounts)

    return accounts[bank_id][4]


# -------------------- ROUTES --------------------

@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    accounts = load_accounts()

    if request.method == "POST":
        username = request.form["username"]
        pin = request.form["pin"]
        age = int(request.form["age"])

        if any(data[2].lower() == username.lower() for data in accounts.values()):
            return "Username exists!"

        if not pin.isdigit() or len(pin) != 6:
            return "PIN must be 6 digits!"

        if age <= 12:
            return "Too young!"

        next_id = str(max([int(k) for k in accounts.keys()] + [0]) + 1).zfill(4)
        created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        accounts[next_id] = [
            500.0,
            int(pin),
            username,
            age,
            0.0,
            created_date,
            interest_default
        ]

        save_accounts(accounts)
        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    accounts = load_accounts()

    if request.method == "POST":
        user_input = request.form["user"]
        pin_input = request.form["pin"]

        for b_id, data in accounts.items():
            if (user_input == data[2] or user_input == b_id) and pin_input == str(data[1]):
                session["bank_id"] = b_id
                return redirect("/profile")

        return "Invalid login"

    return render_template("login.html")


@app.route("/profile")
def profile():
    if "bank_id" not in session:
        return redirect("/login")

    accounts = load_accounts()
    bank_id = session["bank_id"]

    deposit = days_since_creation(accounts, bank_id)

    return render_template(
        "profile.html",
        username=accounts[bank_id][2],
        balance=accounts[bank_id][0],
        age=accounts[bank_id][3],
        deposit=deposit,
        interest=accounts[bank_id][6],
        date_created=format_date(accounts[bank_id][5])
    )


@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    if "bank_id" not in session:
        return redirect("/login")

    accounts = load_accounts()
    bank_id = session["bank_id"]

    if request.method == "POST":
        amount = float(request.form["amount"])

        if amount <= 0 or amount > accounts[bank_id][0]:
            return "Invalid amount"

        accounts[bank_id][0] -= amount
        accounts[bank_id][4] += amount
        save_accounts(accounts)

        return redirect("/profile")

    return render_template("deposit.html")


@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    if "bank_id" not in session:
        return redirect("/login")

    accounts = load_accounts()
    bank_id = session["bank_id"]

    if request.method == "POST":
        amount = float(request.form["amount"])

        if amount <= 0 or amount > accounts[bank_id][4]:
            return "Invalid amount"

        accounts[bank_id][4] -= amount
        accounts[bank_id][0] += amount
        save_accounts(accounts)

        return redirect("/profile")

    return render_template("withdraw.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/musicPage")
def music_changer():
    """
    Serve the music changer page with OST folders and their music files.
    Dynamically reads all subfolders in static/music.
    """
    import os

    MUSIC_BASE = os.path.join(app.root_path, "static", "music")

    # Ensure base folder exists
    if not os.path.exists(MUSIC_BASE):
        os.makedirs(MUSIC_BASE)

    ost_folders = []
    music_library = {}

    # Iterate over all folders inside static/music
    for entry in os.listdir(MUSIC_BASE):
        folder_path = os.path.join(MUSIC_BASE, entry)
        if os.path.isdir(folder_path):
            ost_folders.append(entry)
            files = []

            # Get all audio files in this folder
            for f in os.listdir(folder_path):
                file_path = os.path.join(folder_path, f)
                if os.path.isfile(file_path) and f.lower().endswith((".ogg", ".mp3", ".wav")):
                    files.append(f)

            # Ensure it's always a list (even empty)
            music_library[entry] = files

    # Convert everything to strings to avoid JSON issues
    ost_folders = [str(f) for f in ost_folders]
    music_library = {str(k): [str(f) for f in v] for k, v in music_library.items()}

    ost_folders = sorted(ost_folders,key=lambda x: (x != "Undertale OST", x))
    return render_template(
        "musicPage.html",
        ost_folders=ost_folders,
        music_library=music_library
    )

if __name__ == "__main__":
    app.run(debug=True)
