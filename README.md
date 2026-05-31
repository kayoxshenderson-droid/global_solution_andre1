# Global Solution 2026 — Monitoramento de Missão Espacial

> **Disciplina:** Ciência da Computação — FIAP  
> **Tema:** Soluções em Energias Renováveis e Sustentáveis  

Sistema de monitoramento inteligente para uma missão espacial experimental. Simula, interpreta e visualiza dados operacionais de energia, temperatura, comunicação e status dos módulos da missão, com geração automática de alertas e tomada de decisão automatizada.

---

## Funcionalidades

- Simulação de 5 módulos operacionais com variáveis físicas realistas (irradiação senoidal, temperatura, SOC de bateria)
- Geração automática de alertas em 3 níveis: `INFO`, `WARNING` e `CRITICAL`
- Tomada de decisão automatizada baseada no estado energético e de saúde da missão
- Health score composto (0–100) que reflete a sustentabilidade e segurança da operação
- 5 cenários de simulação com perfis distintos de estresse
- Dashboard gráfico com 6 painéis de visualização (geração, bateria, saúde, renovável, alertas, estado)
- Exportação de relatório em JSON
- Modo interativo via menu e modo automático via CLI

---

## Estrutura do Projeto

```
global_solution_andre1/
├── main.py                        # Ponto de entrada (CLI + menu interativo)
├── charts.py                      # Dashboard gráfico (matplotlib)
├── mission_monitor/               # Pacote principal
│   ├── __init__.py
│   ├── models.py                  # Dataclasses: ModuleReading, Alert, MissionSnapshot
│   ├── scenarios.py               # Cenários e limites operacionais por módulo
│   ├── monitor.py                 # MissionMonitor — simulação física dos módulos
│   ├── alerts.py                  # Lógica de alertas e tomada de decisão
│   ├── display.py                 # Exibição formatada no terminal (com cores ANSI)
│   └── report.py                  # Exportação de relatório JSON
└── tests/
    ├── __init__.py
    └── test_monitor.py            # Testes unitários
```

---

## Como Executar

**Pré-requisito:** Python 3.10+

```bash
# Modo automático — gera N leituras e exibe no terminal
python main.py --steps 5

# Modo automático com cenário específico
python main.py --scenario "Emergencia energetica" --steps 3

# Modo interativo (menu)
python main.py
```

**Dashboard gráfico** (requer `matplotlib`):

```bash
pip install matplotlib

# Gera PNG com 12 leituras do cenário nominal
python charts.py

# Cenário de emergência, 15 leituras, arquivo de saída customizado
python charts.py --scenario "Emergencia energetica" --steps 15 --output dashboard.png
```

**Testes:**

```bash
python -m unittest
```

---

## Cenários Disponíveis

| Cenário | Descrição |
|---|---|
| `Operacao nominal` | Condições ideais de operação |
| `Baixa irradiacao` | Geração solar reduzida a 55% |
| `Instabilidade de comunicacao` | Ruído de 35% nos links de telemetria |
| `Estresse termico` | Bias de +12 °C nos módulos |
| `Emergencia energetica` | Geração baixa (32%) e consumo elevado (128%) |

---

## Módulos Monitorados

| Módulo | Faixa de Temperatura Segura | Energia WARNING | Energia CRITICAL |
|---|---|---|---|
| Painel Solar | −15 °C a 85 °C | < 40% | < 22% |
| Bateria | −5 °C a 55 °C | < 28% | < 14% |
| Habitat | 17 °C a 27 °C | < 35% | < 18% |
| Comunicação | −10 °C a 50 °C | < 30% | < 14% |
| Controle Térmico | −10 °C a 60 °C | < 30% | < 18% |

---

## Integrantes

Kayo Henderson

## RM's
Rm: 570706

---

## Links

- **Repositório GitHub:**: https://github.com/kayoxshenderson-droid/global_solution_andre1.git
- **Vídeo YouTube:** _(preencher)_
