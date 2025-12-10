from flask import Flask, send_from_directory, request, jsonify, session
from db import get_connection
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.secret_key = 'disk-cerveja-key-123'

# ========== ROTAS DE PRODUTOS ==========
@app.route("/api/produtos", methods=["GET"])
def listar_produtos():
    """Lista todos os produtos"""
    conn = get_connection()
    if not conn:
        return jsonify({"success": False, "message": "Banco offline"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nome, categoria, preco_custo, preco_venda, 
                   estoque, unidade, criado_em 
            FROM produtos 
            ORDER BY nome
        """)
        produtos_db = cur.fetchall()
        
        produtos = []
        for p in produtos_db:
            produtos.append({
                "id": p[0],
                "nome": p[1],
                "categoria": p[2],
                "preco_custo": float(p[3]) if p[3] else 0,
                "preco_venda": float(p[4]),
                "estoque": p[5],
                "unidade": p[6],
                "criado_em": p[7].strftime("%d/%m/%Y") if p[7] else ""
            })
        
        return jsonify({"success": True, "produtos": produtos})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

@app.route("/api/produtos", methods=["POST"])
def criar_produto():
    """Cria novo produto"""
    data = request.get_json()
    
    nome = data.get('nome', '').strip()
    categoria = data.get('categoria', '').strip()
    preco_venda = data.get('preco_venda', 0)
    estoque = data.get('estoque', 0)
    
    if not nome or preco_venda <= 0:
        return jsonify({"success": False, "message": "Nome e preço são obrigatórios!"}), 400
    
    conn = get_connection()
    if not conn:
        return jsonify({"success": False, "message": "Banco offline"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO produtos 
            (nome, categoria, preco_venda, estoque, unidade) 
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING id
        """, (nome, categoria, preco_venda, estoque, data.get('unidade', 'UN')))
        
        id_inserido = cur.fetchone()[0]
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"Produto '{nome}' criado!",
            "id": id_inserido
        })
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

@app.route("/api/produtos/<int:id>", methods=["PUT"])
def atualizar_produto(id):
    """Atualiza produto"""
    data = request.get_json()
    
    conn = get_connection()
    if not conn:
        return jsonify({"success": False, "message": "Banco offline"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE produtos SET 
                nome = %s,
                categoria = %s,
                preco_venda = %s,
                estoque = %s,
                unidade = %s
            WHERE id = %s
            RETURNING id
        """, (
            data.get('nome', '').strip(),
            data.get('categoria', '').strip(),
            data.get('preco_venda', 0),
            data.get('estoque', 0),
            data.get('unidade', 'UN'),
            id
        ))
        
        if cur.rowcount > 0:
            conn.commit()
            return jsonify({"success": True, "message": "Produto atualizado!"})
        else:
            return jsonify({"success": False, "message": "Produto não encontrado"}), 404
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

@app.route("/api/produtos/<int:id>", methods=["DELETE"])
def deletar_produto(id):
    """Deleta produto"""
    conn = get_connection()
    if not conn:
        return jsonify({"success": False, "message": "Banco offline"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM produtos WHERE id = %s", (id,))
        conn.commit()
        
        if cur.rowcount > 0:
            return jsonify({"success": True, "message": "Produto deletado!"})
        else:
            return jsonify({"success": False, "message": "Produto não encontrado"}), 404
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

# Adicione esta rota para buscar por código de barras
@app.route("/api/produtos/codigo/<codigo>", methods=["GET"])
def buscar_produto_codigo(codigo):
    """Busca produto por código de barras"""
    conn = get_connection()
    if not conn:
        return jsonify({"success": False, "message": "Banco offline"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nome, categoria, preco_venda, estoque, unidade, codigo_barras
            FROM produtos 
            WHERE codigo_barras = %s
        """, (codigo,))
        
        produto_db = cur.fetchone()
        
        if produto_db:
            produto = {
                "id": produto_db[0],
                "nome": produto_db[1],
                "categoria": produto_db[2],
                "preco_venda": float(produto_db[3]),
                "estoque": produto_db[4],
                "unidade": produto_db[5],
                "codigo_barras": produto_db[6]
            }
            return jsonify({"success": True, "produto": produto})
        else:
            return jsonify({"success": False, "message": "Produto não encontrado"}), 404
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

# ========== ROTAS DE VENDAS ==========

@app.route("/api/vendas", methods=["POST"])
def criar_venda():
    """Cria nova venda"""
    try:
        data = request.get_json()
        print(f"DEBUG: Dados recebidos: {data}")  # Log para debug
        
        cliente_nome = data.get('cliente_nome', '').strip()
        forma_pagamento = data.get('forma_pagamento', 'Dinheiro')
        itens = data.get('itens', [])
        
        if not itens:
            return jsonify({"success": False, "message": "Nenhum item na venda!"}), 400
        
        conn = get_connection()
        if not conn:
            return jsonify({"success": False, "message": "Banco offline"}), 500
        
        cur = conn.cursor()
        
        # Calcular subtotal
        subtotal = sum(item['quantidade'] * item['preco_unitario'] for item in itens)
        
        # Calcular desconto (simples)
        tipo_desconto = data.get('tipo_desconto', 'valor')
        desconto = 0
        
        if tipo_desconto == 'valor':
            desconto = data.get('valor_desconto', 0)
        elif tipo_desconto == 'percentual':
            percentual = data.get('percentual_desconto', 0)
            desconto = subtotal * (percentual / 100)
        
        total = subtotal - desconto
        
        # Criar venda (SEM subtotal na query por enquanto)
        cur.execute("""
            INSERT INTO vendas 
            (cliente_nome, total, forma_pagamento) 
            VALUES (%s, %s, %s) 
            RETURNING id
        """, (cliente_nome, total, forma_pagamento))
        
        venda_id = cur.fetchone()[0]
        
        # Adicionar itens
        for item in itens:
            cur.execute("""
                INSERT INTO venda_itens (venda_id, produto_id, quantidade, preco_unitario)
                VALUES (%s, %s, %s, %s)
            """, (venda_id, item['produto_id'], item['quantidade'], item['preco_unitario']))
            
            # Atualizar estoque
            cur.execute("""
                UPDATE produtos 
                SET estoque = estoque - %s 
                WHERE id = %s
            """, (item['quantidade'], item['produto_id']))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Venda #{venda_id} criada! Total: R$ {total:.2f}",
            "venda_id": venda_id,
            "total": total
        })
        
    except Exception as e:
        print(f"❌ ERRO NA VENDA: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Erro no servidor: {str(e)}"
        }), 500

@app.route("/api/vendas", methods=["GET"])
def listar_vendas():
    """Lista vendas recentes"""
    conn = get_connection()
    if not conn:
        return jsonify({"success": False, "message": "Banco offline"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT v.*, 
                   COUNT(vi.id) as num_itens
            FROM vendas v
            LEFT JOIN venda_itens vi ON v.id = vi.venda_id
            GROUP BY v.id
            ORDER BY v.data_venda DESC
            LIMIT 50
        """)
        vendas_db = cur.fetchall()
        
        vendas = []
        for v in vendas_db:
            vendas.append({
                "id": v[0],
                "cliente_nome": v[1],
                "total": float(v[2]),
                "forma_pagamento": v[3],
                "data_venda": v[4].strftime("%d/%m/%Y %H:%M"),
                "num_itens": v[5]
            })
        
        return jsonify({"success": True, "vendas": vendas})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

# ========== ROTAS INDEX/LOGIN ==========
@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/dashboard")
def dashboard():
    return send_from_directory(BASE_DIR, "dashboard.html")

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if username == "admin" and password == "admin123":
        session['loggedIn'] = True
        session['username'] = username
        session['nomeCompleto'] = "Administrador Sistema"
        return jsonify({"success": True, "message": "Login realizado!"})
    
    return jsonify({"success": False, "message": "Credenciais inválidas!"}), 401

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logout realizado!"})

@app.route("/api/auth/status", methods=["GET"])
def auth_status():
    if 'loggedIn' in session and session['loggedIn']:
        return jsonify({"loggedIn": True, "user": {"username": session.get('username')}})
    return jsonify({"loggedIn": False})

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)

@app.route("/api/dashboard/vendas-hoje", methods=["GET"])
def vendas_hoje():
    """Retorna o total de vendas do dia atual"""
    conn = get_connection()
    if not conn:
        return jsonify({"success": False, "total": 0}), 500
    
    try:
        cur = conn.cursor()
        # Busca vendas de hoje (data atual)
        cur.execute("""
            SELECT COALESCE(SUM(total), 0) as total_hoje
            FROM vendas 
            WHERE DATE(data_venda) = CURRENT_DATE
            AND status = 'Concluída'
        """)
        
        resultado = cur.fetchone()
        total_hoje = float(resultado[0]) if resultado else 0
        
        cur.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "total_hoje": total_hoje
        })
        
    except Exception as e:
        print(f"Erro ao buscar vendas hoje: {e}")
        return jsonify({"success": False, "total": 0}), 500
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)