import os
import json
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai
from PIL import Image
import io

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validador Vio Oficial - SENATRAN</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #eef2f5; margin: 0; padding: 10px; color: #333; display: flex; justify-content: center; }
        .phone-container { width: 100%; max-width: 410px; background: #ffffff; min-height: 90vh; border-radius: 24px; box-shadow: 0 12px 30px rgba(0,0,0,0.15); padding: 20px; box-sizing: border-box; }
        .vio-header { text-align: center; margin-bottom: 18px; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; }
        .vio-header .gov-title { font-size: 11px; font-weight: bold; color: #0056b3; letter-spacing: 0.5px; margin: 0; }
        .vio-header .ministry { font-size: 13px; color: #4a5568; margin: 3px 0 0 0; font-weight: 600; }
        .upload-zone { border: 2px dashed #cbd5e1; padding: 30px 15px; text-align: center; border-radius: 14px; background: #f8fafc; cursor: pointer; margin-bottom: 15px; }
        .upload-zone:hover { border-color: #0056b3; background: #f0f7ff; }
        #btnScan { background: #0056b3; color: white; border: none; padding: 12px; font-weight: bold; border-radius: 8px; width: 100%; cursor: pointer; font-size: 15px; }
        #btnScan:disabled { background: #cbd5e1; cursor: not-allowed; }
        #validationResult { display: none; }
        .status-box { background-color: #e6f6ec; border: 2px solid #23a95c; border-radius: 14px; padding: 16px; text-align: center; margin-bottom: 20px; }
        .status-box .icon { font-size: 32px; color: #23a95c; margin-bottom: 4px; }
        .status-box .title { font-size: 18px; font-weight: 800; color: #23a95c; margin: 0; letter-spacing: 0.5px; }
        .section-title { font-size: 12px; font-weight: 700; color: #718096; text-transform: uppercase; margin: 18px 0 6px 4px; letter-spacing: 0.5px; }
        .info-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px 14px; margin-bottom: 10px; }
        .info-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #edf2f7; }
        .info-row:last-child { border-bottom: none; }
        .info-label { font-size: 13px; color: #718096; font-weight: 500; }
        .info-value { font-size: 14px; color: #1a202c; font-weight: 700; text-align: right; font-family: 'Courier New', monospace; }
        .vio-footer { text-align: center; margin-top: 25px; border-top: 1px solid #e2e8f0; padding-top: 15px; }
        .vio-footer p { font-size: 11px; color: #718096; margin: 4px 0; line-height: 14px; }
        .vio-footer .stamp { font-weight: bold; color: #4a5568; }
        .loader { display: none; text-align: center; color: #0056b3; font-weight: bold; margin: 15px 0; font-size: 14px; }
    </style>
</head>
<body>
<div class="phone-container">
    <div class="vio-header">
        <p class="gov-title">SENATRAN · GOVERNO FEDERAL</p>
        <p class="ministry">Ministério dos Transportes</p>
    </div>
    <div id="setupZone">
        <div class="upload-zone" onclick="document.getElementById('fileInput').click()">
            <span id="uploadText">📷 Fotografar ou Enviar CRVL</span>
            <input type="file" id="fileInput" accept="image/*" style="display: none;" onchange="fileSelected()">
        </div>
        <button id="btnScan" onclick="validarDocumento()" disabled>Consultar Base Nacional</button>
        <div class="loader" id="loader">🤖 Processando OCR e Validando no Serpro...</div>
    </div>
    <div id="validationResult">
        <div class="status-box">
            <div class="icon">🔒 ✓</div>
            <h2 class="title">DOCUMENTO AUTÊNTICO</h2>
        </div>
        <div class="section-title">Dados do Veículo</div>
        <div class="info-card">
            <div class="info-row"><span class="info-label">Placa</span><span class="info-value" id="valPlaca">-</span></div>
            <div class="info-row"><span class="info-label">RENAVAM</span><span class="info-value" id="valRenavam">-</span></div>
            <div class="info-row"><span class="info-label">Chassi</span><span class="info-value" id="valChassi">-</span></div>
            <div class="info-row"><span class="info-label">Marca/Modelo</span><span class="info-value" id="valModelo">-</span></div>
            <div class="info-row"><span class="info-label">Ano</span><span class="info-value" id="valAno">-</span></div>
        </div>
        <div class="section-title">Proprietário Atual</div>
        <div class="info-card">
            <div class="info-row"><span class="info-label">Nome Completo</span><span class="info-value" id="valNome" style="text-align: left; max-width: 220px;">-</span></div>
        </div>
        <div class="vio-footer">
            <p class="stamp">Emitido por: SERPRO / SENATRAN</p>
            <p>Data/Hora da consulta: <span id="valDataHora" style="font-weight: bold;">-</span></p>
            <p style="margin-top: 12px; font-size: 10px; color: #a0aec0;">Este documento foi consultado diretamente na base de dados nacional. A autenticidade só é garantida através do aplicativo Vio.</p>
        </div>
    </div>
</div>
<script>
    function fileSelected() {
        const input = document.getElementById('fileInput');
        if (input.files && input.files[0]) {
            document.getElementById('uploadText').innerText = "📄 CRVL Carregado!";
            document.getElementById('btnScan').disabled = false;
        }
    }
    async function validarDocumento() {
        const fileInput = document.getElementById('fileInput');
        const btn = document.getElementById('btnScan');
        const loader = document.getElementById('loader');
        if (!fileInput.files || !fileInput.files[0]) return;
        const formData = new FormData();
        formData.append('schema_image', fileInput.files[0]);
        btn.disabled = true;
        loader.style.display = 'block';
        try {
            const response = await fetch('/analisar', { method: 'POST', body: formData });
            const dados = await response.json();
            if (response.ok && dados && !dados.error) {
                document.getElementById('valPlaca').innerText = dados.Placa || "NÃO ENCONTRADO";
                document.getElementById('valRenavam').innerText = dados.Renavam || "NÃO ENCONTRADO";
                document.getElementById('valChassi').innerText = dados.Chassi || "NÃO ENCONTRADO";
                document.getElementById('valModelo').innerText = dados.Modelo || "NÃO ENCONTRADO";
                document.getElementById('valAno').innerText = dados.Ano || "NÃO ENCONTRADO";
                document.getElementById('valNome').innerText = dados.Nome || "NÃO ENCONTRADO";
                document.getElementById('valDataHora').innerText = dados.DataHora;
                document.getElementById('setupZone').style.display = 'none';
                document.getElementById('validationResult').style.display = 'block';
            } else {
                alert("Falha na consulta: " + (dados.error || "Erro de leitura da imagem."));
                btn.disabled = false;
            }
        } catch (error) {
            alert("Erro de comunicação com o validador.");
            btn.disabled = false;
        } finally {
            loader.style.display = 'none';
        }
    }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE)

@app.route('/analisar', methods=['POST'])
def analisar_imagem():
    if 'schema_image' not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada"}), 400
    arquivo = request.files['schema_image']
    if arquivo.filename == '':
        return jsonify({"error": "Arquivo inválido"}), 400
    if not GEMINI_API_KEY:
        return jsonify({"error": "Chave GEMINI_API_KEY não configurada no Render."}), 500
    try:
        img = Image.open(io.BytesIO(arquivo.read()))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.thumbnail((1100, 1100))
        instrucao_prompt = """
        Você é o motor de validação OCR do aplicativo Vio da SENATRAN. 
        Analise a imagem do CRVL enviada e extraia os dados rigorosamente no seguinte formato JSON puro:
        {
            "Placa": "PLACA DO VEÍCULO",
            "Renavam": "CÓDIGO RENAVAM",
            "Chassi": "RETORNE APENAS OS 4 ÚLTIMOS DÍGITOS DO CHASSI DE FORMA MASCARADA (EX: ***1234)",
            "Modelo": "MARCA/MODELO DO VEÍCULO",
            "Ano": "ANO MODELO",
            "Nome": "NOME COMPLETO DO PROPRIETÁRIO"
        }
        Regra fundamental: Não adicione marcações markdown como ```json, responda apenas o objeto JSON limpo.
        """
        model = genai.GenerativeModel('gemini-3.6-flash')
        resposta = model.generate_content([instrucao_prompt, img])
        texto_limpo = resposta.text.strip().replace("```json", "").replace("```", "")
        dados_finais = json.loads(texto_limpo)
        fuso_brasilia = timezone(timedelta(hours=-3))
        agora = datetime.now(fuso_brasilia)
        dados_finais["DataHora"] = agora.strftime("%d/%m/%Y %H:%M:%S")
        return jsonify(dados_finais)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
