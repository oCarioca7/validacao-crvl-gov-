import os
from flask import Flask, render_template_string

app = Flask(__name__)

# ==========================================
# PAINEL DE CONTROLE / ADMINISTRAÇÃO (CRVL)
# ==========================================
# Lista com todos os campos oficiais de um CRVL para você preencher.
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
    <title>Gerador e Preenchedor CRVL</title>
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
        .canvas-container { width: 100%; overflow: auto; border: 1px solid #ccc; background: #eee; border-radius: 8px; max-height: 600px; }
        canvas { display: block; margin: 0 auto; }
        .helper-text { font-size: 12px; color: #7f8c8d; margin-top: 10px; line-height: 16px; }
    </style>
</head>
<body>

<div class="header-app">
    <h1>SISTEMA DE PREENCHIMENTO CRVL</h1>
    <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">Gere imagens e documentos com textos carimbados sob medida</p>
</div>

<div class="container">
    <!-- ESQUERDA: FORMULÁRIO COM TODOS OS CAMPOS CRVL -->
    <div class="panel">
        <h2>1. Dados do Painel de Admin</h2>
        
        <div class="upload-area" onclick="document.getElementById('fileInput').click()">
            <span id="uploadText">Selecione a Imagem/Foto de Fundo do CRVL</span>
            <input type="file" id="fileInput" accept="image/*" style="display: none;" onchange="carregarImagemBase(this)">
        </div>

        <form id="adminForm">
            {% for campo in campos %}
            <div class="form-group">
                <label for="{{ campo }}">{{ campo }}</label>
                <input type="text" id="{{ campo }}" class="input-doc" data-campo="{{ campo }}" placeholder="Digite para aplicar na foto..." oninput="atualizarDocumento()">
            </div>
            {% endfor %}
        </form>
        
        <button class="btn btn-success" onclick="baixarImagemFinal()">Baixar Documento Preenchido</button>
        <div class="helper-text">
            <b>💡 Como posicionar os textos:</b><br>
            1. Clique dentro de uma das caixas acima (ex: Placa).<br>
            2. Vá na foto da direita e <b>clique no local exato</b> onde aquela informação deve ficar.<br>
            3. Digite o valor e o texto se moverá para onde você escolheu.
        </div>
    </div>

    <!-- DIREITA: VISUALIZAÇÃO EM TEMPO REAL -->
    <div class="panel">
        <h2>2. Visualização do Documento Modificado</h2>
        <div class="canvas-container">
            <canvas id="documentCanvas"></canvas>
        </div>
    </div>
</div>

<script>
    let imagemBase = new Image();
    const canvas = document.getElementById('documentCanvas');
    const ctx = canvas.getContext('2d');
    
    // Configura posições iniciais padrão espalhadas sequencialmente na tela
    let posicoesTexto = {};
    {% for campo in campos %}
        posicoesTexto["{{ campo }}"] = { x: 40, y: 40 + ({{ loop.index0 }} * 35) };
    {% endfor %}

    let campoSelecionadoAtual = "Código Renavam";

    // Mapeia qual campo o admin está preenchendo no momento
    document.querySelectorAll('.input-doc').forEach(input => {
        input.addEventListener('focus', (e) => {
            campoSelecionadoAtual = e.target.getAttribute('data-campo');
        });
    });

    function carregarImagemBase(input) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagemBase.src = e.target.result;
                imagemBase.onload = function() {
                    canvas.width = imagemBase.width;
                    canvas.height = imagemBase.height;
                    document.getElementById('uploadText').innerText = "Modelo de CRVL carregado!";
                    atualizarDocumento();
                }
            }
            reader.readAsDataURL(input.files[0]);
        }
    }

    function atualizarDocumento() {
        if (!imagemBase.src) return;
        
        // Limpa e redesenha o fundo
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(imagemBase, 0, 0);
        
        // Estilo da fonte do carimbo (Ajuste o tamanho '16px' se precisar de letras maiores/menores)
        ctx.font = "bold 16px Arial";
        ctx.fillStyle = "black";
        
        // Aplica o texto de cada input na respectiva coordenada cadastrada pelo clique
        document.querySelectorAll('.input-doc').forEach(input => {
            const nomeCampo = input.getAttribute('data-campo');
            const valorTexto = input.value;
            const posicao = posicoesTexto[nomeCampo];
            
            if (valorTexto && posicao) {
                ctx.fillText(valorTexto, posicao.x, posicao.y);
            }
        });
    }

    // Altera a coordenada do campo selecionado ao clicar na foto
    canvas.addEventListener('click', function(e) {
        if (!imagemBase.src) return;
        
        const rect = canvas.getBoundingClientRect();
        const escalaX = canvas.width / rect.width;
        const escalaY = canvas.height / rect.height;
        
        const cliqueX = (e.clientX - rect.left) * escalaX;
        const cliqueY = (e.clientY - rect.top) * escalaY;
        
        if (campoSelecionadoAtual) {
            posicoesTexto[campoSelecionadoAtual] = { x: cliqueX, y: cliqueY };
            atualizarDocumento();
        }
    });

    function baixarImagemFinal() {
        if (!imagemBase.src) {
            alert("Por favor, carregue uma imagem de fundo primeiro!");
            return;
        }
        const link = document.createElement('a');
        link.download = 'CRVL_Gerado_Preenchido.png';
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
