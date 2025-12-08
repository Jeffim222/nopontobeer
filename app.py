from flask import Flask, render_template, request, redirect, session, send_from_directory
import os

app = Flask(__name__)
app.secret_key = "qualquercoisa123"  # troque depois

# ---- Rotas ----

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return send_from_directory(".", "dashboard.html")
    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    # login simples para testes
    if username == "admin" and password == "123":
        session["user"] = username
        return redirect("/dashboard")

    return "Usuário ou senha inválidos!"

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# permitir carregar arquivos estáticos
@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory("static", path)

if __name__ == "__main__":
    app.run(debug=True)
