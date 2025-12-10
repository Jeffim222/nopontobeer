from flask import Flask, send_from_directory, request
from db import get_connection
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/inserir", methods=["POST"])
def inserir():
    nome = request.form.get("nome")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO teste (nome) VALUES (%s)", (nome,))
    conn.commit()

    cur.close()
    conn.close()

    return "Inserido com sucesso!"


# Isso permite acessar CSS, JS, imagens na raiz
@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)


if __name__ == "__main__":
    app.run()
