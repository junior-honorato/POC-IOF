import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="POC - Simulador IOF VGBL (Regra 2026)", layout="wide")

# --- LÓGICA DE CÁLCULO (MOTOR BACK-OFFICE) ---
def calcular_iof_vgbl(aporte_atual, mensalidade_atual, hist_declarado, hist_interno, is_pj):
    LIMITE_ANUAL = 600000.00
    ALIQUOTA_IOF = 0.05
    
    # 1. Regra de isenção para aportes corporativos (PJ)
    if is_pj:
        return {
            "aporte_bruto": aporte_atual,
            "iof_cobrado": 0.00,
            "reserva_liquida": aporte_atual,
            "parcela_isenta": aporte_atual,
            "parcela_tributada": 0.00,
            "mensalidade_bruta": mensalidade_atual,
            "iof_mensalidade": 0.00,
            "reserva_liquida_mensal": mensalidade_atual,
            "mensalidade_isenta": mensalidade_atual,
            "mensalidade_tributada": 0.00,
            "historico_total_previo": 0.00,
            "limite_inicial": 0.00,
            "status": "Isento (Aporte PJ)"
        }
    
    # 2. CONSOLIDAÇÃO DO HISTÓRICO PRÉVIO E LIMITE INICIAL
    historico_total_previo = hist_declarado + hist_interno
    limite_inicial = max(0.00, LIMITE_ANUAL - historico_total_previo)
    
    # 3. Processamento da Contribuição Eventual
    if aporte_atual <= limite_inicial:
        parcela_isenta_avulso = aporte_atual
        parcela_tributada_avulso = 0.00
        iof_avulso = 0.00
        reserva_liquida_avulso = aporte_atual
        limite_restante_apos_avulso = limite_inicial - aporte_atual
    else:
        parcela_isenta_avulso = limite_inicial
        parcela_tributada_avulso = aporte_atual - limite_inicial
        reserva_sobre_excedente_avulso = parcela_tributada_avulso / (1 + ALIQUOTA_IOF)
        iof_avulso = reserva_sobre_excedente_avulso * ALIQUOTA_IOF
        reserva_liquida_avulso = parcela_isenta_avulso + reserva_sobre_excedente_avulso
        limite_restante_apos_avulso = 0.00
        
    # 4. Processamento da Mensalidade Programada (Cascata)
    if mensalidade_atual <= limite_restante_apos_avulso:
        parcela_isenta_mensal = mensalidade_atual
        parcela_tributada_mensal = 0.00
        iof_mensal = 0.00
        reserva_liquida_mensal = mensalidade_atual
    else:
        parcela_isenta_mensal = limite_restante_apos_avulso
        parcela_tributada_mensal = mensalidade_atual - limite_restante_apos_avulso
        reserva_sobre_excedente_mensal = parcela_tributada_mensal / (1 + ALIQUOTA_IOF)
        iof_mensal = reserva_sobre_excedente_mensal * ALIQUOTA_IOF
        reserva_liquida_mensal = parcela_isenta_mensal + reserva_sobre_excedente_mensal
        
    status = "Tributado 'Por Dentro'" if (iof_avulso > 0 or iof_mensal > 0) else "Isento (Dentro do Limite Global)"
    
    return {
        "aporte_bruto": aporte_atual,
        "iof_cobrado": iof_avulso,
        "reserva_liquida": reserva_liquida_avulso,
        "parcela_isenta": parcela_isenta_avulso,
        "parcela_tributada": parcela_tributada_avulso,
        "mensalidade_bruta": mensalidade_atual,
        "iof_mensalidade": iof_mensal,
        "reserva_liquida_mensal": reserva_liquida_mensal,
        "mensalidade_isenta": parcela_isenta_mensal,
        "mensalidade_tributada": parcela_tributada_mensal,
        "historico_total_previo": historico_total_previo,
        "limite_inicial": limite_inicial,
        "status": status
    }

# --- FUNÇÃO AUXILIAR DE FORMATAÇÃO E INPUT ---
def formata_br(valor):
    if isinstance(valor, str):
        return valor
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def parse_moeda(val_str):
    val_str = val_str.replace("R$", "").strip()
    if not val_str:
        return 0.0
    if "," in val_str:
        val_str = val_str.replace(".", "").replace(",", ".")
    else:
        if val_str.count(".") == 1:
            partes = val_str.split(".")
            if len(partes[1]) == 2:
                pass
            else:
                val_str = val_str.replace(".", "")
        else:
            val_str = val_str.replace(".", "")
    try:
        return float(val_str)
    except ValueError:
        return 0.0

def format_moeda_callback(key):
    val_str = st.session_state[key]
    val_float = parse_moeda(val_str)
    st.session_state[key] = formata_br(val_float)

def input_moeda(label, default_value, key):
    if key not in st.session_state:
        st.session_state[key] = formata_br(default_value)
    
    val_str = st.text_input(label, key=key, on_change=format_moeda_callback, args=(key,))
    val_float = parse_moeda(val_str)
    return val_float

# --- DIALOG: DETALHAMENTO MATEMÁTICO ---
@st.dialog("🧮 Detalhamento Matemático (Passo a Passo)", width="large")
def exibir_detalhes_matematicos(res, hist_dec, hist_int, ap_atual, mens_atual, is_pj):
    st.markdown("### 📋 Consolidação de Limites")
    
    if is_pj:
        st.markdown("**Cenário Corporativo (Pessoa Jurídica)**")
        st.markdown("Contribuições realizadas sob CNPJ (Pessoa Jurídica) possuem isenção total de IOF e não consomem o teto anual de isenção global de Pessoa Física.")
        st.latex(r"IOF = 0,00")
        st.latex(rf"R_{{\text{{líquida}}}} = {formata_br(ap_atual + mens_atual)}")
        return
        
    st.markdown("#### 1. Histórico Prévio Acumulado")
    st.markdown("O histórico prévio é a soma dos aportes declarados em outras instituições com os aportes internos na Sicoob Seguradora:")
    st.latex(r"H_{\text{prévio}} = H_{\text{declarado}} + H_{\text{interno}}")
    st.latex(rf"{formata_br(hist_dec + hist_int)} = {formata_br(hist_dec)} + {formata_br(hist_int)}")
    
    st.markdown("#### 2. Limite Isento Inicial Disponível")
    st.markdown("O limite isento anual por CPF em 2026 é de **R$ 600.000,00**. O limite inicial disponível é o teto anual menos o histórico prévio acumulado:")
    st.latex(r"L_{\text{inicial}} = \max(0, 600.000,00 - H_{\text{prévio}})")
    lim_ini = max(0.0, 600000.0 - (hist_dec + hist_int))
    st.latex(rf"{formata_br(lim_ini)} = \max(0, 600.000,00 - {formata_br(hist_dec + hist_int)})")
    
    st.divider()
    
    st.markdown("### ⚡ 1. Contribuição Eventual (Aporte Avulso)")
    st.markdown("O aporte eventual consome o limite disponível prioritariamente.")
    
    if ap_atual <= lim_ini:
        st.markdown("**Cenário A: Aporte dentro do limite disponível**")
        st.latex(rf"A_{{\text{{atual}}}} \le L_{{\text{{inicial}}}} \quad ({formata_br(ap_atual)} \le {formata_br(lim_ini)})")
        st.markdown("Como o aporte atual é menor ou igual ao limite disponível, toda a contribuição é isenta de IOF.")
        st.latex(rf"A_{{\text{{isento}}}} = A_{{\text{{atual}}}} = {formata_br(ap_atual)}")
        st.latex(r"A_{\text{tributável}} = 0,00")
        st.latex(r"IOF_{A} = 0,00")
        st.latex(rf"R_{{\text{{líquida, A}}}} = A_{{\text{{atual}}}} = {formata_br(ap_atual)}")
        lim_rest = lim_ini - ap_atual
        st.latex(r"L_{\text{restante}} = L_{\text{inicial}} - A_{\text{atual}}")
        st.latex(rf"{formata_br(lim_rest)} = {formata_br(lim_ini)} - {formata_br(ap_atual)}")
    else:
        st.markdown("**Cenário B: Aporte excede o limite disponível**")
        st.latex(rf"A_{{\text{{atual}}}} > L_{{\text{{inicial}}}} \quad ({formata_br(ap_atual)} > {formata_br(lim_ini)})")
        st.markdown("A parcela dentro do limite é isenta. O excedente é tributado.")
        st.latex(rf"A_{{\text{{isento}}}} = L_{{\text{{inicial}}}} = {formata_br(lim_ini)}")
        trib_a = ap_atual - lim_ini
        st.latex(r"A_{\text{tributável}} = A_{\text{atual}} - L_{\text{inicial}}")
        st.latex(rf"{formata_br(trib_a)} = {formata_br(ap_atual)} - {formata_br(lim_ini)}")
        
        st.markdown("O cálculo do **IOF 'Por Dentro'** (alíquota de 5%) divide a parcela tributável por 1,05 para encontrar a base de cálculo líquida, retendo 5% sobre esta base:")
        st.latex(r"BC_{A} = \frac{A_{\text{tributável}}}{1,05}")
        bc_a = trib_a / 1.05
        st.latex(rf"{formata_br(bc_a)} = \frac{{{formata_br(trib_a)}}}{{1,05}}")
        
        st.latex(r"IOF_{A} = BC_{A} \times 0,05")
        iof_a = bc_a * 0.05
        st.latex(rf"{formata_br(iof_a)} = {formata_br(bc_a)} \times 0,05")
        
        st.markdown("A reserva líquida efetiva do aporte é a soma da parcela isenta com a base de cálculo líquida do excedente:")
        st.latex(r"R_{\text{líquida, A}} = A_{\text{isento}} + BC_{A}")
        st.latex(rf"{formata_br(lim_ini + bc_a)} = {formata_br(lim_ini)} + {formata_br(bc_a)}")
        st.markdown("*(Nota de conciliação: Reserva Líquida + IOF = Valor Bruto)*")
        st.latex(rf"{formata_br(lim_ini + bc_a)} + {formata_br(iof_a)} = {formata_br(ap_atual)}")
        
        lim_rest = 0.0
        st.latex(r"L_{\text{restante}} = 0,00")
        
    st.divider()
    
    st.markdown("### 📅 2. Contribuição Programada Mensal")
    st.markdown("A mensalidade consome o limite restante após a eventual.")
    
    if mens_atual <= lim_rest:
        st.markdown("**Cenário A: Mensalidade dentro do limite restante**")
        st.latex(rf"M_{{\text{{atual}}}} \le L_{{\text{{restante}}}} \quad ({formata_br(mens_atual)} \le {formata_br(lim_rest)})")
        st.markdown("Como a mensalidade atual é menor ou igual ao limite restante, toda a contribuição é isenta de IOF.")
        st.latex(rf"M_{{\text{{isenta}}}} = M_{{\text{{atual}}}} = {formata_br(mens_atual)}")
        st.latex(r"M_{\text{tributável}} = 0,00")
        st.latex(r"IOF_{M} = 0,00")
        st.latex(rf"R_{{\text{{líquida, M}}}} = M_{{\text{{atual}}}} = {formata_br(mens_atual)}")
    else:
        st.markdown("**Cenário B: Mensalidade excede o limite restante**")
        st.latex(rf"M_{{\text{{atual}}}} > L_{{\text{{restante}}}} \quad ({formata_br(mens_atual)} > {formata_br(lim_rest)})")
        st.markdown("A parcela dentro do limite é isenta. O excedente é tributado.")
        st.latex(rf"M_{{\text{{isenta}}}} = L_{{\text{{restante}}}} = {formata_br(lim_rest)}")
        trib_m = mens_atual - lim_rest
        st.latex(r"M_{\text{tributável}} = M_{\text{atual}} - L_{\text{restante}}")
        st.latex(rf"{formata_br(trib_m)} = {formata_br(mens_atual)} - {formata_br(lim_rest)}")
        
        st.markdown("O cálculo do **IOF 'Por Dentro'** (alíquota de 5%) divide a parcela tributável por 1,05 para encontrar a base de cálculo líquida, retendo 5% sobre esta base:")
        st.latex(r"BC_{M} = \frac{M_{\text{tributável}}}{1,05}")
        bc_m = trib_m / 1.05
        st.latex(rf"{formata_br(bc_m)} = \frac{{{formata_br(trib_m)}}}{{1,05}}")
        
        st.latex(r"IOF_{M} = BC_{M} \times 0,05")
        iof_m = bc_m * 0.05
        st.latex(rf"{formata_br(iof_m)} = {formata_br(bc_m)} \times 0,05")
        
        st.markdown("A reserva líquida efetiva da mensalidade é a soma da parcela isenta com a base de cálculo líquida do excedente:")
        st.latex(r"R_{\text{líquida, M}} = M_{\text{isenta}} + BC_{M}")
        st.latex(rf"{formata_br(lim_rest + bc_m)} = {formata_br(lim_rest)} + {formata_br(bc_m)}")
        st.markdown("*(Nota de conciliação: Reserva Líquida + IOF = Valor Bruto)*")
        st.latex(rf"{formata_br(lim_rest + bc_m)} + {formata_br(iof_m)} = {formata_br(mens_atual)}")

# --- INTERFACE DO USUÁRIO (FRONT-END) ---
st.title("🛡️ Simulador de Retenção de IOF - VGBL (Regras 2026)")
st.markdown("Validação da esteira de cálculo de IOF 'Por Dentro' considerando o teto global de **R$ 600.000,00**.")
st.divider()

quadrante_esquerdo, quadrante_direito = st.columns([1, 1], gap="large")

# === QUADRANTE ESQUERDO: INPUTS E CARDS DE RESULTADO ===
with quadrante_esquerdo:
    st.subheader("1. Parâmetros de Entrada")
    
    st.markdown("**1º Passo: Avaliação de Histórico (Consumo do Teto):**")
    
    tem_aporte_externo = st.radio(
        "O cliente realizou aportes em outras Seguradoras em 2026? (Autodeclaração)",
        ["Não", "Sim"],
        index=0,
        key="tem_aporte_ext"
    )
    
    hist_declarado = 0.0
    
    if tem_aporte_externo == "Sim":
        st.info("ℹ️ O valor informado abaixo serve estritamente para abater o limite global de isenção (R$ 600 mil). Não há cálculo financeiro ou retenção de IOF por parte da nossa Seguradora sobre este montante.")
        hist_declarado = input_moeda("Valor Aportado em Outras Seguradoras", 500000.0, key="hist_dec")
        
    hist_interno = input_moeda("Saldo na Sicoob Seguradora", 80000.0, key="hist_int")
    
    st.markdown("**2º Passo: Valores da Operação Atual:**")
    aporte_atual = input_moeda("Valor da Contribuição Eventual", 15000.0, key="aporte_evt")
    mensalidade_atual = input_moeda("Contribuição Programada Mensal", 10000.0, key="mensal_prg")
    
    is_pj = False

    # Roda o motor de cálculo
    resultado = calcular_iof_vgbl(aporte_atual, mensalidade_atual, hist_declarado, hist_interno, is_pj)
    
    st.divider()
    st.subheader("2. Resultado Operacional")
    
    # --- TERMÔMETRO VISUAL DO LIMITE ---
    if is_pj:
        st.markdown("<div style='background-color:#1e4620; padding:15px; border-radius:8px; color:white; font-size:16px;'><b>✅ Aporte Corporativo (PJ)</b><br>Isenção garantida por lei. Não consome o limite PF.</div>", unsafe_allow_html=True)
    else:
        # Verifica o impacto total da operação no teto
        limite_inicial = max(0.00, 600000.00 - (hist_declarado + hist_interno))
        consumo_total_operacao = aporte_atual + mensalidade_atual
        limite_final_projetado = limite_inicial - consumo_total_operacao
        
        if limite_final_projetado >= 0:
            st.markdown(f"<div style='background-color:#1e4620; padding:15px; border-radius:8px; color:white; font-size:16px;'><b>✅ Limite Isento Restante: {formata_br(limite_final_projetado)}</b><br>A soma da eventual com a contribuição programada está dentro do teto global.</div>", unsafe_allow_html=True)
        else:
            estouro = abs(limite_final_projetado) if limite_inicial > 0 else consumo_total_operacao
            st.markdown(f"<div style='background-color:#7f1d1d; padding:15px; border-radius:8px; color:white; font-size:16px;'><b>⚠️ Limite Global Estourado!</b><br>A operação ultrapassou o teto em <b>{formata_br(estouro)}</b>. Cobrança de IOF ativada.</div>", unsafe_allow_html=True)
            
            if resultado['iof_mensalidade'] > 0:
                st.warning("⚠️ **Alerta Back-office:** A contribuição programada mensal foi afetada. O faturamento recorrente deverá reter o IOF automaticamente.")

    st.markdown("<br>", unsafe_allow_html=True) # Espaçamento

    # Cards de Resultado
    c1, c2, c3 = st.columns(3)
    c1.metric("Débito Eventual", formata_br(resultado['aporte_bruto']))
    c2.metric("IOF Retido (Eventual)", formata_br(resultado['iof_cobrado']))
    c3.metric("Reserva Efetiva (Eventual)", formata_br(resultado['reserva_liquida']))

    st.divider()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Débito Prog. Mensal", formata_br(resultado['mensalidade_bruta']))
    m2.metric("IOF Retido (Prog. Mensal)", formata_br(resultado['iof_mensalidade']))
    m3.metric("Reserva Efetiva (Prog. Mensal)", formata_br(resultado['reserva_liquida_mensal']))

# === QUADRANTE DIREITO: MEMÓRIA DE CÁLCULO E AUDITORIA ===
with quadrante_direito:
    st.subheader("📊 Auditoria Tributária (Memória de Cálculo)")
    
    col_status, col_btn = st.columns([3, 2])
    with col_status:
        st.markdown(f"**Status:** `{resultado['status']}`")
    with col_btn:
        if st.button("🧮 Ver Matemática", use_container_width=True):
            exibir_detalhes_matematicos(resultado, hist_declarado, hist_interno, aporte_atual, mensalidade_atual, is_pj)
    
    # Preparação das variáveis para a visão consolidada
    historico_previo = resultado['historico_total_previo']
    limite_inicial = resultado['limite_inicial'] if not is_pj else "N/A"
    
    total_operacao = resultado['aporte_bruto'] + resultado['mensalidade_bruta']
    limite_final = max(0.00, 600000.00 - (historico_previo + total_operacao)) if not is_pj else "N/A"
    novo_historico_acumulado = historico_previo + total_operacao if not is_pj else "N/A"
    
    base_calc_avulso = resultado['parcela_tributada'] / 1.05 if resultado['parcela_tributada'] > 0 else 0.00
    base_calc_mensal = resultado['mensalidade_tributada'] / 1.05 if resultado['mensalidade_tributada'] > 0 else 0.00
    
    # 1. Visão Global da Operação
    st.markdown("#### 1. Visão Global da Operação")
    df_global = pd.DataFrame({
        "Métrica / Etapa do Motor": [
            "Teto Anual Global",
            "Histórico Anterior (Autodeclaração + Sicoob)",
            "Limite Isento DISPONÍVEL (Antes da Operação)",
            "Total Solicitado na Operação (Eventual + Mensal)",
            "Novo Histórico Consumido Acumulado",
            "Limite Isento RESTANTE (Após Operação)"
        ],
        "Valor Auditado": [
            "R$ 600.000,00",
            formata_br(historico_previo),
            formata_br(limite_inicial),
            formata_br(total_operacao),
            formata_br(novo_historico_acumulado),
            formata_br(limite_final)
        ]
    })
    st.table(df_global.style.hide(axis="index"))
    
    # 2. Tributação: Contribuição Eventual
    st.markdown("#### 2. Tributação: Contribuição Eventual")
    df_eventual = pd.DataFrame({
        "Métrica / Etapa do Motor": [
            "Valor Bruto Solicitado",
            "Parcela Enquadrada na Isenção",
            "Parcela TRIBUTÁVEL (Excedente)",
            "Base de Cálculo 'Por Dentro' (Tributável ÷ 1,05)",
            "IOF Retido (Base × 5%)"
        ],
        "Valor Auditado": [
            formata_br(resultado['aporte_bruto']),
            formata_br(resultado['parcela_isenta']),
            formata_br(resultado['parcela_tributada']),
            formata_br(base_calc_avulso),
            formata_br(resultado['iof_cobrado'])
        ]
    })
    st.table(df_eventual.style.hide(axis="index"))
    
    # 3. Tributação: Contribuição Programada Mensal
    st.markdown("#### 3. Tributação: Contribuição Programada Mensal")
    df_mensal = pd.DataFrame({
        "Métrica / Etapa do Motor": [
            "Valor Bruto Programado",
            "Parcela Enquadrada na Isenção",
            "Parcela TRIBUTÁVEL (Excedente)",
            "Base de Cálculo 'Por Dentro' (Tributável ÷ 1,05)",
            "IOF Retido (Base × 5%)"
        ],
        "Valor Auditado": [
            formata_br(resultado['mensalidade_bruta']),
            formata_br(resultado['mensalidade_isenta']),
            formata_br(resultado['mensalidade_tributada']),
            formata_br(base_calc_mensal),
            formata_br(resultado['iof_mensalidade'])
        ]
    })
    st.table(df_mensal.style.hide(axis="index"))