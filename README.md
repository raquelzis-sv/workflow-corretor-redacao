# 📝 Workflow de Correção de Redações

Sistema automatizado de avaliação de redações inspirado no modelo **ENEM**. O fluxo integra chamadas a Modelos de Linguagem (LLMs) com *tool calling* para validação determinística, aceitando entradas em **PDF**, **imagem (OCR)** e **texto plano**.

---

## 📂 Estrutura do Projeto

```text
.
├── README.md                            # Visão geral do projeto (este arquivo)
├── prd.md                               # Documento de Requisitos de Produto
├── requirements.txt                     # Dependências Python
├── .env.example                         # Variáveis Ollama (copiar para .env)
├── cartilha_enem_2025.pdf               # Material de referência ENEM (opcional)
│
├── contracts/
│   └── contrato.yaml                    # Competências e níveis de avaliação
│
├── schemas/
│   └── pontos_interesse.json            # Schema de extração de desvios e acertos
│
├── docs/
│   └── workflow.md                      # Documentação do pipeline e arquitetura
│   └── workflow.yaml                    # Workflow estruturado (etapas, I/O, tools, POP)
│
├── scripts/
│   ├── process_redacao.py               # 🚀 Orquestrador principal do workflow
│   ├── input_handler.py                 # Roteador de entrada (PDF / Imagem / Texto)
│   ├── pdf_extractor.py                 # Extração de texto via pdfplumber
│   ├── ocr_engine.py                    # Digitalização de imagens via Tesseract OCR
│   ├── calculadora_notas.py             # Cálculo e validação determinística de notas
│   ├── llm_avaliador.py                 # Avaliação via Ollama (Llama 3.2)
│   └── tracing.py                       # Rastreio e logging do processo
│
├── exemplos/                            # Arquivos de exemplo para testes
│   ├── redacao_nota_alta.txt            # Redação completa (texto plano)
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

O sistema possui duas formas principais de orquestração:

### 1. Workflow Agentic (Recomendado)
O fluxo é gerenciado ativamente por um **Agente de IA** instruído pelo arquivo `.agents/workflows/corretor.md`. Neste modelo, a IA:
1. Faz a leitura inteligente e extração do texto (via tools).
2. Aciona o Ollama (`llm_avaliador.py`) como uma *tool call* para extrair notas e desvios.
3. Aciona a calculadora matemática (`calculadora_notas.py`) como uma *tool call* para consolidar a nota com 100% de precisão lógica.
4. Redige e estrutura o relatório Markdown final.

### 2. Workflow Automático Local
Caso o professor deseje rodar a automação isoladamente no terminal (sem chat), a orquestração é feita em Python:

| Etapa | Descrição | Módulo |
|:-----:|-----------|--------|
| 1 | **Ingestão** — Recebe o arquivo (PDF, imagem ou texto) | `input_handler.py` |
| 2 | **Pré-validação** — Verifica regras de negócio (ex: mínimo de 7 linhas) | `process_redacao.py` |
| 3 | **Análise da IA** — Pontos de interesse + notas por competência | `llm_avaliador.py` (Ollama / `llama3.2`) + `contrato.yaml` |
| 4 | **Cálculo de Notas** — Soma, valida e aplica regras de anulação | `calculadora_notas.py` |
| 5 | **Relatório Markdown** — Gera arquivo `.md` com resultado completo | `process_redacao.py` |
| 6 | **Rastreio do Processo** — Salva log e trace JSON de cada etapa | `tracing.py` |

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

### 2. Ollama + Llama 3.2 (avaliação por IA)

| Passo | Comando / ação |
|-------|----------------|
| Instalar Ollama | [https://ollama.com](https://ollama.com) (já instalado no Windows, se `ollama` funcionar no terminal) |
| Baixar o modelo | `ollama pull llama3.2` |
| Variáveis (opcional) | Copie `.env.example` para `.env` ou exporte `OLLAMA_MODEL=llama3.2` |

O servidor Ollama deve estar em execução. Sem ele, o pipeline usa **modo simulado** (notas fixas) e avisa no console.

Para desativar a IA local: `OLLAMA_DISABLED=1`.

### 3. Tesseract OCR (necessário apenas para entrada por imagem)

| Sistema | Comando |
|---------|---------|
| **Windows** | Baixe o instalador em [Tesseract OCR para Windows](https://github.com/UB-Mannheim/tesseract/wiki). O script detecta o caminho automaticamente. |
| **macOS** | `brew install tesseract tesseract-lang` |
| **Linux** | `sudo apt-get install tesseract-ocr tesseract-ocr-por` |

> **Dica:** Durante a instalação no Windows, marque o pacote de idioma **Português** para melhor precisão no OCR.

---

## 💻 Como Executar

Você pode executar o workflow localmente através do novo comando `corretor` (batch wrapper) ou via Python.

### 1. Via Comando Principal (Batch Wrapper)

```bash
corretor <caminho_do_arquivo> "<tema_ou_caminho_do_tema>"
```

### 2. Via Python

```bash
python -m scripts.corretor_cli <caminho_do_arquivo> "<tema>"
```

### Exemplos Práticos no Terminal

```bash
# Redação em texto plano
corretor exemplos/redacao_nota_alta.txt exemplos/tema.txt

# Redação em PDF
corretor exemplos/redacao_3.pdf exemplos/tema_2.txt

# Redação manuscrita (imagem — requer Tesseract)
corretor exemplos/redacao_2.JPG exemplos/tema_2.txt

# Redação curta (testa anulação automática)
corretor exemplos/redacao_curta.txt
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
| [prd.md](prd.md) | Requisitos de Produto — objetivos, personas e requisitos |
| [.agents/workflows/corretor.md](.agents/workflows/corretor.md) | **Workflow Agentic** — Regras de orquestração para a IA |
| [contracts/contrato.yaml](contracts/contrato.yaml) | Definição das 5 competências e seus níveis de avaliação |
| [schemas/pontos_interesse.json](schemas/pontos_interesse.json) | Schema JSON para extração de desvios e acertos |
