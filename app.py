import os
import datetime
from flask import Flask, render_template_string

app = Flask(__name__)

# Lista de campos oficiais do Vio para você preencher no painel admin
CAMPOS_ADMIN = [
    "Placa",
    "RENAVAM",
    "Chassi (4 últimos dígitos)",
    "Marca / Modelo",
    "Ano",
    "Nome Completo do Proprietário"
]

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validador Vio Oficial - SENATRAN</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 1000px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .panel { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: fit-content; }
        h2 { margin-top: 0; color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; font-size: 18px; }
        
        /* Formulário Admin */
        .form-group { margin-bottom: 12px; }
        label { display: block; font-weight: 600; margin-bottom: 4px; color: #34495e; font-size: 13px; }
        input[type="text"] { width: 100%; padding: 10px 12px; border: 1px solid #ccd1d9; border-radius: 6px; box-sizing: border-box; background-color: #fdfdfd; font-size: 14px; color: #444; }
        
        /* Layout Celular - Padrão Vio Original */
        .phone-preview { width: 100%; max-width: 380px; background: #ffffff; min-height: 650px; border-radius: 24px; box-shadow: 0 12px 30px rgba(0,0,0,0.15); padding: 20px; box-sizing: border-box; margin: 0 auto; }
        .vio-header { text-align: center; margin-bottom: 18px; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; }
        .vio-header .gov-title { font-size: 10px; font-weight: bold; color: #0056b3; letter-spacing: 0.5px; margin: 0; }
        .vio-header .ministry { font-size: 12px; color: #4a5568; margin: 3px 0 0 0; font-weight: 600; }
        
        /* Caixa Verde Oficial Vio */
        .status-box { background-color: #e6f6ec; border: 2px solid #23a95c; border-radius: 14px; padding: 14px; text-align: center; margin-bottom: 20px; }
        .status-box .icon { font-size: 28px; color: #23a95c; margin-bottom: 2px; font-weight: bold; }
        .status-box .title { font-size: 16px; font-weight: 800; color: #23a95c; margin: 0; letter-spacing: 0.5px; text-transform: uppercase; }
        
        /* Cards de Dados */
        .section-title { font-size: 11px; font-weight: 700; color: #718096; text-transform: uppercase; margin: 15px 0 6px 4px; letter-spacing: 0.5px; }
        .info-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 10px 14px; margin-bottom: 10px; }
        .info-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #edf2f7; }
        .info-row:last-child { border-bottom: none; }
        .info-label { font-size: 12px; color: #718096; font-weight: 500; }
        .info-value { font-size: 13px; color: #1a202c; font-weight: 700; text-align: right; font-family: Arial, sans-serif; }
        
        /* Rodapé Vio */
        .vio-footer { text-align: center; margin-top: 25px; border-top: 1px solid #e2e8f0; padding-top: 15px; }
        .vio-footer p { font-size: 10px; color: #718096; margin: 4px 0; line-height: 14px; }
        .vio-footer .stamp { font-weight: bold; color: #4a5568; font-size: 11px; }
    </style>
</head>
<body>

<div class="container">
    <!-- ESQUERDA: PAINEL DE CONTROLE ADMIN -->
    <div class="panel">
        <h2>Painel Administrativo (Digitação Manual)</h2>
        <form id="adminForm">
            <div class="form-group">
                <label>Placa</label>
                <input type="text" id="in_placa" placeholder="Ex: ABC1D23" oninput="atualizarTela()">
            </div>
            <div class="form-group">
                <label>RENAVAM</label>
                <input type="text" id="in_renavam" placeholder="Ex: 12345678901" oninput="atualizarTela()">
            </div>
            <div class="form-group">
                <label>Chassi (4 últimos dígitos)</label>
                <input type="text" id="in_chassi" placeholder="Ex: 1234" oninput="atualizarTela()">
            </div>
            <div class="form-group">
                <label>Marca / Modelo</label>
                <input type="text" id="in_modelo" placeholder="Ex: VW/GOL TLI" oninput="atualizarTela()">
            </div>
            <div class="form-group">
                <label>Ano</label>
                <input type="text" id="in_ano" placeholder="Ex: 2023/2024" oninput="atualizarTela()">
            </div>
            <div class="form-group">
                <label>Nome Completo do Proprietário</label>
                <input type="text" id="in_nome" placeholder="Ex: JOÃO DOS SANTOS SILVA" oninput="atualizarTela()">
            </div>
        </form>
    </div>

    <!-- DIREITA: APP VIO ORIGINAL EM TEMPO REAL -->
    <div class="phone-preview">
        <div class="vio-header">
            <p class="gov-title">SENATRAN · GOVERNO FEDERAL</p>
            <p class="ministry">Ministério dos Transportes</p>
        </div>

        <div class="status-box">
            <div class="icon">✓</div>
            <h2 class="title">DOCUMENTO AUTÊNTICO</h2>
        </div>

        <div class="section-title">Veículo</div>
        <div class="info-card">
            <div class="info-row"><span class="info-label">Placa</span><span class="info-value" id="out_placa"></span></div>
            <div class="info-row"><span class="info-label">RENAVAM</span><span class="info-value" id="out_renavam"></span></div>
            <div class="info-row"><span class="info-label">Chassi</span><span class="info-value" id="out_chassi"></span></div>
            <div class="info-row"><span class="info-label">Marca/Modelo</span><span class="info-value" id="out_modelo"></span></div>
            <div class="info-row"><span class="info-label">Ano</span><span class="info-value" id="out_ano"></span></div>
        </div>

        <div class="section-title">Proprietário</div>
        <div class="info-card">
            <div class="info-row"><span class="info-label">Nome</span><span class="info-value" id="out_nome" style="text-align: left; max-width: 200px;"></span></div>
        </div>

        <div class="vio-footer">
            <p class="stamp">Emitido por: SERPRO / SENATRAN</p>
            <p>Data/Hora da consulta: <span style="font-weight: bold;">{{ data_hora }}</span></p>
            <p style="margin-top: 12px; font-size: 9px; color: #a0aec0;">Este documento foi consultado diretamente na base de dados nacional. A autenticidade só é garantida através do aplicativo Vio.</p>
        </div>
    </div>
</div>

<script>
    function atualizarTela() {
        // Pega o que foi digitado e joga na tela do Vio em Letras Maiúsculas
        document.getElementById('out_placa').innerText = document.getElementById('in_placa').value.toUpperCase() || "-";
        document.getElementById('out_renavam').innerText = document.getElementById('in_renavam').value || "-";
        
        let chassiDig = document.getElementById('in_chassi').value;
        document.getElementById('out_chassi').innerText = chassiDig ? "***" + chassiDig.toUpperCase() : "-";
        
        document.getElementById('out_modelo').innerText = document.getElementById('in_modelo').value.toUpperCase() || "-";
        document.getElementById('out_ano').innerText = document.getElementById('in_ano').value || "-";
        document.getElementById('out_nome').innerText = document.getElementById('in_nome').value.toUpperCase() || "-";
    }
    
    // Roda uma vez para limpar os traços iniciais
    atualizarTela();
</script>

</body>
</html>
"""

@app.route('/')
def index():
    # Carimba o horário atual direto do servidor de forma estática
    agora = datetime.datetime.now()
    data_hora_formatada = agora.strftime("%d/%m/%Y %H:%M:%S")
    return render_template_string(HTML_INTERFACE, data_hora=data_hora_formatada)

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
