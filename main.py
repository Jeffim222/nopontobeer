from flask import Flask, send_from_directory, request, jsonify
from db import get_connection
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Criar tabela se não existir
def criar_tabela():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100),
                email VARCHAR(200)
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Tabela 'clientes' verificada/criada")
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")

# Executar ao iniciar
criar_tabela()

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/inserir", methods=["POST"])
def inserir():
    nome = request.form.get("nome")
    email = request.form.get("email", "")  # email opcional
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        if email:
            cur.execute(
                "INSERT INTO clientes (nome, email) VALUES (%s, %s) RETURNING id", 
                (nome, email)
            )
        else:
            cur.execute(
                "INSERT INTO clientes (nome) VALUES (%s) RETURNING id", 
                (nome,)
            )
        
        id_inserido = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Nome '{nome}' inserido com sucesso!",
            "id": id_inserido
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao inserir: {str(e)}"
        }), 500

@app.route("/api/clientes", methods=["GET"])
def listar_clientes():
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id, nome, email FROM clientes ORDER BY id")
        clientes = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Converter para lista de dicionários
        resultado = []
        for cliente in clientes:
            resultado.append({
                "id": cliente[0],
                "nome": cliente[1],
                "email": cliente[2] or ""
            })
        
        return jsonify({"clientes": resultado})
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao listar: {str(e)}"
        }), 500

@app.route("/api/deletar/<int:id>", methods=["DELETE"])
def deletar_cliente(id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("DELETE FROM clientes WHERE id = %s", (id,))
        linhas_afetadas = cur.rowcount
        conn.commit()
        
        cur.close()
        conn.close()
        
        if linhas_afetadas > 0:
            return jsonify({
                "success": True,
                "message": f"Cliente ID {id} deletado com sucesso!"
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Cliente ID {id} não encontrado"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao deletar: {str(e)}"
        }), 500

# Arquivos estáticos
@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)