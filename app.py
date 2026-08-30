import os
import uuid
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify, render_template_string, url_for

app = Flask(__name__)
BANCO_DADOS = {}

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema Vio Oficial - SENATRAN</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 1000px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .panel { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: fit-content; }
        h2 { margin-top: 0; color: #004b82; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; font-size: 18px; }
        .form-group { margin-bottom: 12px; }
        label { display: block; font-weight: 600; margin-bottom: 4px; color: #34495e; font-size: 13px; }
        input[type="text"] { width: 100%; padding: 10px 12px; border: 1px solid #ccd1d9; border-radius: 6px; box-sizing: border-box; background-color: #fdfdfd; font-size: 14px; color: #444; }
        .btn-emissao { background: #004b82; color: white; border: none; padding: 14px; font-size: 15px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 15px; text-transform: uppercase; }
        .result-box { display: none; margin-top: 25px; padding: 20px; background: #f8fafc; border: 2px dashed #23a95c; border-radius: 8px; text-align: center; }
        .qr-display { margin: 15px 0; display: inline-block; padding: 10px; background: white; border: 1px solid #e2e8f0; border-radius: 6px; }
        .link-output { word-break: break-all; font-weight: bold; color: #004b82; text-decoration: none; display: block; margin-top: 10px; font-size: 14px; }
        .phone-wrapper { width: 100%; max-width: 410px; background: #ffffff; min-height: 680px; border-radius: 24px; box-shadow: 0 12px 30px rgba(0,0,0,0.15); padding: 20px; box-sizing: border-box; margin: 0 auto; display: flex; flex-direction: column; }
        .vio-header-app { text-align: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #e1e8ed; }
        .vio-header-app .title-gov { font-size: 11px; font-weight: 700; color: #004b82; letter-spacing: 0.8px; margin: 0; text-transform: uppercase; }
        .vio-header-app .sub-gov { font-size: 13px; font-weight: 600; color: #5c6873; margin: 3px 0 0 0; }
        .banner-autentico { background-color: #eaf7ed; border: 1px solid #23a95c; border-radius: 12px; padding: 14px; text-align: center; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .banner-autentico .check-badge { display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; background: #23a95c; color: white; border-radius: 50%; font-size: 13px; font-weight: bold; }
        .banner-autentico .txt-status { font-size: 15px; font-weight: 800; color: #23a95c; margin: 0; letter-spacing: 0.3px; }
        .label-grupo { font-size: 11px; font-weight: 700; color: #657786; text-transform: uppercase; margin: 14px 0 6px 4px; letter-spacing: 0.5px; }
        .container-dados { background: #f8fafc; border: 1px solid #e6ecf0; border-radius: 12px; padding: 4px 14px; margin-bottom: 12px; }
        .linha-dados { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #e6ecf0; }
        .linha-dados:last-child { border-bottom: none; }
        .lbl-campo { font-size: 13px; color: #657786; font-weight: 500; }
        .val-campo { font-size: 13px; color: #14171a; font-weight: 700; text-align: right; }
        .rodape-fiscalizacao { text-align: center; margin-top: auto; padding-top: 30px; }
        .rodape-fiscalizacao .orgao { font-size: 11px; font-weight: 700; color: #657786; margin: 0; }
        .rodape-fiscalizacao .data-hora { font-size: 11px; font-weight: 500; color: #14171a; margin: 3px 0 0 0; }
        .rodape-fiscalizacao .aviso-legal { font-size: 10px; color: #a4b0be; line-height: 14px; margin-top: 15px; padding: 0 5px; }
    </style>
</head>
<body>
"""
HTML_DADOS = """
<div class="container">
    <div class="panel">
        <h2>Painel Administrativo - Emissão Vio</h2>
        <form id="adminForm">
            <div class="form-group"><label>Nome Completo do Proprietário</label><input type="text" id="nome" required></div>
            <div class="form-group"><label>Placa</label><input type="text" id="placa" required></div>
            <div class="form-group"><label>RENAVAM</label><input type="text" id="renavam" required></div>
            <div class="form-group"><label>Chassi Completo</label><input type="text" id="chassi" required></div>
            <div class="form-group"><label>Marca / Modelo</label><input type="text" id="modelo" required></div>
            <div class="form-group"><label>Ano Fab / Ano Mod</label><input type="text" id="ano" required></div>
            <button type="button" class="btn-emissao" onclick="emitirRegistro()">Gerar Registro e QR Code</button>
        </form>
        <div class="result-box" id="resultBox">
            <h3 style="color: #23a95c; margin: 0 0 10px 0;">✓ Registro Criado!</h3>
            <div class="qr-display" id="qrContainer"></div>
            <a id="linkPolicial" class="link-output" target="_blank" href="#">Carregando...</a>
        </div>
    </div>
    <div class="phone-wrapper">
        <div class="vio-header-app">
            <p class="title-gov">SENATRAN · GOVERNO FEDERAL</p>
            <p class="sub-gov">Ministério dos Transportes</p>
        </div>
        <div class="banner-autentico"><div class="check-badge">✓</div><h2 class="txt-status">DOCUMENTO AUTÊNTICO</h2></div>
        <div class="label-grupo">Veículo</div>
        <div class="container-dados">
            <div class="linha-dados"><span class="lbl-campo">Placa</span><span class="val-campo" id="view_placa">-</span></div>
            <div class="linha-dados"><span class="lbl-campo">RENAVAM</span><span class="val-campo" id="view_renavam">-</span></div>
            <div class="linha-dados"><span class="lbl-campo">Chassi</span><span class="val-campo" id="view_chassi">-</span></div>
            <div class="linha-dados"><span class="lbl-campo">Marca / Modelo</span><span class="val-campo" id="view_modelo">-</span></div>
            <div class="linha-dados"><span class="lbl-campo">Ano</span><span class="val-campo" id="view_ano">-</span></div>
        </div>
        <div class="label-grupo">Proprietário Atual</div>
        <div class="container-dados">
            <div class="linha-dados"><span class="lbl-campo">Nome / Nome Empresarial</span><span class="val-campo" id="view_nome" style="text-align: left; max-width: 200px; word-break: break-word;">-</span></div>
        </div>
        <div class="rodape-fiscalizacao">
            <p class="orgao">Emitido por: SERPRO / SENATRAN</p>
            <p class="data-hora">Data/Hora da consulta: <span style="font-weight: 700;">{{ data_hora }}</span></p>
            <p class="aviso-legal">Este documento foi consultado diretamente na base de dados nacional. A autenticidade só é garantida através do aplicativo Vio.</p>
        </div>
    </div>
</div>
<script>
    async function emitirRegistro() {
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
            document.getElementById('view_nome').innerText = payload.nome.toUpperCase();
            document.getElementById('view_placa').innerText = payload.placa.toUpperCase();
            document.getElementById('view_renavam').innerText = payload.renavam;
            let chassi = document.getElementById('chassi').value.trim();
            let ultimos = chassi.substring(chassi.length - 4);
            document.getElementById('view_chassi').innerText = "***" + ultimos.toUpperCase();
            document.getElementById('view_modelo').innerText = payload.modelo.toUpperCase();
            document.getElementById('view_ano').innerText = payload.ano;
            document.getElementById('qrContainer').innerHTML = `<img src="https://qrserver.com{encodeURIComponent(data.url_validacao)}" alt="QR Vio">`;
            document.getElementById('linkPolicial').href = data.url_validacao;
            document.getElementById('linkPolicial').innerText = data.url_validacao;
            document.getElementById('resultBox').style.display = 'block';
        } else { alert('Erro ao emitir dados.'); }
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
    <title>Vio - Validação de Documentos Digitais</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f4f6f8; margin: 0; padding: 0; display: flex; justify-content: center; }
        .vio-wrapper { width: 100%; max-width: 440px; background: #ffffff; min-height: 100vh; box-sizing: border-box; padding: 16px 20px; display: flex; flex-direction: column; }
        .vio-header-app { text-align: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #e1e8ed; }
        .vio-header-app .title-gov { font-size: 11px; font-weight: 700; color: #004b82; letter-spacing: 0.8px; margin: 0; text-transform: uppercase; }
        .vio-header-app .sub-gov { font-size: 13px; font-weight: 600; color: #5c6873; margin: 3px 0 0 0; }
        .banner-autentico { background-color: #eaf7ed; border: 1px solid #23a95c; border-radius: 12px; padding: 14px; text-align: center; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .banner-autentico .check-badge { display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; background: #23a95c; color: white; border-radius: 50%; font-size: 13px; font-weight: bold; }
        .banner-autentico .txt-status { font-size: 15px; font-weight: 800; color: #23a95c; margin: 0; letter-spacing: 0.3px; }
        .label-grupo { font-size: 11px; font-weight: 700; color: #657786; text-transform: uppercase; margin: 14px 0 6px 4px; letter-spacing: 0.5px; }
        .container-dados { background: #f8fafc; border: 1px solid #e6ecf0; border-radius: 12px; padding: 4px 14px; margin-bottom: 12px; }
        .linha-dados { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #e6ecf0; }
        .linha-dados:last-child { border-bottom: none; }
        .lbl-campo { font-size: 13px; color: #657786; font-weight: 500; }
        .val-campo { font-size: 13px; color: #14171a; font-weight: 700; text-align: right; }
        .rodape-fiscalizacao { text-align: center; margin-top: auto; padding-top: 30px; }
        .rodape-fiscalizacao .orgao { font-size: 11px; font-weight: 700; color: #657786; margin: 0; }
        .rodape-fiscalizacao .data-hora { font-size: 11px; font-weight: 500; color: #14171a; margin: 3px 0 0 0; }
        .rodape-fiscalizacao .aviso-legal { font-size: 10px; color: #a4b0be; line-height: 14px; margin-top: 15px; padding: 0 5px; }
    </style>
</head>
<body>
<div class="vio-wrapper">
    <div class="vio-header-app">
        <p class="title-gov">SENATRAN · GOVERNO FEDERAL</p>
        <p class="sub-gov">Ministério dos Transportes</p>
    </div>
    <div class="banner-autentico"><div class="check-badge">✓</div><h2 class="txt-status">DOCUMENTO AUTÊNTICO</h2></div>
    <div class="label-grupo">Veículo</div>
    <div class="container-dados">
        <div class="linha-dados"><span class="lbl-campo">Placa</span><span class="val-campo">{{ dados.placa }}</span></div>
        <div class="linha-dados"><span class="lbl-campo">RENAVAM</span><span class="val-campo">{{ dados.renavam }}</span></div>
        <div class="linha-dados"><span class="lbl-campo">Chassi</span><span class="val-campo">{{ dados.chassi_mascarado }}</span></div>
        <div class="linha-dados"><span class="lbl-campo">Marca / Modelo</span><span class="val-campo">{{ dados.modelo }}</span></div>
        <div class="linha-dados"><span class="lbl-campo">Ano</span><span class="val-campo">{{ dados.ano }}</span></div>
    </div>
    <div class="label-grupo">Proprietário Atual</div>
    <div class="container-dados">
        <div class="linha-dados"><span class="lbl-campo">Nome / Nome Empresarial</span><span class="val-campo" style="text-align: left; max-width: 220px; word-break: break-word;">{{ dados.nome }}</span></div>
    </div>
    <div class="rodape-fiscalizacao">
        <p class="orgao">Emitido por: SERPRO / SENATRAN</p>
        <p class="data-hora">Data/Hora da consulta: <span style="font-weight: 700;">{{ dados.data_hora }}</span></p>
        <p class="aviso-legal">Este documento foi consultado diretamente na base de dados nacional. A autenticidade só é garantida através do aplicativo Vio.</p>
    </div>
</div>
</body>
</html>
"""

@app.route('/')
@app.route('/admin')
def admin():
    fuso_brasilia = timezone(timedelta(hours=-3))
    data_hora_atual = datetime.now(fuso_brasilia).strftime("%d/%m/%Y %H:%M:%S")
    return render_template_string(HTML_INTERFACE + HTML_DADOS, data_hora=data_hora_atual)

@app.route('/api/criar', methods=['POST'])
def api_criar():
    dados = request.json
    if not dados: return jsonify({"error": "Dados inválidos"}), 400
    id_consulta = str(uuid.uuid4())[:8]
    chassi_original = dados.get('chassi', '').strip()
    ultimos_digitos = chassi_original[-4:] if len(chassi_original) >= 4 else chassi_original
    chassi_mascarado = f"***{ultimos_digitos.upper()}"
    fuso_brasilia = timezone(timedelta(hours=-3))
    data_hora_atual = datetime.now(fuso_brasilia).strftime("%d/%m/%Y %H:%M:%S")
    BANCO_DADOS[id_consulta] = {
        "nome": dados.get('nome', '').upper(),
        "placa": dados.get('placa', '').upper(),
        "renavam": dados.get('renavam', ''),
        "chassi_mascarado": chassi_mascarado,
        "modelo": dados.get('modelo', '').upper(),
        "ano": dados.get('ano', ''),
        "data_hora": data_hora_atual
    }
    url_completa = request.host_url.rstrip('/') + url_for('validar_policial', id_consulta=id_consulta)
    return jsonify({"id": id_consulta, "url_validacao": url_completa})

@app.route('/validar/<id_consulta>')
def validar_policial(id_consulta):
    registro = BANCO_DADOS.get(id_consulta)
    if not registro: return "<h3>Erro 404: Registro não encontrado.</h3>", 404
    return render_template_string(HTML_POLICIAL, dados=registro)

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
