import os
import uuid
import sqlite3
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify, render_template_string, url_for

app = Flask(__name__)
DB_FILE = "base_vio_nacional.db"

def inicializar_banco():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS validacoes (
            id TEXT PRIMARY KEY,
            nome TEXT,
            placa TEXT,
            renavam TEXT,
            chassi_mascarado TEXT,
            modelo TEXT,
            ano TEXT,
            data_hora TEXT
        )
    ''')
    conn.commit()
    conn.close()

inicializar_banco()

HTML_ADMIN = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Admin - Gerador Vio Oficial</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #edf2f7; margin: 0; padding: 20px; }
        .admin-box { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        h2 { margin-top: 0; color: #004b82; border-bottom: 2px solid #edf2f7; padding-bottom: 10px; font-size: 18px; text-transform: uppercase; }
        .form-group { margin-bottom: 15px; }
        label { display: block; font-weight: 600; margin-bottom: 5px; font-size: 13px; color: #4a5568; }
        input { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        .btn { background: #004b82; color: white; border: none; padding: 12px 20px; font-size: 16px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 15px; text-transform: uppercase; }
        .result-box { display: none; margin-top: 25px; padding: 20px; background: #f8fafc; border: 2px dashed #23a95c; border-radius: 8px; text-align: center; }
        .qr-code { margin: 20px 0; display: inline-block; padding: 10px; background: white; border: 1px solid #e2e8f0; border-radius: 6px; min-height: 160px; min-width: 160px; }
        .link-url { word-break: break-all; font-weight: bold; color: #0056b3; text-decoration: none; display: block; margin-top: 10px; font-size: 14px; }
    </style>
</head>
<body>
<div class="admin-box">
    <h2>Painel de Controle - Emissão Vio</h2>
    <form id="formAdmin">
        <div class="form-group"><label>Nome Completo do Proprietário</label><input type="text" id="nome" required></div>
        <div class="form-group"><label>Placa</label><input type="text" id="placa" required></div>
        <div class="form-group"><label>RENAVAM</label><input type="text" id="renavam" required></div>
        <div class="form-group"><label>Chassi Completo</label><input type="text" id="chassi" required></div>
        <div class="form-group"><label>Marca / Modelo</label><input type="text" id="modelo" required></div>
        <div class="form-group"><label>Ano Fab / Ano Mod</label><input type="text" id="ano" placeholder="Ex: 2025/2026" required></div>
        <button type="button" class="btn" onclick="gerarAutenticacao()">Gerar Autenticação e QR Code</button>
    </form>
    <div class="result-box" id="resultBox">
        <h3 style="color: #23a95c; margin-top: 0;">✓ Registro Criado na Base de Dados Permanente!</h3>
        <p style="font-size: 14px;">Abaixo está o QR Code para você colocar no seu CRVL:</p>
        <div class="qr-code" id="qrContainer"></div>
        <p style="font-size: 14px;">Link direto da tela de validação do policial:</p>
        <a id="linkPolicial" class="link-url" target="_blank" href="#">Carregando...</a>
    </div>
</div>
<script src="https://unpkg.com"></script>
<script>
    async function gerarAutenticacao() {
        const payload = {
            nome: document.getElementById('nome').value,
            placa: document.getElementById('placa').value,
            renavam: document.getElementById('renavam').value,
            chassi: document.getElementById('chassi').value,
            modelo: document.getElementById('modelo').value,
            ano: document.getElementById('ano').value
        };
        const response = await fetch('/api/criar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        if(response.ok) {
            document.getElementById('linkPolicial').href = data.url_validacao;
            document.getElementById('linkPolicial').innerText = data.url_validacao;
            var qr = qrcode(4, 'L');
            qr.addData(data.url_validacao);
            qr.make();
            document.getElementById('qrContainer').innerHTML = qr.createImgTag(4);
            document.getElementById('resultBox').style.display = 'block';
        } else {
            alert('Erro ao processar dados no servidor.');
        }
    }
</script>
</body>
</html>
"""
HTML_POLICIAL = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Vio - Validação de Documentos Digitais</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f2f3f5; margin: 0; padding: 0; display: flex; justify-content: center; -webkit-font-smoothing: antialiased; }
        .vio-wrapper { width: 100%; max-width: 440px; background: #ffffff; min-height: 100vh; box-sizing: border-box; padding: 18px 20px; display: flex; flex-direction: column; box-shadow: 0 4px 25px rgba(0,0,0,0.08); margin: 0 auto; }
        .vio-app-header { text-align: center; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid #e1e8ed; display: flex; flex-direction: column; align-items: center; }
        .vio-app-header .brasao-logo { width: 22px; height: 22px; background: #004b82; border-radius: 4px; margin-bottom: 6px; display: inline-block; position: relative; }
        .vio-app-header .brasao-logo::after { content: "★"; color: white; font-size: 11px; position: absolute; top: 2px; left: 5px; }
        .vio-app-header .top-gov { font-size: 11px; font-weight: 700; color: #004b82; letter-spacing: 0.8px; margin: 0; text-transform: uppercase; }
        .vio-app-header .sub-gov { font-size: 13px; font-weight: 600; color: #5c6873; margin: 3px 0 0 0; }
        .success-banner { background-color: #eaf7ed; border: 1px solid #23a95c; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 22px; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .success-banner .check-circle { display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; background: #23a95c; color: white; border-radius: 50%; font-size: 11px; font-weight: bold; }
        .success-banner .status-title { font-size: 14px; font-weight: 800; color: #23a95c; margin: 0; letter-spacing: 0.5px; }
        .group-label { font-size: 11px; font-weight: 700; color: #657786; text-transform: uppercase; margin: 15px 0 6px 4px; letter-spacing: 0.5px; }
        .card-container { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 0 14px; margin-bottom: 15px; }
        .data-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f1f3f4; }
        .data-row:last-child { border-bottom: none; }
        .field-label { font-size: 13px; color: #657786; font-weight: 500; }
        .field-value { font-size: 13px; color: #14171a; font-weight: 700; text-align: right; }
        .footer-stamp { text-align: center; margin-top: auto; padding-top: 30px; }
        .footer-stamp .authority { font-size: 11px; font-weight: 700; color: #657786; margin: 0; }
        .footer-stamp .timestamp { font-size: 11px; font-weight: 500; color: #14171a; margin: 4px 0 0 0; }
        .legal-notice { font-size: 10px; color: #a4b0be; line-height: 14px; margin-top: 15px; padding: 0 10px; }
    </style>
</head>
<body>
<div class="phone-wrapper">
    <div class="vio-wrapper">
        <div class="vio-app-header">
            <div class="brasao-logo"></div>
            <p class="top-gov">SENATRAN · GOVERNO FEDERAL</p>
            <p class="sub-gov">Ministério dos Transportes</p>
        </div>
        <div class="success-banner">
            <div class="check-circle">✓</div>
            <h2 class="status-title">DOCUMENTO AUTÊNTICO</h2>
        </div>
        <div class="group-label">Veículo</div>
        <div class="card-container">
            <div class="data-row"><span class="field-label">Placa</span><span class="field-value">{{ dados[1] }}</span></div>
            <div class="data-row"><span class="field-label">RENAVAM</span><span class="field-value">{{ dados[2] }}</span></div>
            <div class="data-row"><span class="field-label">Chassi</span><span class="field-value">{{ dados[3] }}</span></div>
            <div class="data-row"><span class="field-label">Marca / Modelo</span><span class="field-value">{{ dados[4] }}</span></div>
            <div class="data-row"><span class="field-label">Ano</span><span class="field-value">{{ dados[5] }}</span></div>
        </div>
        <div class="group-label">Proprietário Atual</div>
        <div class="card-container">
            <div class="data-row"><span class="field-label">Nome / Nome Empresarial</span><span class="field-value" style="text-align: left; max-width: 220px; word-break: break-word;">{{ dados[0] }}</span></div>
        </div>
        <div class="footer-stamp">
            <p class="authority">Emitido por: SERPRO / SENATRAN</p>
            <p class="timestamp">Data/Hora da consulta: <span style="font-weight: 700;">{{ dados[6] }}</span></p>
            <p class="legal-notice">Este documento foi consultado diretamente na base de dados nacional. A autenticidade só é garantida através do aplicativo Vio.</p>
        </div>
    </div>
</div>
</body>
</html>
"""
@app.route('/')
@app.route('/admin')
def admin():
    return render_template_string(HTML_ADMIN)

@app.route('/api/criar', methods=['POST'])
def api_criar():
    dados = request.json
    if not dados:
        return jsonify({"error": "Dados inválidos"}), 400

    id_consulta = str(uuid.uuid4())[:8]
    chassi_original = dados.get('chassi', '').strip()
    ultimos_digitos = chassi_original[-4:] if len(chassi_original) >= 4 else chassi_original
    chassi_mascarado = f"***{ultimos_digitos.upper()}"

    fuso_brasilia = timezone(timedelta(hours=-3))
    data_hora_atual = datetime.now(fuso_brasilia).strftime("%d/%m/%Y %H:%M:%S")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO validacoes (id, nome, placa, renavam, chassi_mascarado, modelo, ano, data_hora)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        id_consulta,
        dados.get('nome', '').upper(),
        dados.get('placa', '').upper(),
        dados.get('renavam', ''),
        chassi_mascarado,
        dados.get('modelo', '').upper(),
        dados.get('ano', ''),
        data_hora_atual
    ))
    conn.commit()
    conn.close()

    url_completa = request.host_url.rstrip('/') + url_for('validar_policial', id_consulta=id_consulta)
    return jsonify({"id": id_consulta, "url_validacao": url_completa})

@app.route('/validar/<id_consulta>')
def validar_policial(id_consulta):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT nome, placa, renavam, chassi_mascarado, modelo, ano, data_hora FROM validacoes WHERE id = ?', (id_consulta,))
    registro = cursor.fetchone()
    conn.close()

    if not registro:
        return "<h3>Erro 404: Registro não encontrado na base de dados nacional do SENATRAN.</h3>", 404
        
    return render_template_string(HTML_POLICIAL, dados=registro)

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
