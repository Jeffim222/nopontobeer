from flask import Flask, request, jsonify, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "CHAVE_SUPER_SECRETA_MUDE_AQUI"
CORS(app, supports_credentials=True)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# Criar tabela se não existir
with get_db() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    db.commit()

# -------------------------- ROTAS --------------------------

@app.post("/register")
def register():
    data = request.get_json()
    email = data["email"]
    password = generate_password_hash(data["password"])

    try:
        db = get_db()
        db.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        db.commit()
        return jsonify({"message": "Usuário registrado com sucesso!"})
    except:
        return jsonify({"error": "Email já cadastrado"}), 400


@app.post("/login")
def login():
    data = request.get_json()
    email = data["email"]
    password = data["password"]

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if user and check_password_hash(user["password"], password):
        session["user"] = email
        return jsonify({"message": "Login bem-sucedido!"})
    
    return jsonify({"error": "Credenciais inválidas"}), 401


@app.get("/check")
def check_session():
    if "user" in session:
        return jsonify({"logged": True, "email": session["user"]})
    return jsonify({"logged": False})


@app.get("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logout efetuado!"})

# -----------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
