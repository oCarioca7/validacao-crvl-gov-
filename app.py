import os
import json
from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai
from PIL import Image
import io

app = Flask(__name__)

# ==========================================
# PAINEL DE CONTROLE / ADMINISTRAÇÃO
# ==========================================
# Altere, adicione ou remova campos nesta lista.
# O sistema vai criar as caixas na tela e ler a foto automaticamente baseando-se nela.
CAMPOS_ADMIN = [
    "Nome Completo",
    "CPF",
    "Data de Nascimento",
    "Nome da Mãe",
    "Número do Documento (RG/CNH)"
]

# Configuração de Segurança da API Key (Lê o painel do Render ou local se testar no PC)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "SUA_CHAVE_LOCAL_SE_NAO_USAR_RENDER")
if GEMINI_API_KEY and GEMINI_API_KEY != "SUA_CHAVE_LOCAL_SE_NAO_USAR_RENDER":
    genai.configure(api_key=GEMINI_API_KEY)

# Página Web (Interface HTML + CSS + JavaScript tudo integrado)
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Leitor de Imagens Inteligente</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .panel { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        h2 { margin-top: 0; color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }
        .upload-area { border: 3px dashed #bdc3c7; border-radius: 8px; padding: 40px 20px; text-align: center; cursor: pointer; background: #fafafa; transition: 0.3s; }
        .upload-area:hover { border-color: #3498db; background: #f0f7fc; }
        #preview { max-width: 100%; max-height: 250px; margin-top: 15px; display: none; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        label { display: block; font-weight: 600; margin-bottom: 5px; color: #34495e; }
        input[type="text"] { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; background-color: #fdfdfd; font-size: 14px; }
        button { background: #2ecc71; color: white; border: none; padding: 12px 20px; font-size: 16px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; transition: 0.2s; margin-top: 15px; }
        button:hover { background: #27ae60; }
        button:disabled { background: #bdc3c7; cursor: not-allowed; }
        .loading { display: none; color: #3498db; font-weight: bold; text-align: center; margin-top: 10px; }
    </style>
</head>
<body>

<div style="text-align: center; margin-bottom: 30px;">
    <h1>Scanner de Documentos IA</h1>
    <p>Arraste uma imagem e o sistema preencherá os campos do Admin de forma automática.</p>
</div>

<div class="container">
    <!-- LADO ESQUERDO: ENVIO DA IMAGEM -->
    <div class="panel">
        <h2>1. Upload da Imagem</h2>
        <div class="upload-area" onclick="document.getElementById('fileInput').click()">
            <span id="uploadText">Clique ou Arraste a Imagem Aqui</span>
            <input type="file" id="fileInput" accept="image/*" style="display: none;" onchange="previewImage(this)">
            <center><img id="preview" alt="Miniatura do documento"></center>
        </div>
        <button id="btnProcessar" onclick="processarImagem()" disabled>Processar e Preencher Texto</button>
        <div class="loading" id="loadingText">🤖 Inteligência Artificial analisando a imagem... Aguarde.</div>
    </div>

    <!-- LADO DIREITO: CAMPOS DINÂMICOS DO ADMIN -->
    <div class="panel">
        <h2>2. Dados Extraídos (Painel Admin)</h2>
        <form id="adminForm">
            {% for campo in campos %}
            <div class="form-group">
                <label for="{{ campo }}">{{ campo }}</label>
                <input type="text" id="{{ campo }}" name="{{ campo }}" placeholder="Aguardando leitura da foto...">
            </div>
            {% endfor %}
        </form>
    </div>
</div>

<script>
    function previewImage(input) {
        const preview = document.getElementById('preview');
        const uploadText = document.getElementById('uploadText');
        const btn = document.getElementById('btnProcessar');
        
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
                uploadText.style.display = 'none';
                btn.disabled = false;
            }
            reader.readAsDataURL(input.files[0]);
        }
    }

    async function processarImagem() {
        const fileInput = document.getElementById('fileInput');
        const btn = document.getElementById('btnProcessar');
        const loading = document.getElementById('loadingText');
        
        if (!fileInput.files[0]) return;

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
            
            if (response.ok) {
                // Preenche os campos dinamicamente baseado no JSON de retorno
                for (const [campo, valor] of Object.entries(dados)) {
                    const inputElement = document.getElementById(campo);
                    if (inputElement) {
                        inputElement.value = valor;
                    }
                }
            } else {
                alert("Erro ao ler dados: " + (dados.error || "Erro desconhecido"));
            }
        } catch (error) {
            alert("Erro de comunicação com o servidor.");
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
    # Passa a lista CAMPOS_ADMIN para renderizar as caixas de texto corretas no HTML
    return render_template_string(HTML_INTERFACE, campos=CAMPOS_ADMIN)

@app.route('/analisar', methods=['POST'])
def analisar_imagem():
    if 'schema_image' not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada"}), 400
        
    arquivo = request.files['schema_image']
    if arquivo.filename == '':
        return jsonify({"error": "Arquivo inválido"}), 400

    if not GEMINI_API_KEY or GEMINI_API_KEY == "SUA_CHAVE_LOCAL_SE_NAO_USAR_RENDER":
        return jsonify({"error": "API Key do Gemini não foi configurada no servidor."}), 500

    try:
        # Abre a imagem recebida usando a biblioteca Pillow
        img = Image.open(io.BytesIO(arquivo.read()))
        
        # Monta a instrução baseada nos campos atuais definidos no CAMPOS_ADMIN
        estrutura_exemplo = {campo: "texto extraído" for campo in CAMPOS_ADMIN}
        
        instrucao_prompt = f"""
        Você é um assistente de extração de dados especializado. 
        Analise cuidadosamente a imagem do documento enviada.
        Extraia as informações textuais da imagem e organize exatamente no seguinte formato JSON:
        {json.dumps(estrutura_exemplo, ensure_ascii=False)}
        
        Regras fundamentais:
        1. Responda APENAS o objeto JSON puro, sem marcações de código markdown (como ```json) e sem texto explicativo.
        2. Mantenha as chaves do JSON idênticas aos nomes solicitados.
        3. Se não encontrar alguma informação na imagem, deixe o valor do campo vazio ("").
        """

        # Inicializa o modelo atual estável
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        resposta = model.generate_content([instrucao_prompt, img])


        
        # Limpa e converte o texto retornado para um dicionário JSON válido
        texto_limpo = resposta.text.strip().replace("```json", "").replace("```", "")
        dados_finais = json.loads(texto_limpo)
        
        return jsonify(dados_finais)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Garante que o Render consiga definir a porta de execução de forma automática
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
