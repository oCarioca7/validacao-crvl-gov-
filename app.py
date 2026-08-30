import os
import json
from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai
from PIL import Image
import io

app = Flask(__name__)

# ==========================================
# PAINEL DE CONTROLE / ADMINISTRAÇÃO (CRVL)
# ==========================================
CAMPOS_ADMIN = [
    "Código Renavam",
    "Placa",
    "Chassi",
    "Ano Fabricação",
    "Ano Modelo",
    "Combustível",
    "Marca / Modelo",
    "Nome / Nome Empresarial (Proprietário)",
    "CPF / CNPJ",
    "Número do CRV",
    "Código de Segurança do CLA",
    "Categoria",
    "Capacidade / Lotação"
]

# Configuração de Segurança da API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "SUA_CHAVE_LOCAL_SE_NAO_USAR_RENDER")
if GEMINI_API_KEY and GEMINI_API_KEY != "SUA_CHAVE_LOCAL_SE_NAO_USAR_RENDER":
    genai.configure(api_key=GEMINI_API_KEY)

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scanner CRVL Oficial - IA</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }
        .header-app { text-align: center; margin-bottom: 30px; background: #2c3e50; color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .header-app h1 { margin: 0; font-size: 24px; letter-spacing: 1px; }
        .container { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .panel { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: fit-content; }
        h2 { margin-top: 0; color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; font-size: 18px; }
        .upload-area { border: 3px dashed #bdc3c7; border-radius: 8px; padding: 40px 20px; text-align: center; cursor: pointer; background: #fafafa; transition: 0.3s; }
        .upload-area:hover { border-color: #2ecc71; background: #f0fdf4; }
        #preview { max-width: 100%; max-height: 320px; margin-top: 15px; display: none; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 12px; }
        label { display: block; font-weight: 600; margin-bottom: 4px; color: #34495e; font-size: 13px; }
        input[type="text"] { width: 100%; padding: 10px 12px; border: 1px solid #ccd1d9; border-radius: 6px; box-sizing: border-box; background-color: #fdfdfd; font-size: 14px; color: #444; }
        .btn { color: white; border: none; padding: 14px 20px; font-size: 15px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; transition: 0.2s; margin-top: 10px; display: block; text-align: center; text-decoration: none; box-sizing: border-box; }
        .btn-success { background: #2ecc71; }
        .btn-success:hover { background: #27ae60; }
        .btn-pdf { background: #e74c3c; display: none; }
        .btn-pdf:hover { background: #c0392b; }
        button:disabled { background: #bdc3c7 !important; cursor: not-allowed; }
        .loading { display: none; color: #2980b9; font-weight: bold; text-align: center; margin-top: 15px; font-size: 14px; }
        
        /* Estilos de Impressão para o PDF limpo */
        @media print {
            body { background: white; color: black; padding: 0; }
            .header-app { background: #1a365d !important; color: white !important; border-radius: 0; padding: 15px; -webkit-print-color-adjust: exact; }
            .container { display: block; }
            .panel:nth-child(1), #btnPdf { display: none !important; }
            .panel:nth-child(2) { box-shadow: none; padding: 0; width: 100%; }
            h2 { color: #1a365d; border-bottom: 2px solid #1a365d; font-size: 20px; }
            .form-group { margin-bottom: 15px; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; }
            input[type="text"] { border: none; background: transparent; padding: 5px 0; font-size: 16px; font-weight: bold; color: black; }
            label { font-size: 12px; color: #4a5568; }
        }
    </style>
</head>
<body>

<div class="header-app">
    <h1>REPÚBLICA FEDERATIVA DO BRASIL</h1>
    <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">MINISTÉRIO DOS TRANSPORTES - SENATRAN</p>
</div>

<div class="container">
    <!-- ESQUERDA: ENTRADA -->
    <div class="panel">
        <h2>1. Upload do CRVL Digital</h2>
        <div class="upload-area" onclick="document.getElementById('fileInput').click()">
            <span id="uploadText">Clique aqui ou arraste o documento veicular</span>
            <input type="file" id="fileInput" accept="image/*" style="display: none;" onchange="previewImage(this)">
            <center><img id="preview" alt="Documento carregado"></center>
        </div>
        <button id="btnProcessar" class="btn btn-success" onclick="processarImagem()" disabled>Processar e Preencher Texto</button>
        <div class="loading" id="loadingText">🤖 Extraindo dados estruturados do CRVL... Por favor, aguarde.</div>
    </div>

    <!-- DIREITA: RESULTADOS -->
    <div class="panel">
        <h2>2. Dados Extraídos do Veículo</h2>
        <form id="adminForm">
            {% for campo in campos %}
            <div class="form-group">
                <label for="{{ campo }}">{{ campo }}</label>
                <input type="text" id="{{ campo }}" name="{{ campo }}" placeholder="Aguardando processamento...">
            </div>
            {% endfor %}
            <button type="button" id="btnPdf" class="btn btn-pdf" onclick="window.print()">Gerar e Salvar Documento PDF</button>
        </form>
    </div>
</div>

<script>
    function previewImage(input) {
        const preview = document.getElementById('preview');
        const uploadText = document.getElementById('uploadText');
        const btn = document.getElementById('btnProcessar');
        const btnPdf = document.getElementById('btnPdf');
        
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
                uploadText.style.display = 'none';
                btn.disabled = false;
                btnPdf.style.display = 'none';
                
                const inputs = document.querySelectorAll('#adminForm input[type="text"]');
                inputs.forEach(inp => inp.value = '');
            }
            reader.readAsDataURL(input.files[0]);
        }
    }

    async function processarImagem() {
        const fileInput = document.getElementById('fileInput');
        const btn = document.getElementById('btnProcessar');
        const btnPdf = document.getElementById('btnPdf');
        const loading = document.getElementById('loadingText');
        
        if (!fileInput.files || !fileInput.files[0]) return;

        const formData = new FormData();
        formData.append('schema_image', fileInput.files[0]);

        btn.disabled = true;
        loading.style.display = 'block';

        try {
            const response = await fetch('/analisar', {
                method: 'POST',
                body: formData
            });
            
            const dados = await response.json();
            
            if (response.ok && dados && !dados.error) {
                for (const [campo, valor] of Object.entries(dados)) {
                    const inputElement = document.getElementById(campo);
                    if (inputElement) {
                        inputElement.value = valor;
                    }
                }
                btnPdf.style.display = 'block';
            } else {
                alert("Falha no processamento: " + (dados.error || "Erro na resposta da IA."));
            }
        } catch (error) {
            alert("Processamento concluído. Verifique as caixas na tela.");
        } finally {
            btn.disabled = false;
            loading.style.display = 'none';
        }
    }
</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE, campos=CAMPOS_ADMIN)

@app.route('/analisar', methods=['POST'])
def analisar_imagem():
    if 'schema_image' not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada"}), 400
        
    arquivo = request.files['schema_image']
    if arquivo.filename == '':
        return jsonify({"error": "Arquivo inválido"}), 400

    if not GEMINI_API_KEY or GEMINI_API_KEY == "SUA_CHAVE_LOCAL_SE_NAO_USAR_RENDER":
        return jsonify({"error": "API Key do Gemini não configurada."}), 500

    try:
        img = Image.open(io.BytesIO(arquivo.read()))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.thumbnail((1200, 1200))
        
        estrutura_exemplo = {campo: "texto extraído" for campo in CAMPOS_ADMIN}
        
        instrucao_prompt = f"""
        Você é um sistema OCR especialista em documentos automotivos brasileiros.
        Analise a imagem do CRVL enviado.
        Extraia as informações textuais correspondentes e monte estritamente uma estrutura JSON pura:
        {json.dumps(estrutura_exemplo, ensure_ascii=False)}
        
        Regras cruciais:
        1. Responda APENAS o objeto JSON, sem blocos de código markdown ou explicações.
        2. Chaves idênticas às solicitadas.
        3. Caso não visualize o dado, atribua string vazia "".
        """

        model = genai.GenerativeModel('gemini-3.6-flash')
        resposta = model.generate_content([instrucao_prompt, img])
        
        texto_limpo = resposta.text.strip().replace("```json", "").replace("```", "")
        dados_finais = json.loads(texto_limpo)
        
        return jsonify(dados_finais)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":

porta = int(os.environ.get("PORT", 5000))app.run(host="0.0.0.0", port=porta)
