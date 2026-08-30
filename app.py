import os
import uuid
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify, render_template_string, url_for

app = Flask(__name__)

# Banco de dados temporário em memória para salvar as validações geradas
BANCO_DADOS = {}

HTML_ADMIN = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Admin - Emissor Vio Oficial</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 20px; }
        .admin-container { max-width: 700px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        h2 { margin-top: 0; color: #004b82; border-bottom: 2px solid #edf2f7; padding-bottom: 10px; text-transform: uppercase; font-size: 18px; }
        .grid-inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .form-group { margin-bottom: 12px; }
        .full-width { grid-column: span 2; }
        label { display: block; font-weight: 600; margin-bottom: 4px; font-size: 12px; color: #4a5568; }
        input { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        .btn-emissao { background: #004b82; color: white; border: none; padding: 14px; font-size: 16px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 20px; text-transform: uppercase; }
        .btn-emissao:hover { background: #00335a; }
        .result-box { display: none; margin-top: 25px; padding: 25px; background: #f8fafc; border: 2px dashed #1db954; border-radius: 8px; text-align: center; }
        .qr-display { margin: 20px 0; display: inline-block; padding: 15px; background: white; border: 1px solid #e2e8f0; border-radius: 8px; }
        .link-output { word-break: break-all; font-weight: bold; color: #004b82; font-size: 15px; text-decoration: none; display: block; margin-top: 10px; }
    </style>
</head>
<body>
<div class="admin-container">
    <h2>Painel de Controle - Emissão Vio Original</h2>
    <form id="formAdmin">
        <div class="grid-inputs">
            <div class="form-group full-width"><label>Nome Completo do Proprietário</label><input type="text" id="nome" required></div>
            <div class="form-group"><label>CPF / CNPJ</label><input type="text" id="doc_proprietario" required></div>
            <div class="form-group"><label>Placa</label><input type="text" id="placa" required></div>
            <div class="form-group"><label>RENAVAM</label><input type="text" id="renavam" required></div>
            <div class="form-group"><label>Chassi Completo</label><input type="text" id="chassi" required></div>
            <div class="form-group"><label>Marca / Modelo</label><input type="text" id="modelo" required></div>
            <div class="form-group"><label>Ano Fab / Ano Mod</label><input type="text" id="ano" placeholder="Ex: 2023/2024" required></div>
            <div class="form-group"><label>Município / UF</label><input type="text" id="municipio" placeholder="Ex: RIO DE JANEIRO / RJ" required></div>
            <div class="form-group"><label>Combustível</label><input type="text" id="combustivel" placeholder="Ex: ALCOOL/GASOLINA" required></div>
            <div class="form-group"><label>Cor Predominante</label><input type="text" id="cor" placeholder="Ex: PRETA" required></div>
            <div class="form-group"><label>Espécie / Tipo</label><input type="text" id="especie" placeholder="Ex: PASSAGEIRO / AUTOMOVEL" required></div>
            <div class="form-group"><label>Categoria</label><input type="text" id="categoria" placeholder="Ex: PARTICULAR" required></div>
            <div class="form-group"><label>Capacidade / Lotação</label><input type="text" id="capacidade" placeholder="Ex: 5 PASSAGEIROS" required></div>
            <div class="form-group"><label>Código de Segurança do CLA</label><input type="text" id="cla_seguranca" required></div>
            <div class="form-group"><label>Número do CRV (Antigo DUT)</label><input type="text" id="crv_numero" required></div>
            <div class="form-group"><label>Restrições / Observações</label><input type="text" id="restricoes" placeholder="Ex: NADA CONSTA ou ALIENACAO FIDUCIARIA"></div>
            <div class="form-group"><label>Status IPVA / Licenciamento</label><input type="text" id="Status_licenca" placeholder="Ex: QUITADO / LICENCIADO 2026"></div>
        </div>
        <button type="button" class="btn-emissao" onclick="emitirRegistro()">Gerar Registro Nacional e QR Code</button>
    </form>
    <div class="result-box" id="resultBox">
        <h3 style="color: #1db954; margin: 0 0 10px 0;">✓ Registro Gerado no Banco de Dados!</h3>
        <p style="font-size: 14px; margin: 0;">Insira este QR Code no documento impresso do veículo:</p>
        <div class="qr-display" id="qrcode"></div>
        <p style="font-size: 14px; margin: 10px 0 0 0;">Link direto de fiscalização (Tela do Policial):</p>
        <a id="linkPolicial" class="link-output" target="_blank" href="#">Carregando link...</a>
    </div>
</div>
<!-- Importação da biblioteca oficial e segura de QR Code via JS do navegador -->
<script src="https://cloudflare.com"></script>
<script>
    async function emitirRegistro() {
        const payload = {
            nome: document.getElementById('nome').value,
            doc_proprietario: document.getElementById('doc_proprietario').value,
            placa: document.getElementById('placa').value,
            renavam: document.getElementById('renavam').value,
            chassi: document.getElementById('chassi').value,
            modelo: document.getElementById('modelo').value,
            ano: document.getElementById('ano').value,
            municipio: document.getElementById('municipio').value,
            combustivel: document.getElementById('combustivel').value,
            cor: document.getElementById('cor').value,
            especie: document.getElementById('especie').value,
            categoria: document.getElementById('categoria').value,
            capacidade: document.getElementById('capacidade').value,
            cla_seguranca: document.getElementById('cla_seguranca').value,
            crv_numero: document.getElementById('crv_numero').value,
            restricoes: document.getElementById('restricoes').value,
            Status_licenca: document.getElementById('Status_licenca').value
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
            document.getElementById('qrcode').innerHTML = "";
            new QRCode(document.getElementById("qrcode"), {
                text: data.url_validacao,
                width: 180,
                height: 180,
                colorDark : "#000000",
                colorLight : "#ffffff",
                correctLevel : QRCode.CorrectLevel.H
            });
            document.getElementById('resultBox').style.display = 'block';
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vio - Validação de Documentos Digitais</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f4f6f8; margin: 0; padding: 0; display: flex; justify-content: center; }
        .vio-wrapper { width: 100%; max-width: 440px; background: #ffffff; min-height: 100vh; box-sizing: border-box; padding: 16px 20px; display: flex; flex-direction: column; box-shadow: 0 0 10px rgba(0,0,0,0.02); }
        
        /* Topo Oficial App Vio */
        .vio-header-app { text-align: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #e1e8ed; }
        .vio-header-app .title-gov { font-size: 11px; font-weight: 700; color: #004b82; letter-spacing: 0.8px; margin: 0; text-transform: uppercase; }
        .vio-header-app .sub-gov { font-size: 13px; font-weight: 600; color: #5c6873; margin: 3px 0 0 0; }
        
        /* Banner Verde de Autenticidade Original do Vio */
        .banner-autentico { background-color: #eaf7ed; border: 1px solid #1db954; border-radius: 12px; padding: 14px; text-align: center; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .banner-autentico .check-badge { display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; background: #1db954; color: white; border-radius: 50%; font-size: 13px; font-weight: bold; }
        .banner-autentico .txt-status { font-size: 15px; font-weight: 800; color: #1db954; margin: 0; letter-spacing: 0.3px; }
        
        /* Grupos de Informações */
        .label-grupo { font-size: 11px; font-weight: 700; color: #657786; text-transform: uppercase; margin: 14px 0 6px 4px; letter-spacing: 0.5px; }
        .container-dados { background: #f8fafc; border: 1px solid #e6ecf0; border-radius: 12px; padding: 4px 14px; margin-bottom: 12px; }
        .linha-dados { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #e6ecf0; }
        .linha-dados:last-child { border-bottom: none; }
        .lbl-campo { font-size: 13px; color: #657786; font-weight: 500; }
        .val-campo { font-size: 13px; color: #14171a; font-weight: 700; text-align: right; }
        
        /* Rodapé de Segurança e Data/Hora */
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
    <div class="banner-autentico">
        <div class="check-badge">✓</div>
        <h2 class="txt-status">DOCUMENTO AUTÊNTICO</h2>
    </div>
    
    <div class="label-grupo">Veículo</div>
    <div class="container-dados">
        <div class="linha-dados"><span class="lbl-campo">Placa</span><span class="val-campo">{{ dados.placa }}</span></div>
        <div class="linha-dados"><span class="lbl-campo">RENAVAM</span><span class="val-campo">{{ dados.renavam }}</span></div>
        <div class="linha-dados"><span class="lbl-campo">Chassi</span><span class="val-campo">{{ dados.chassi_mascarado }}</span></div>
        <div class="linha-dados"><span class="lbl-campo">Marca / Modelo</span><span class="val-campo">{{ dados.modelo }}</span></div>
        <div class="linha-dados"><span class="lbl-campo">Ano Fab / Ano Mod</span><span class="val-campo">{{ dados.ano }}</span></div>
        <div class="linha-dados"><span class="lbl-campo">Município / UF</span><span class="val-campo">{{ dados.municipio }}</span></div>
    </div>

    <div class="label-grupo">Características do Veículo</div>
    <div class="container-dados">
        <div class="linha-dados"><span class="lbl-campo">Combustível</span><span class="val-campo">{{ dados.combustivel }}</span></div>
        <div class="linha-dados"><span class="lbl-campo">Cor Predominante</span><span class="val-campo">{{ dados.cor }}</span></div>
        <div class="linha-dados"><span class="lbl-campo">Espécie / Tipo</span><span class="val-campo">{{ dados.especie }}</span></div>
        <div class="linha-dados"><span class="lbl-campo">Categoria</span><span class="val-campo">{{ dados.categoria }}</span></div>
        <div class="linha-dados"><span class="lbl-campo">Capacidade / Lotação</span><span class="val-campo">{{ dados.capacidade }}</span></div>
    </div>

    <div class="label-grupo">Proprietário Atual</div>
    <div class="container-dados">
        <div class="linha-dados"><span class="lbl-campo">Nome / Nome Empresarial</span><span class="val-campo" style="text-align: left; max-width: 220px; word-break: break-word;">{{ dados.nome }}</span></div>
        <div class="linha-dados"><span class="lbl-campo">CPF / CNPJ</span><span class="val-campo">{{ dados.doc_proprietario }}</span></div>
    </div>

    <div class="label-grupo">Documento e Situação</div>
    <div class="container-dados">
        <div class="linha-dados"><span class="lbl-campo">Código de Segurança CLA</span><span class="val-campo">{{ dados.cla_seguranca }}</span></div>
        <div class="linha-dados"><span class="lbl-campo">Número do CRV</span><span class="val-campo">{{ dados.crv_numero }}</span></div>
        <div class="linha-dados"><span class="lbl-campo">Restrições / Observações</span><span class="val-campo">{{ dados.restricoes }}</span></div>
        <div class="linha-dados"><span class="lbl-campo">Situação IPVA / Licenciamento</span><span class="val-campo" style="color: #1db954;">{{ dados.Status_licenca }}</span></div>
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
        "doc_proprietario": dados.get('doc_proprietario', '').upper(),
        "placa": dados.get('placa', '').upper(),
        "renavam": dados.get('renavam', ''),
        "chassi_mascarado": chassi_mascarado,
        "modelo": dados.get('modelo', '').upper(),
        "ano": dados.get('ano', ''),
        "municipio": dados.get('municipio', '').upper(),
        "combustivel": dados.get('combustivel', '').upper(),
        "cor": dados.get('cor', '').upper(),
        "especie": dados.get('especie', '').upper(),
        "categoria": dados.get('categoria', '').upper(),
        "capacidade": dados.get('capacidade', '').upper(),
        "cla_seguranca": dados.get('cla_seguranca', ''),
        "crv_numero": dados.get('crv_numero', ''),
        "restricoes": dados.get('restricoes', '').upper() or "NADA CONSTA",
        "Status_licenca": dados.get('Status_licenca', '').upper() or "QUITADO / LICENCIADO",
        "data_hora": data_hora_atual
    }

    url_completa = request.host_url.rstrip('/') + url_for('validar_policial', id_consulta=id_consulta)
    return jsonify({"id": id_consulta, "url_validacao": url_completa})

@app.route('/validar/<id_consulta>')
def validar_policial(id_consulta):
    registro = BANCO_DADOS.get(id_consulta)
    if not registro:
        return "<h3>Erro 404: Registro não encontrado na base de dados nacional do SENATRAN.</h3>", 404
    return render_template_string(HTML_POLICIAL, dados=registro)

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
