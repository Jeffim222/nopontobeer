from flask import Flask, render_template, request
from db import get_connection

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/salvar", methods=["POST"])
def salvar():
    nome = request.form.get("nome")
    email = request.form.get("email")

    # Conexão com o banco
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO clientes (nome, email)
        VALUES (%s, %s)
    """, (nome, email))

    conn.commit()
    cur.close()
    conn.close()

    return "Dados salvos com sucesso no PostgreSQL!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
