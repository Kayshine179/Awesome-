from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

# ----- Initialize Database -----
def init_db():
    if not os.path.exists("users.db"):
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            wallet INTEGER DEFAULT 1000
        )
        """)
        conn.commit()
        conn.close()

init_db()

# ----- Routes -----
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        message = "✅ Registration successful! You can login now."
    except:
        message = "❌ Username already exists."
    conn.close()
    return render_template("index.html", message=message)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        wallet = user[3]
        return f"""
        <h1>Dashboard</h1>
        <p>Welcome, {username}</p>
        <p>Wallet: ₦{wallet}</p>
        <button onclick="location.href='/buy/1/{user[0]}'">Buy 1GB - ₦300</button><br><br>
        <button onclick="location.href='/buy/2/{user[0]}'">Buy 2GB - ₦500</button><br><br>
        <button onclick="location.href='/'">Logout</button>
        """
    else:
        return render_template("index.html", message="❌ Invalid login")

@app.route('/buy/<int:plan>/<int:user_id>')
def buy(plan, user_id):
    price = 300 if plan == 1 else 500
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT wallet FROM users WHERE id=?", (user_id,))
    wallet = c.fetchone()[0]

    if wallet >= price:
        new_wallet = wallet - price
        c.execute("UPDATE users SET wallet=? WHERE id=?", (new_wallet, user_id))
        conn.commit()
        message = f"✅ Purchase successful! ₦{price} deducted. New wallet: ₦{new_wallet}"
    else:
        message = "❌ Insufficient wallet balance!"
    conn.close()
    return f"""
        <h1>{message}</h1>
        <button onclick="location.href='/'">Back to Home</button>
    """

# ----- Run Server (Deployment-ready) -----
if __name__ == "__main__":
    # 0.0.0.0 allows Railway or other cloud services to access the server
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))