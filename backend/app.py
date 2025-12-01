from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Dados vindos das variáveis de ambiente do Render
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    senha = data.get("senha")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM usuarios WHERE email=%s AND senha=%s",
                (email, senha))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if user:
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "erro", "msg": "Credenciais inválidas"}), 401

@app.route("/")
def home():
    return "API está rodando!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
