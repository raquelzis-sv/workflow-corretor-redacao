# 📝 Workflow de Correção de Redações

Sistema automatizado de avaliação de redações inspirado no modelo **ENEM**. O fluxo integra chamadas a Modelos de Linguagem (LLMs) com *tool calling* para validação determinística, aceitando entradas em **PDF**, **imagem (OCR)** e **texto plano**.

---

## 📂 Estrutura do Projeto

```text
.
├── README.md                            # Visão geral do projeto (este arquivo)
├── prd.md                               # Documento de Requisitos de Produto
├── requirements.txt                     # Dependências Python
├── cartilha_enem_2025.pdf               # Material de referência ENEM
│
├── contracts/
│   └── contrato.yaml                    # Competências e níveis de avaliação
│
├── schemas/
│   └── pontos_interesse.json            # Schema de extração de desvios e acertos
│
├── docs/
│   └── workflow.md                      # Documentação do pipeline e arquitetura
│
├── scripts/
│   ├── process_redacao.py               # 🚀 Orquestrador principal do workflow
│   ├── input_handler.py                 # Roteador de entrada (PDF / Imagem / Texto)
│   ├── pdf_extractor.py                 # Extração de texto via pdfplumber
│   ├── ocr_engine.py                    # Digitalização de imagens via Tesseract OCR
│   ├── calculadora_notas.py             # Cálculo e validação determinística de notas
│   └── tracing.py                       # Rastreio e logging do processo
│
├── exemplos/                            # Arquivos de exemplo para testes
│   ├── redacao_nota_alta.txt            # Redação de exemplo (texto plano)
│   ├── redacao_curta.txt                # Redação curta (testa anulação automática)
│   ├── redacao_2.JPG                    # Redação manuscrita (testa OCR)
│   ├── redacao_3.pdf                    # Redação em PDF digital
│   ├── tema.txt                         # Tema de redação de exemplo
│   └── tema_2.txt                       # Tema de redação de exemplo 2
│
├── relatorios/                          # 📄 Relatórios .md gerados automaticamente
├── logs/                                # 🔍 Logs de rastreio (.log e .json)
│
└── tests_workflow/
    └── test_pipeline.py                 # Testes unitários do pipeline
```

---

## 🚀 Como Funciona

O workflow segue **7 etapas** sequenciais:

| Etapa | Descrição | Módulo |
|:-----:|-----------|--------|
| 1 | **Ingestão** — Recebe o arquivo (PDF, imagem ou texto) | `input_handler.py` |
| 2 | **Extração de Texto** — Converte o conteúdo para texto puro | `pdf_extractor.py` / `ocr_engine.py` |
| 3 | **Pré-validação** — Verifica regras de negócio (ex: mínimo de 7 linhas) | `process_redacao.py` |
| 4 | **Análise da IA** — Identifica Pontos de Interesse e avalia competências | LLM + `contrato.yaml` |
| 5 | **Cálculo de Notas** — Soma, valida e aplica regras de anulação | `calculadora_notas.py` |
| 6 | **Relatório Markdown** — Gera arquivo `.md` com resultado completo | `process_redacao.py` |
| 7 | **Rastreio do Processo** — Salva log e trace JSON de cada etapa | `tracing.py` |

### Formatos de Entrada Suportados

| Formato | Extensões | Método de Extração |
|---------|-----------|-------------------|
| PDF digital | `.pdf` | `pdfplumber` |
| Imagem / Foto | `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.webp` | Tesseract OCR + OpenCV |
| Texto plano | `.txt`, `.md` | Leitura direta UTF-8 |

### Saídas Geradas

| Saída | Local | Descrição |
|-------|-------|-----------|
| Relatório `.md` | `relatorios/` | Relatório completo com notas, comentários por competência e rastreio |
| Trace `.json` | `logs/` | Dados estruturados de cada etapa do pipeline |
| Log `.log` | `logs/` | Log textual detalhado da execução |

---

## 🛠️ Instalação

### 1. Dependências Python

```bash
pip install -r requirements.txt
```

### 2. Tesseract OCR (necessário apenas para entrada por imagem)

| Sistema | Comando |
|---------|---------|
| **Windows** | Baixe o instalador em [Tesseract OCR para Windows](https://github.com/UB-Mannheim/tesseract/wiki). O script detecta o caminho automaticamente. |
| **macOS** | `brew install tesseract tesseract-lang` |
| **Linux** | `sudo apt-get install tesseract-ocr tesseract-ocr-por` |

> **Dica:** Durante a instalação no Windows, marque o pacote de idioma **Português** para melhor precisão no OCR.

---

## 💻 Como Executar

### Comando principal

```bash
python -m scripts.process_redacao <caminho_do_arquivo> "[Tema da Redação]"
```

### Exemplos

```bash
# Redação em texto plano
python -m scripts.process_redacao exemplos/redacao_nota_alta.txt "Desafios para a formação educacional de surdos no Brasil"

# Redação em PDF
python -m scripts.process_redacao exemplos/redacao_3.pdf "Invisibilidade e registro civil"

# Redação manuscrita (imagem)
python -m scripts.process_redacao exemplos/redacao_2.JPG "A importância da leitura na era digital"

# Redação curta (testa anulação automática)
python -m scripts.process_redacao exemplos/redacao_curta.txt
```

### Executar testes

```bash
pytest -q
```

---

## 📄 Exemplo de Relatório Gerado

O workflow gera automaticamente um relatório `.md` na pasta `relatorios/` contendo:

- **🏆 Resultado Geral** — Status e nota final
- **📊 Notas por Competência** — Tabela C1 a C5 com descrições
- **💬 Comentários Detalhados** — Feedback por competência com nível (Excelente / Bom / Regular / Insuficiente)
- **📄 Texto Extraído** — Conteúdo completo da redação
- **🔍 Rastreio do Processo** — Tabela com cada etapa do pipeline e detalhes

---

## 📚 Documentação Complementar

| Documento | Descrição |
|-----------|-----------|
| [prd.md](prd.md) | Requisitos de Produto — objetivos, personas, requisitos funcionais e não-funcionais |
| [docs/workflow.md](docs/workflow.md) | Arquitetura do pipeline, diagramas de fluxo e prompts |
| [contracts/contrato.yaml](contracts/contrato.yaml) | Definição das 5 competências e seus níveis de avaliação |
| [schemas/pontos_interesse.json](schemas/pontos_interesse.json) | Schema JSON para extração de desvios e acertos |
