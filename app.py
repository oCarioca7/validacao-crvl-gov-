import os
import uuid
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify, render_template_string, url_for

app = Flask(__name__)
BANCO_DADOS = {}

HTML_ADMIN = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Admin - Gerador Vio</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 30px; }
        .admin-box { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        h2 { margin-top: 0; color: #1a365d; border-bottom: 2px solid #edf2f7; padding-bottom: 10px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; font-weight: 600; margin-bottom: 5px; font-size: 13px; color: #4a5568; }
        input[type="text"] { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        .btn { background: #23a95c; color: white; border: none; padding: 12px 20px; font-size: 16px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 15px; }
        .result-box { display: none; margin-top: 25px; padding: 20px; background: #f8fafc; border: 1px dashed #23a95c; border-radius: 8px; text-align: center; }
        .qr-code { margin: 20px 0; display: inline-block; padding: 10px; background: white; border: 1px solid #e2e8f0; }
        .link-url { word-break: break-all; font-weight: bold; color: #0056b3; text-decoration: none; display: block; margin-top: 10px; }
    </style>
</head>
<body>
<div class="admin-box">
    <h2>Painel de Controle - Emissão Vio</h2>
    <form id="formAdmin">
        <div class="form-group"><label>Nome Completo do Proprietário</label><input type="text" id="nome" required></div>
        <div class="form-group"><label>CPF / CNPJ do Proprietário</label><input type="text" id="doc_proprietario" placeholder="Ex: 000.000.000-00"></div>
        <div class="form-group"><label>Placa</label><input type="text" id="placa" required></div>
        <div class="form-group"><label>RENAVAM</label><input type="text" id="renavam" required></div>
        <div class="form-group"><label>Chassi Completo</label><input type="text" id="chassi" required></div>
        <div class="form-group"><label>Marca / Modelo</label><input type="text" id="modelo" required></div>
        <div class="form-group"><label>Ano Fabricação / Ano Modelo</label><input type="text" id="ano" placeholder="Ex: 2023/2024" required></div>
        <div class="form-group"><label>Código de Segurança do CLA</label><input type="text" id="cla_seguranca"></div>
        <div class="form-group"><label>Número do CRV</label><input type="text" id="crv_numero"></div>
        <button type="button" class="btn" onclick="gerarAutenticacao()">Gerar Registro e QR Code</button>
    </form>
    <div class="result-box" id="resultBox">
        <h3 style="color: #23a95c; margin-top: 0;">✓ Registro Criado com Sucesso!</h3>
        <p>Abaixo está o QR Code para você embutir no seu CRVL:</p>
        <div class="qr-code" id="qrContainer"></div>
        <p>Link direto da tela de validação do policial:</p>
        <a id="linkPolicial" class="link-url" target="_blank" href="#">Carregando...</a>
    </div>
</div>
<script>
    async function gerarAutenticacao() {
        const payload = {
            nome: document.getElementById('nome').value,
            doc_proprietario: document.getElementById('doc_proprietario').value,
            placa: document.getElementById('placa').value,
            renavam: document.getElementById('renavam').value,
            chassi: document.getElementById('chassi').value,
            modelo: document.getElementById('modelo').value,
            ano: document.getElementById('ano').value,
            cla_seguranca: document.getElementById('cla_seguranca').value,
            crv_numero: document.getElementById('crv_numero').value
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
            document.getElementById('qrContainer').innerHTML = `<img src="https://qrserver.com{encodeURIComponent(data.url_validacao)}" alt="QR Code Vio">`;
            document.getElementById('resultBox').style.display = 'block';
        } else {
            alert('Erro ao processar dados.');
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resultado da Consulta - Vio</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f7f9fa; margin: 0; padding: 0; display: flex; justify-content: center; }
        .phone-wrapper { width: 100%; max-width: 450px; background: white; min-height: 100vh; box-sizing: border-box; padding: 20px; display: flex; flex-direction: column; }
        .vio-app-header { text-align: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #e1e8ed; }
        .vio-app-header .top-gov { font-size: 11px; font-weight: bold; color: #004b82; letter-spacing: 0.8px; margin: 0; }
        .vio-app-header .sub-gov { font-size: 13px; font-weight: 600; color: #5c6873; margin: 4px 0 0 0; }
        .success-banner { background-color: #e6f6ec; border: 1.5px solid #23a95c; border-radius: 12px; padding: 18px; text-align: center; margin-bottom: 22px; }
        .success-banner .check-circle { display: inline-flex; align-items: center; justify-content: center; width: 34px; height: 34px; background: #23a95c; color: white; border-radius: 50%; font-size: 18px; font-weight: bold; margin-bottom: 8px; }
        .success-banner .status-title { font-size: 16px; font-weight: 800; color: #23a95c; margin: 0; letter-spacing: 0.5px; }
        .group-label { font-size: 12px; font-weight: 700; color: #657786; text-transform: uppercase; margin: 15px 0 6px 4px; letter-spacing: 0.5px; }
        .card-container { background: #f8fafc; border: 1px solid #e6ecf0; border-radius: 12px; padding: 8px 16px; margin-bottom: 15px; }
        .data-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #e6ecf0; }
        .data-row:last-child { border-bottom: none; }
        .field-label { font-size: 13px; color: #657786; font-weight: 500; }
        .field-value { font-size: 14px; color: #14171a; font-weight: 700; text-align: right; }
        .footer-stamp { text-align: center; margin-top: auto; padding-top: 30px; }
        .footer-stamp .authority { font-size: 11px; font-weight: 700; color: #657786; margin: 0; }
        .footer-stamp .timestamp { font-size: 11px; font-weight: 500; color: #14171a; margin: 4px 0 0 0; }
        .legal-notice { font-size: 10px; color: #a4b0be; line-height: 14px; margin-top: 15px; padding: 0 10px; }
    </style>
</head>
<body>
<div class="phone-wrapper">
    <div class="vio-app-header">
        <p class="top-gov">SENATRAN · GOVERNO FEDERAL</p>
        <p class="sub-gov">Ministério dos Transportes</p>
    </div>
    <div class="success-banner">
        <div class="check-circle">✓</div>
        <h2 class="status-title">DOCUMENTO AUTÊNTICO</h2>
    </div>
    <div class="group-label">Veículo</div>
    <div class="card-container">
        <div class="data-row"><span class="field-label">Placa</span><span class="field-value">{{ dados.placa }}</span></div>
        <div class="data-row"><span class="field-label">RENAVAM</span><span class="field-value">{{ dados.renavam }}</span></div>
        <div class="data-row"><span class="field-label">Chassi</span><span class="field-value">{{ dados.chassi_mascarado }}</span></div>
        <div class="data-row"><span class="field-label">Marca/Modelo</span><span class="field-value">{{ dados.modelo }}</span></div>
        <div class="data-row"><span class="field-label">Ano</span><span class="field-value">{{ dados.ano }}</span></div>
    </div>
    <div class="group-label">Proprietário Atual</div>
    <div class="card-container">
        <div class="data-row"><span class="field-label">Nome Completo</span><span class="field-value" style="text-align: left; max-width: 240px;">{{ dados.nome }}</span></div>
        <div class="data-row"><span class="field-label">CPF / CNPJ</span><span class="field-value">{{ dados.doc_proprietario }}</span></div>
    </div>
    <div class="group-label">Documento</div>
    <div class="card-container">
        <div class="data-row"><span class="field-label">Código de Segurança CLA</span><span class="field-value">{{ dados.cla_seguranca }}</span></div>
        <div class="data-row"><span class="field-label">Número do CRV</span><span class="field-value">{{ dados.crv_numero }}</span></div>
    </div>
    <div class="footer-stamp">
        <p class="authority">Emitido por: SERPRO / SENATRAN</p>
        <p class="timestamp">Data/Hora da consulta: <span style="font-weight: 700;">{{ dados.data_hora }}</span></p>
        <p class="legal-notice">Este documento foi consultado diretamente na base de dados nacional. A autenticidade só é garantida através do aplicativo Vio.</p>
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

    BANCO_DADOS[id_consulta] = {
        "nome": dados.get('nome', '').upper(),
        "doc_proprietario": dados.get('doc_proprietario', '') or "---",
        "placa": dados.get('placa', '').upper(),
        "renavam": dados.get('renavam', ''),
        "chassi_mascarado": chassi_mascarado,
        "modelo": dados.get('modelo', '').upper(),
        "ano": dados.get('ano', ''),
        "cla_seguranca": dados.get('cla_seguranca', '') or "---",
        "crv_numero": dados.get('crv_numero', '') or "---",
        "data_hora": data_hora_atual
    }

    url_completa = request.host_url.rstrip('/') + url_for('validar_policial', id_consulta=id_consulta)
    return jsonify({"id": id_consulta, "url_validacao": url_completa})

@app.route('/validar/<id_consulta>')
def validar_policial(id_consulta):
    registro = BANCO_DADOS.get(id_consulta)
    if not registro:
        return "<h3>Erro 404: Registro não encontrado.</h3>", 404
    return render_template_string(HTML_POLICIAL, dados=registro)

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
