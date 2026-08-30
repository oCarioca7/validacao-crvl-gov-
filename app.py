import os
from flask import Flask, render_template_string

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

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gerador CRVL Automático</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }
        .header-app { text-align: center; margin-bottom: 30px; background: #2c3e50; color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .header-app h1 { margin: 0; font-size: 24px; letter-spacing: 1px; }
        .container { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .panel { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: fit-content; }
        h2 { margin-top: 0; color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; font-size: 18px; }
        .upload-area { border: 3px dashed #bdc3c7; border-radius: 8px; padding: 20px; text-align: center; cursor: pointer; background: #fafafa; margin-bottom: 15px; }
        .upload-area:hover { border-color: #2ecc71; background: #f0fdf4; }
        .form-group { margin-bottom: 12px; }
        label { display: block; font-weight: 600; margin-bottom: 4px; color: #34495e; font-size: 13px; }
        input[type="text"] { width: 100%; padding: 10px 12px; border: 1px solid #ccd1d9; border-radius: 6px; box-sizing: border-box; background-color: #fdfdfd; font-size: 14px; color: #444; }
        .btn { color: white; border: none; padding: 14px 20px; font-size: 15px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; transition: 0.2s; margin-top: 10px; display: block; text-align: center; text-decoration: none; box-sizing: border-box; }
        .btn-success { background: #2ecc71; }
        .btn-success:hover { background: #27ae60; }
        .canvas-container { width: 100%; overflow: auto; border: 1px solid #ccc; background: #eee; border-radius: 8px; max-height: 750px; }
        canvas { display: block; margin: 0 auto; }
        .helper-text { font-size: 12px; color: #7f8c8d; margin-top: 10px; line-height: 16px; }
    </style>
</head>
<body>

<div class="header-app">
    <h1>SISTEMA DE PREENCHIMENTO AUTOMÁTICO CRVL</h1>
    <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">Os dados digitados vão sozinhos para as posições corretas do formulário</p>
</div>

<div class="container">
    <!-- ESQUERDA: FORMULÁRIO -->
    <div class="panel">
        <h2>1. Painel de Dados</h2>
        
        <div class="upload-area" onclick="document.getElementById('fileInput').click()">
            <span id="uploadText">Carregue o seu Modelo de CRVL em Branco</span>
            <input type="file" id="fileInput" accept="image/*" style="display: none;" onchange="carregarImagemBase(this)">
        </div>

        <form id="adminForm">
            {% for campo in campos %}
            <div class="form-group">
                <label for="{{ campo }}">{{ campo }}</label>
                <input type="text" id="{{ campo }}" class="input-doc" data-campo="{{ campo }}" placeholder="Apenas digite aqui..." oninput="atualizarDocumento()">
            </div>
            {% endfor %}
        </form>
        
        <button class="btn btn-success" onclick="baixarImagemFinal()">Baixar Documento Pronto</button>
        <div class="helper-text">
            <b>🚀 Modo 100% Automático Ativo:</b><br>
            Você só precisa digitar as informações na esquerda. O sistema já sabe onde fica a Placa, o Renavam e o Nome e carimba tudo no local exato do papel sozinho.
        </div>
    </div>

    <!-- DIREITA: DOCUMENTO AUTOMÁTICO -->
    <div class="panel">
        <h2>2. Visualização do Documento (Preenchimento Automático)</h2>
        <div class="canvas-container">
            <canvas id="documentCanvas"></canvas>
        </div>
    </div>
</div>

<script>
    let imagemBase = new Image();
    const canvas = document.getElementById('documentCanvas');
    const ctx = canvas.getContext('2d');
    
    // ====================================================================
    # MAPEAMENTO AUTOMÁTICO DE COORDENADAS (AJUSTADO PARA O MODELO PADRÃO)
    // ====================================================================
    // Aqui estão salvos os locais exatos (X e Y) de cada caixinha do documento.
    // O texto vai pular para cá sozinho assim que você digitar.
    const posicoesAutomaticas = {
        "Código Renavam": { x: 70, y: 375 },
        "Placa": { x: 70, y: 415 },
        "Chassi": { x: 345, y: 730 },
        "Ano Fabricação": { x: 70, y: 450 },
        "Ano Modelo": { x: 195, y: 450 },
        "Combustível": { x: 200, y: 775 },
        "Marca / Modelo": { x: 70, y: 615 },
        "Nome / Nome Empresarial (Proprietário)": { x: 620, y: 515 },
        "CPF / CNPJ": { x: 785, y: 550 },
        "Número do CRV": { x: 70, y: 490 },
        "Código de Segurança do CLA": { x: 70, y: 575 },
        "Categoria": { x: 620, y: 335 },
        "Capacidade / Lotação": { x: 875, y: 415 }
    };

    function carregarImagemBase(input) {
        if (input.files && input.files) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagemBase.src = e.target.result;
                imagemBase.onload = function() {
                    // Força o tamanho padrão do documento impresso para bater com as coordenadas
                    canvas.width = 1190;
                    canvas.height = 1684;
                    document.getElementById('uploadText').innerText = "Modelo de CRVL Pronto e Sincronizado!";
                    atualizarDocumento();
                }
            }
            reader.readAsDataURL(input.files);
        }
    }

    function atualizarDocumento() {
        if (!imagemBase.src) return;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(imagemBase, 0, 0, canvas.width, canvas.height);
        
        // Estilo da fonte oficial para o preenchimento (Fonte escura estilo impressora)
        ctx.font = "bold 20px Courier New";
        ctx.fillStyle = "#111111";
        
        document.querySelectorAll('.input-doc').forEach(input => {
            const nomeCampo = input.getAttribute('data-campo');
            const valorTexto = input.value.toUpperCase(); // Força ficar em Letra Maiúscula padrão Detran
            const posicao = posicoesAutomaticas[nomeCampo];
            
            if (valorTexto && posicao) {
                ctx.fillText(valorTexto, posicao.x, posicao.y);
            }
        });
    }

    function baixarImagemFinal() {
        if (!imagemBase.src) {
            alert("Por favor, carregue a imagem do documento primeiro!");
            return;
        }
        const link = document.createElement('a');
        link.download = 'CRVL_Gerado_Automatico.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
    }
</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE, campos=CAMPOS_ADMIN)

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
