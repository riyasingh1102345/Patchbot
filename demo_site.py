import sqlite3
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

# Initialize an in-memory demo database
conn = sqlite3.connect(":memory:", check_same_thread=False)
conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, role TEXT)")
conn.execute("INSERT INTO users (username, role) VALUES ('admin', 'superuser'), ('khushi', 'developer')")
conn.commit()


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Acme Pay — Internal Portal</title>
        <style>
            body { font-family: system-ui, sans-serif; max-width: 560px; margin: 60px auto; padding: 24px; background: #f8fafc; color: #0f172a; }
            .card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 24px; margin-bottom: 20px; }
            input { width: 100%; padding: 9px; margin: 8px 0 14px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; }
            button { background: #0f172a; color: #fff; border: none; padding: 10px 16px; border-radius: 6px; cursor: pointer; font-weight: 600; }
        </style>
    </head>
    <body>
        <h2>Acme Pay — Internal Developer Portal</h2>
        <div class="card">
            <h3>1. User Directory Lookup</h3>
            <form action="/user" method="post">
                <label>Username</label>
                <input type="text" name="username" placeholder="e.g. admin" />
                <button type="submit">Search User</button>
            </form>
        </div>
        <div class="card">
            <h3>2. Quick Fee Calculator</h3>
            <form action="/calculate" method="post">
                <label>Formula</label>
                <input type="text" name="formula" placeholder="e.g. 1500 * 0.18" />
                <button type="submit">Calculate</button>
            </form>
        </div>
    </body>
    </html>
    """


@app.post("/user")
def lookup_user(username: str = Form(...)):
    # VULNERABILITY 1 (CWE-89): Unparameterized SQL query vulnerable to SQL Injection
    query = f"SELECT id, username, role FROM users WHERE username = '{username}'"
    rows = conn.execute(query).fetchall()
    return {"query_executed": query, "results": rows}


@app.post("/calculate")
def calculate_fee(formula: str = Form(...)):
    # VULNERABILITY 2 (CWE-95): Arbitrary code execution via eval()
    result = eval(formula)
    return {"formula": formula, "result": result}