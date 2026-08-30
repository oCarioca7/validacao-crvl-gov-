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

HTML_ADMIN = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Admin - Emissor Vio CRLV-e</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #edf2f7; margin: 0; padding: 20px; }
        .admin-box { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        h2 { margin-top: 0; color: #004b82; border-bottom: 2px solid #edf2f7; padding-bottom: 10px; font-size: 18px; text-transform: uppercase; }
        .form-group { margin-bottom: 15px; }
        label { display: block; font-weight: 600; margin-bottom: 5px; font-size: 13px; color: #4a5568; }
        input { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        .btn { background: #004b82; color: white; border: none; padding: 12px 20px; font-size: 16px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 15px; text-transform: uppercase; }
        .result-box { display: none; margin-top: 25px; padding: 20px; background: #f8fafc; border: 2px dashed #23a95c; border-radius: 8px; text-align: center; }
        .qr-code { margin: 20px 0; display: inline-block; padding: 10px; background: white; border: 1px solid #e2e8f0; border-radius: 6px; min-height: 160px; }
        .link-url { word-break: break-all; font-weight: bold; color: #0056b3; text-decoration: none; display: block; margin-top: 10px; font-size: 14px; }
    </style>
</head>
<body>
<div class="admin-box">
    <h2>Painel de Emissão CRLV-e - Vio Original</h2>
    <form id="formAdmin">
        <div class="form-group"><label>Nome Completo do Proprietário</label><input type="text" id="nome" required></div>
        <div class="form-group"><label>Placa</label><input type="text" id="placa" required></div>
        <div class="form-group"><label>RENAVAM</label><input type="text" id="renavam" required></div>
        <div class="form-group"><label>Chassi Completo</label><input type="text" id="chassi" required></div>
        <div class="form-group"><label>Marca / Modelo</label><input type="text" id="modelo" required></div>
        <div class="form-group"><label>Ano</label><input type="text" id="ano" placeholder="Ex: 2025" required></div>
        <button type="button" class="btn" onclick="gerarAutenticacao()">Gerar Autenticação e QR Code</button>
    </form>
    <div class="result-box" id="resultBox">
        <h3 style="color: #23a95c; margin-top: 0;">✓ Registro Criado na Base Nacional!</h3>
        <p style="font-size: 14px; margin: 0;">Abaixo está o QR Code para você colocar no documento do veículo:</p>
        <div class="qr-code" id="qrContainer"></div>
        <p style="font-size: 14px; margin: 0;">Link direto de fiscalização (Tela do Policial):</p>
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
        alert('Erro ao processar dados.');
    }
}
</script>
</body>
</html>"""
"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Vio - Validação de Documentos Digitais</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f5f6f8; margin: 0; padding: 0; display: flex; justify-content: center; -webkit-font-smoothing: antialiased; }
        .vio-wrapper { width: 100%; max-width: 450px; background: #ffffff; min-height: 100vh; box-sizing: border-box; padding: 0; display: flex; flex-direction: column; box-shadow: 0 4px 20px rgba(0,0,0,0.05); margin: 0 auto; }
        .vio-top-navbar { background: #002d56; color: white; display: flex; align-items: center; justify-content: space-between; padding: 14px 16px; box-sizing: border-box; }
        .vio-top-navbar .nav-left { display: flex; align-items: center; gap: 14px; font-size: 20px; cursor: pointer; }
        .vio-top-navbar .nav-title-app { font-size: 16px; font-weight: 700; letter-spacing: 0.3px; }
        .vio-top-navbar .nav-right { font-size: 18px; font-weight: bold; cursor: pointer; opacity: 0.8; }
        .main-scroll-content { padding: 16px 18px; display: flex; flex-direction: column; flex: 1; }
        .vio-app-header { text-align: center; margin-bottom: 16px; display: flex; flex-direction: column; align-items: center; }
        .vio-app-header .top-gov { font-size: 10px; font-weight: 700; color: #004b82; letter-spacing: 0.6px; margin: 0; text-transform: uppercase; }
        .vio-app-header .sub-gov { font-size: 12px; font-weight: 600; color: #546e7a; margin: 3px 0 0 0; }
        .success-banner { background-color: #eaf7ed; border: 1px solid #23a95c; border-radius: 8px; padding: 11px 14px; text-align: center; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .success-banner .check-circle { display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; background: #23a95c; color: white; border-radius: 50%; font-size: 12px; font-weight: bold; }
        .success-banner .status-title { font-size: 14px; font-weight: 800; color: #23a95c; margin: 0; letter-spacing: 0.3px; }
        .group-label { font-size: 11px; font-weight: 700; color: #78909c; text-transform: uppercase; margin: 14px 0 6px 4px; letter-spacing: 0.5px; }
        .card-container { background: #ffffff; border: 1px solid #cfd8dc; border-radius: 8px; padding: 0 14px; margin-bottom: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.01); }
        .data-row { display: flex; justify-content: space-between; align-items: flex-start; padding: 11px 0; border-bottom: 1px solid #f1f3f4; }
        .data-row:last-child { border-bottom: none; }
        .field-label { font-size: 13px; color: #607d8b; font-weight: 500; padding-top: 1px; }
        .field-value { font-size: 13px; color: #212121; font-weight: 700; text-align: right; max-width: 210px; word-break: break-word; }
        .footer-stamp { text-align: center; margin-top: auto; padding-top: 25px; border-top: 1px solid #e1e8ed; }
        .footer-stamp .authority { font-size: 11px; font-weight: 700; color: #546e7a; margin: 0; }
        .footer-stamp .timestamp { font-size: 11px; font-weight: 500; color: #212121; margin: 4px 0 0 0; }
        .legal-notice { font-size: 10px; color: #90a4ae; line-height: 14px; margin-top: 14px; padding: 0 10px; }
    </style>
</head>
<body>
<div class="vio-wrapper">
    <div class="vio-top-navbar">
        <div class="nav-left"><span>←</span> <span class="nav-title-app">Resultado da consulta</span></div>
        <div class="nav-right">⋮</div>
    </div>
    <div class="main-scroll-content">
        <div class="vio-app-header">
            <p class="top-gov">SENATRAN · GOVERNO FEDERAL</p>
            <p class="sub-gov">Ministério dos Transportes</p>
        </div>
        <div class="success-banner">
            <div class="check-circle">✓</div>
            <h2 class="status-title">DOCUMENTO AUTÊNTICO</h2>
        </div>
        <div class="label-grupo">Veículo</div>
        <div class="card-container">
            <div class="data-row"><span class="field-label">Placa</span><span class="field-value">{{ dados[1] }}</span></div>
            <div class="data-row"><span class="field-label">RENAVAM</span><span class="field-value">{{ dados[2] }}</span></div>
            <div class="data-row"><span class="field-label">Chassi</span><span class="field-value">{{ dados[3] }}</span></div>
            <div class="data-row"><span class="field-label">Marca / Modelo</span><span class="field-value">{{ dados[4] }}</span></div>
            <div class="data-row"><span class="field-label">Ano</span><span class="field-value">{{ dados[5] }}</span></div>
        </div>
        <div class="label-grupo">Proprietário Atual</div>
        <div class="card-container">
            <div class="data-row"><span class="field-label">Nome / Nome Empresarial</span><span class="field-value">{{ dados[0] }}</span></div>
        </div>
        <div class="footer-stamp">
            <p class="authority">Emitido por: SERPRO / SENATRAN</p>
            <p class="timestamp">Data/Hora da consulta: <span style="font-weight: 700;">{{ dados[6] }}</span></p>
            <p class="legal-notice">Este documento foi consultado diretamente na base de dados nacional. A autenticidade só é garantida através do aplicativo Vio.</p>
        </div>@app.route('/')
@app.route('/admin')
def admin():
    return render_template_string(HTML_ADMIN)

@app.route('/api/criar', methods=['POST'])
def api_criar():
    dados = request.json
    if not dados:
        return jsonify({"error": "Dados inválidos"}), 400

    id_consulta = str(uuid.uuid4())[:8]
    chassi_orig = dados.get('chassi', '').strip()
    ultimos_chassi = chassi_orig[-4:] if len(chassi_orig) >= 4 else chassi_orig
    chassi_mascarado = f"***{ultimos_chassi.upper()}"

    fuso_brasilia = timezone(timedelta(hours=-3))
    data_hora_atual = datetime.now(fuso_brasilia).strftime("%d/%m/%Y %H:%M:%S")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO validacoes (
        id, nome, placa, renavam, chassi_mascarado, modelo, ano, data_hora
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
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
