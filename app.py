from flask import Flask, request, redirect, render_template
import psycopg2

app = Flask(__name__)

def conectar():
    return psycopg2.connect(
        host="dpg-xxxxxxxxxx.render.com",
        database="nome_do_banco",
        user="usuario",
        password="senha",
        port="5432"
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    usuario = request.form["usuario"]
    senha = request.form["senha"]

    conn = conectar()
    cur = conn.cursor()

    cur.execute("SELECT * FROM usuarios WHERE usuario=%s AND senha=%s", (usuario, senha))
    result = cur.fetchone()

    cur.close()
    conn.close()

    if result:
        return redirect("/home")
    else:
        return "Usuário ou senha inválidos"

@app.route("/home")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run()
