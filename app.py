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
        .qr-code { margin: 20px 0; display: inline-block; padding: 10px; background: white; border: 1px solid #e2e8f0; border-radius: 6px; }
        .link-url { word-break: break-all; font-weight: bold; color: #0056b3; text-decoration: none; display: block; margin-top: 10px; }
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
        <div class="form-group"><label>Ano Fab / Ano Mod</label><input type="text" id="ano" placeholder="Ex: 2023/2024" required></div>
        <button type="button" class="btn" onclick="gerarAutenticacao()">Gerar Autenticação e QR Code</button>
    </form>
    <div class="result-box" id="resultBox">
        <h3 style="color: #23a95c; margin-top: 0;">✓ Registro Criado com Sucesso!</h3>
        <p style="font-size: 14px;">Abaixo está o QR Code para você embutir no seu CRVL:</p>
        <div class="qr-code" id="qrContainer"></div>
        <p style="font-size: 14px;">Link direto da tela de validação do policial:</p>
        <a id="linkPolicial" class="link-url" target="_blank" href="#">Carregando...</a>
    </div>
</div>
<script src="https://cloudflare.com"></script>
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
            document.getElementById('qrContainer').innerHTML = "";
            new QRCode(document.getElementById("qrContainer"), {
                text: data.url_validacao,
                width: 160,
                height: 160
            });
            document.getElementById('resultBox').style.display = 'block';
        } else {
            alert('Erro ao processar dados.');
        }
    }
</script>
</body>
</html>
"""
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
        .qr-code { margin: 20px 0; display: inline-block; padding: 10px; background: white; border: 1px solid #e2e8f0; border-radius: 6px; }
        .link-url { word-break: break-all; font-weight: bold; color: #0056b3; text-decoration: none; display: block; margin-top: 10px; }
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
        <div class="form-group"><label>Ano Fab / Ano Mod</label><input type="text" id="ano" placeholder="Ex: 2023/2024" required></div>
        <button type="button" class="btn" onclick="gerarAutenticacao()">Gerar Autenticação e QR Code</button>
    </form>
    <div class="result-box" id="resultBox">
        <h3 style="color: #23a95c; margin-top: 0;">✓ Registro Criado com Sucesso!</h3>
        <p style="font-size: 14px;">Abaixo está o QR Code para você embutir no seu CRVL:</p>
        <div class="qr-code" id="qrContainer"></div>
        <p style="font-size: 14px;">Link direto da tela de validação do policial:</p>
        <a id="linkPolicial" class="link-url" target="_blank" href="#">Carregando...</a>
    </div>
</div>
<script src="https://cloudflare.com"></script>
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
            document.getElementById('qrContainer').innerHTML = "";
            new QRCode(document.getElementById("qrContainer"), {
                text: data.url_validacao,
                width: 160,
                height: 160
            });
            document.getElementById('resultBox').style.display = 'block';
        } else {
            alert('Erro ao processar dados.');
        }
    }
</script>
</body>
</html>
"""
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
        .qr-code { margin: 20px 0; display: inline-block; padding: 10px; background: white; border: 1px solid #e2e8f0; border-radius: 6px; }
        .link-url { word-break: break-all; font-weight: bold; color: #0056b3; text-decoration: none; display: block; margin-top: 10px; }
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
        <div class="form-group"><label>Ano Fab / Ano Mod</label><input type="text" id="ano" placeholder="Ex: 2023/2024" required></div>
        <button type="button" class="btn" onclick="gerarAutenticacao()">Gerar Autenticação e QR Code</button>
    </form>
    <div class="result-box" id="resultBox">
        <h3 style="color: #23a95c; margin-top: 0;">✓ Registro Criado com Sucesso!</h3>
        <p style="font-size: 14px;">Abaixo está o QR Code para você embutir no seu CRVL:</p>
        <div class="qr-code" id="qrContainer"></div>
        <p style="font-size: 14px;">Link direto da tela de validação do policial:</p>
        <a id="linkPolicial" class="link-url" target="_blank" href="#">Carregando...</a>
    </div>
</div>
<script src="https://cloudflare.com"></script>
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
            document.getElementById('qrContainer').innerHTML = "";
            new QRCode(document.getElementById("qrContainer"), {
                text: data.url_validacao,
                width: 160,
                height: 160
            });
            document.getElementById('resultBox').style.display = 'block';
        } else {
            alert('Erro ao processar dados.');
        }
    }
</script>
</body>
</html>
"""
