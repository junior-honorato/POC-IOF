# 🛡️ Simulador de Retenção de IOF - VGBL (Regras 2026)

Esta é uma POC (Prova de Conceito) interativa desenvolvida em **Streamlit** para simulação e validação da esteira de cálculo de retenção de **IOF "Por Dentro"** em operações de previdência complementar do tipo **VGBL**, em conformidade com as regras estabelecidas para 2026.

O simulador avalia o consumo do teto anual de isenção global de **R$ 600.000,00** por CPF e aplica a tributação em cascata sobre as contribuições.

---

## 🎯 Principais Funcionalidades

1. **Gestão do Teto Global (R$ 600.000,00/ano):**
   * **Histórico Interno:** Importa/recebe o saldo atualizado na Sicoob Seguradora.
   * **Autodeclaração:** Menu interativo para informar aportes realizados em outras instituições financeiras no ano corrente.

2. **Cálculo da Operação Atual (Ordem de Consumo):**
   * **1º - Contribuição Eventual:** Consome prioritariamente o limite de isenção disponível.
   * **2º - Contribuição Programada Mensal:** Consome o saldo de limite remanescente após o aporte eventual.

3. **Auditoria Tributária Dividida em Blocos:**
   * **Bloco 1 - Visão Global da Operação:** Demonstrativo do consumo do limite disponível e projeção de excedente.
   * **Bloco 2 - Tributação da Contribuição Eventual:** Memória de cálculo do IOF (alíquota nominal de 5% calculada "por dentro", resultando em uma divisão por $1,05$) sobre o valor excedente da eventual.
   * **Bloco 3 - Tributação da Contribuição Programada Mensal:** Memória de cálculo do IOF "por dentro" sobre o excedente da contribuição programada.

4. **Portabilidade e Facilidade de Uso:**
   * Geração de um executável independente (`.exe`) para Windows, eliminando a necessidade de instalar Python ou dependências em máquinas de outros usuários.

---

## 💻 Como Executar Localmente

### Pré-requisitos
* Python 3.10+ instalado.

### Instalação das dependências
Abra o terminal na pasta do projeto e execute:
```bash
pip install streamlit pandas
```

### Inicializando o servidor
Execute o comando abaixo para abrir o painel interativo no seu navegador:
```bash
streamlit run app.py
```

---

## 📦 Como Recompilar o Executável

Caso faça modificações no código em `app.py` e precise atualizar o executável para compartilhamento, utilize o **PyInstaller** através do arquivo de especificações `.spec`:

```bash
# Instale o PyInstaller no seu ambiente
pip install pyinstaller

# Execute a compilação utilizando o arquivo de especificação
pyinstaller SimuladorIOF_VGBL.spec --clean
```

O novo arquivo compilado estará disponível na pasta `./dist/SimuladorIOF_VGBL.exe`.
