from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Configuração do banco de dados SQLite
DATABASE = "controle_acessos.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

pnconfig = PNConfiguration()
pnconfig.publish_key = "pub-c-bd70df2f-77cb-4ddb-94ad-4b66a060a2cd"
pnconfig.subscribe_key = "sub-c-311e7b27-3a38-47dd-b389-936d390ed97a"
pnconfig.uuid = "servidor-api"  
pubnub = PubNub(pnconfig)

pubnub = PubNub(pnconfig)

# Criar tabelas no banco de dados
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS colaboradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            permissao TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            colaborador_id INTEGER,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            horario TEXT NOT NULL,
            FOREIGN KEY (colaborador_id) REFERENCES colaboradores (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

# Enviar logs para o PubNub
def enviar_log_pubnub(log):
    pubnub.publish().channel("logs_acesso").message(log).sync()

# ------------------ ROTAS ------------------

@app.route("/", methods=["GET"])
def index():
    return "API de Controle de Acesso está rodando!"

# 📌 LISTAR TODOS OS COLABORADORES
@app.route("/colaboradores", methods=["GET"])
def listar_colaboradores():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM colaboradores;")
    colaboradores = cursor.fetchall()
    conn.close()
    return jsonify([dict(col) for col in colaboradores])

# 📌 ADICIONAR UM NOVO COLABORADOR
@app.route("/colaboradores", methods=["POST"])
def adicionar_colaborador():
    data = request.json
    nome = data.get("nome")
    permissao = data.get("permissao")

    if not nome or not permissao:
        return jsonify({"error": "Nome e permissão são obrigatórios"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO colaboradores (nome, permissao) VALUES (?, ?);", (nome, permissao))
    conn.commit()
    colaborador_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": colaborador_id, "message": "Colaborador adicionado com sucesso!"}), 201

# 📌 EDITAR UM COLABORADOR EXISTENTE
@app.route("/colaboradores/<int:id>", methods=["PUT"])
def editar_colaborador(id):
    data = request.json
    nome = data.get("nome")
    permissao = data.get("permissao")

    if not nome or not permissao:
        return jsonify({"error": "Nome e permissão são obrigatórios"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE colaboradores SET nome = ?, permissao = ? WHERE id = ?;", (nome, permissao, id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Colaborador atualizado com sucesso!"})

# 📌 EXCLUIR UM COLABORADOR
@app.route("/colaboradores/<int:id>", methods=["DELETE"])
def excluir_colaborador(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM colaboradores WHERE id = ?;", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Colaborador excluído com sucesso!"})

# 📌 LISTAR TODOS OS LOGS
@app.route("/logs", methods=["GET"])
def listar_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs ORDER BY horario DESC;")
    logs = cursor.fetchall()
    conn.close()
    return jsonify([dict(log) for log in logs])

# 📌 ADICIONAR UM LOG (Acesso ou Bloqueado)
@app.route("/logs", methods=["POST"])
def adicionar_log():
    data = request.json
    colaborador_id = data.get("colaborador_id")
    nome = data.get("nome")
    tipo = data.get("tipo")

    if not colaborador_id or not nome or not tipo:
        return jsonify({"error": "ID do colaborador, nome e tipo são obrigatórios"}), 400

    horario = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (colaborador_id, nome, tipo, horario) VALUES (?, ?, ?, ?)",
                   (colaborador_id, nome, tipo, horario))
    conn.commit()
    conn.close()

    log_data = {
        "colaborador_id": colaborador_id,
        "nome": nome,
        "tipo": tipo,
        "horario": horario
    }
    enviar_log_pubnub(log_data)

    return jsonify({"message": "Log recebido e armazenado com sucesso!"}), 201

# ------------------ INICIALIZAÇÃO ------------------

if __name__ == "__main__":
    create_tables()
    app.run(host="0.0.0.0", port=5000, debug=True)
