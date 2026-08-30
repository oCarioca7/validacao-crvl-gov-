import os
import uuid
import sqlite3
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify, render_template, Response

app = Flask(__name__)
DB_FILE = "base_vio_nacional.db"

def inicializar_banco():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS validacoes (
        id TEXT PRIMARY KEY,
        nome TEXT,
        placa TEXT,
        renavam TEXT,
        chassi_mascarado TEXT,
        modelo TEXT,
        ano TEXT,
        data_hora TEXT
    )''')
    conn.commit()
    conn.close()

inicializar_banco()

@app.route('/')
def admin():
    return render_template('admin.html')

@app.route('/manifest.json')
def manifest():
    manifest_data = """{
        "name": "Vio - Validador",
        "short_name": "Vio",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#002d56",
        "theme_color": "#002d56",
        "icons": [
            {
                "src": "https://icons8.com",
                "sizes": "192x192",
                "type": "image/png"
            }
        ]
    }"""
    return Response(manifest_data, mimetype='application/json')

@app.route('/api/criar', methods=['POST'])
def criar_registro():
    dados = request.get_json() or {}
    novo_id = str(uuid.uuid4())
    
    chassi = dados.get('chassi', '').strip()
    if len(chassi) >= 6:
        chassi_mascarado = chassi[:3] + ("*" * (len(chassi) - 7)) + chassi[-4:]
    else:
        chassi_mascarado = chassi

    fuso_br = timezone(timedelta(hours=-3))
    data_hora_atual = datetime.now(fuso_br).strftime('%d/%m/%Y %H:%M:%S')

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO validacoes (id, nome, placa, renavam, chassi_mascarado, modelo, ano, data_hora)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
        novo_id,
        dados.get('nome', '').upper(),
        dados.get('placa', '').upper(),
        dados.get('renavam', ''),
        chassi_mascarado.upper(),
        dados.get('modelo', '').upper(),
        dados.get('ano', ''),
        data_hora_atual
    ))
    conn.commit()
    conn.close()

    url_base = request.host_url.rstrip('/')
    url_validacao = f"{url_base}/validar/{novo_id}"

    return jsonify({"status": "sucesso", "id": novo_id, "url_validacao": url_validacao})

@app.route('/validar/<doc_id>')
def validar(doc_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT nome, placa, renavam, chassi_mascarado, modelo, ano, data_hora FROM validacoes WHERE id = ?', (doc_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        dados = {
            "nome": row,
            "placa": row,
            "renavam": row,
            "chassi_mascarado": row,
            "modelo": row,
            "ano": row,
            "data_hora": row
        }
        return render_template('validacao.html', dados=dados)
    else:
        return "<h3>Documento não encontrado na Base Nacional.</h3>", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
