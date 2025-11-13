from flask import Flask, render_template, request, redirect, session
import json, os, hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = "gizli_anahtar"
USER_FILE = "users.json"
MESSAGE_FILE = "messages.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def load_messages():
    if os.path.exists(MESSAGE_FILE):
        with open(MESSAGE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_messages(messages):
    with open(MESSAGE_FILE, "w") as f:
        json.dump(messages, f)

@app.route("/", methods=["GET", "POST"])
def login():
    users = load_users()
    message = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_hash = hash_password(password)

        if username == "Cleaner Personeli" and password == "571de":
            session["username"] = username
            session["admin"] = True
            return redirect("/dashboard")

        if username in users:
            if users[username]["password"] == password_hash:
                session["username"] = username
                session["admin"] = False
                return redirect("/dashboard")
            else:
                message = "Şifre yanlış!"
        else:
            users[username] = {
                "password": password_hash,
                "cl": 50
            }
            save_users(users)
            session["username"] = username
            session["admin"] = False
            return redirect("/dashboard")

    return render_template("login.html", message=message)

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "username" not in session:
        return redirect("/")
    users = load_users()
    messages = load_messages()
    username = session["username"]

    if session.get("admin"):
        selected_user = request.form.get("selected_user")
        if selected_user:
            return redirect(f"/user/{selected_user}")
        return render_template("admin_dashboard.html", users=users)
    else:
        user_messages = messages.get(username, [])
        return render_template("user_dashboard.html", cl=users[username]["cl"], messages=user_messages)

@app.route("/user/<username>", methods=["GET", "POST"])
def user_panel(username):
    if not session.get("admin"):
        return redirect("/")
    users = load_users()
    messages = load_messages()
    message = ""

    if request.method == "POST":
        if "amount" in request.form:
            try:
                amount = int(request.form["amount"])
                users[username]["cl"] += amount
                save_users(users)
                message = f"CL güncellendi: {amount:+}"
            except:
                message = "CL güncelleme hatası!"
        elif "new_message" in request.form:
            text = request.form["new_message"]
            messages.setdefault(username, []).append({
                "text": text,
                "date": str(datetime.now()),
                "deleted": False
            })
            save_messages(messages)
            message = "Mesaj gönderildi."
        elif "delete_index" in request.form:
            index = int(request.form["delete_index"])
            if 0 <= index < len(messages.get(username, [])):
                messages[username][index]["deleted"] = True
                save_messages(messages)
                message = "Mesaj silindi."

    user_messages = messages.get(username, [])
    return render_template("user_panel.html", username=username, cl=users[username]["cl"], messages=user_messages, message=message)

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")

# ✅ Railway için gerekli çalıştırma satırı
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
