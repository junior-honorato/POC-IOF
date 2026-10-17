# CLAUDE.md — POC-IOF

Simulador em Streamlit da retenção de IOF "por dentro" (5%) sobre aportes VGBL, com teto anual de isenção de R$ 600 mil por CPF (regras 2026).

## Stack

- Python 3.10+ (indicado no README), Streamlit + pandas.
- `app.py`: toda a lógica (função `calcular_iof_vgbl`) e a interface.
- `run_app.py`: launcher usado para empacotar com PyInstaller (resolve `sys._MEIPASS`).

## Como rodar localmente (macOS)

```bash
python3 -m venv venv && source venv/bin/activate
pip install streamlit pandas
streamlit run app.py
```

## Variáveis de ambiente

Nenhuma (o app não lê `.env`).

## Armadilhas

- Não há `requirements.txt`: dependências só estão no README (streamlit, pandas).
- O README cita `SimuladorIOF_VGBL.spec` para gerar o `.exe` (Windows) com PyInstaller, mas o arquivo não está no repositório; `build/` e `dist/` são ignorados.
- Ordem de consumo do limite: contribuição eventual primeiro, depois a programada mensal; aportes PJ são isentos.

## Fluxo de trabalho

- Autonomia para commitar e dar push na main (projeto pessoal).
- Responder sempre em português do Brasil.
