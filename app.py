from flask import Flask, request, send_from_directory
import psycopg2
import bcrypt

app = Flask(__name__)

# ---------------------------------
# CONEXÃO COM O POSTGRESQL
# ---------------------------------
def get_conn():
    return psycopg2.connect(
        host="dpg-d4ffejk9c44c73boc8hg-a.oregon-postgres.render.com",
        database="beer_jp8s",
        user="admin",
        password="FvNx1g2vewP6487FkJ1z0eItBLJe5joR",
        port="5432"
    )

# ---------------------------------
# TELA DE LOGIN
# ---------------------------------
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# ---------------------------------
# PROCESSAMENTO DO LOGIN
# ---------------------------------
@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT password_hash FROM users WHERE email = %s", (email,))
    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return "Usuário não existe."

    stored_hash = row[0].encode("utf-8")

    if bcrypt.checkpw(password.encode(), stored_hash):
        return "Login OK!"
    else:
        return "Senha incorreta."

# ---------------------------------
# CRIAR USUÁRIO TESTE
# ---------------------------------
@app.route("/criarusuario")
def criarusuario():
    email = "admin@teste.com"
    password = "123456"

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s)", (email, hashed))
    conn.commit()

    cur.close()
    conn.close()

    return "Usuário criado!<br>Email: admin@teste.com<br>Senha: 123456"

if __name__ == "__main__":
    app.run(debug=True)
