import os
import sys
import json
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

try:
    from scripts.input_handler import extract_text
    from scripts.calculadora_notas import calcular_nota_final
    from scripts.tracing import get_logger, dump_json_log
    from scripts.llm_avaliador import avaliar_redacao
except ImportError:
    from input_handler import extract_text
    from calculadora_notas import calcular_nota_final
    from tracing import get_logger, dump_json_log
    from llm_avaliador import avaliar_redacao


def gerar_relatorio_md(
    file_path: str,
    tema: str,
    texto_extraido: str,
    contagem_linhas: int,
    motivo_anulacao: str | None,
    notas_ia: dict,
    resultado_calculo: dict,
    trace_steps: list,
    comentarios_llm: dict | None = None,
    pontos_interesse: dict | None = None,
    output_dir: str = None,
) -> str:
    """
    Gera um relatório completo de correção em formato Markdown (.md).

    :param file_path: Caminho do arquivo original.
    :param tema: Tema da redação.
    :param texto_extraido: Texto extraído do arquivo.
    :param contagem_linhas: Quantidade de linhas válidas.
    :param motivo_anulacao: Motivo de anulação, se houver.
    :param notas_ia: Dicionário com notas por competência atribuídas pela IA.
    :param resultado_calculo: Resultado da calculadora de notas.
    :param trace_steps: Lista de etapas registradas pelo rastreio.
    :param output_dir: Diretório de saída. Se None, usa ./relatorios.
    :return: Caminho absoluto do arquivo .md gerado.
    """
    if output_dir is None:
        output_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "relatorios")
        )
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_base = os.path.splitext(os.path.basename(file_path))[0]
    md_filename = f"correcao_{nome_base}_{timestamp}.md"
    md_path = os.path.join(output_dir, md_filename)

    # Mapeamento de nomes de competências
    competencias_nomes = {
        "C1": "Domínio da norma culta da língua escrita",
        "C2": "Compreensão da proposta de redação",
        "C3": "Seleção e organização das informações",
        "C4": "Conhecimento dos mecanismos linguísticos",
        "C5": "Elaboração de proposta de intervenção",
    }

    status = resultado_calculo["status"].upper()
    nota_final = resultado_calculo["nota_final"]
    detalhes = resultado_calculo["detalhes"]
    mensagens = resultado_calculo.get("mensagens", [])

    lines = []
    lines.append(f"# 📝 Relatório de Correção de Redação")
    lines.append("")
    lines.append(f"> **Arquivo:** `{os.path.basename(file_path)}`  ")
    lines.append(f"> **Tema:** {tema}  ")
    lines.append(f"> **Data/Hora:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  ")
    lines.append(f"> **Linhas válidas:** {contagem_linhas}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Resultado geral
    lines.append("## 🏆 Resultado Geral")
    lines.append("")
    if status == "ANULADA":
        lines.append(f"> [!CAUTION]")
        lines.append(f"> **Status:** {status}  ")
        lines.append(f"> **Motivo:** {motivo_anulacao}")
    else:
        lines.append(f"| Item | Valor |")
        lines.append(f"|------|-------|")
        lines.append(f"| **Status** | {status} |")
        lines.append(f"| **Nota Final** | **{nota_final}/1000** |")
    lines.append("")

    # Notas por competência
    lines.append("## 📊 Notas por Competência")
    lines.append("")
    lines.append("| Competência | Descrição | Nota |")
    lines.append("|:-----------:|-----------|:----:|")
    for comp, nota in detalhes.items():
        descricao = competencias_nomes.get(comp, comp)
        lines.append(f"| **{comp}** | {descricao} | {nota}/200 |")
    lines.append("")

    # Comentários detalhados por competência
    lines.append("## 💬 Comentários Detalhados por Competência")
    lines.append("")
    for comp, nota in detalhes.items():
        descricao = competencias_nomes.get(comp, comp)
        lines.append(f"### {comp} — {descricao} ({nota}/200)")
        lines.append("")
        if comentarios_llm and comentarios_llm.get(comp):
            lines.append(comentarios_llm[comp])
        else:
            comentario = _gerar_comentario_competencia(comp, nota, motivo_anulacao)
            lines.append(comentario)
        lines.append("")

    if pontos_interesse and pontos_interesse.get("pontos_interesse"):
        lines.append("## 🔎 Pontos de Interesse")
        lines.append("")
        for p in pontos_interesse["pontos_interesse"]:
            tipo = p.get("tipo", "—")
            gravidade = p.get("gravidade", "—")
            trecho = p.get("trecho", "")
            coment = p.get("comentario", "")
            lines.append(f"- **{tipo}** ({gravidade}): \"{trecho}\" — {coment}")
        lines.append("")

    # Observações
    if mensagens:
        lines.append("## ⚠️ Observações")
        lines.append("")
        for msg in mensagens:
            lines.append(f"- {msg}")
        lines.append("")

    # Texto extraído
    lines.append("## 📄 Texto Extraído")
    lines.append("")
    lines.append("<details>")
    lines.append("<summary>Clique para expandir o texto completo</summary>")
    lines.append("")
    lines.append("```")
    lines.append(texto_extraido)
    lines.append("```")
    lines.append("")
    lines.append("</details>")
    lines.append("")

    # Rastreio do processo
    lines.append("## 🔍 Rastreio do Processo")
    lines.append("")
    lines.append("| # | Etapa | Detalhes |")
    lines.append("|:-:|-------|----------|")
    for i, step in enumerate(trace_steps, 1):
        nome = step.get("name", "—")
        detalhes_step = {k: v for k, v in step.items() if k != "name"}
        detalhes_str = ", ".join(f"{k}={v}" for k, v in detalhes_step.items()) or "OK"
        lines.append(f"| {i} | `{nome}` | {detalhes_str} |")
    lines.append("")
    lines.append("---")
    lines.append(f"*Relatório gerado automaticamente pelo Workflow Corretor de Redações.*")

    content = "\n".join(lines)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)

    return md_path


def _gerar_comentario_competencia(comp: str, nota: int, motivo_anulacao: str | None) -> str:
    """
    Gera um comentário descritivo para cada competência com base na faixa de nota.
    Em produção, esse comentário viria da LLM. Aqui geramos comentários simulados.
    """
    if motivo_anulacao:
        return (
            "> [!WARNING]\n"
            "> Redação anulada — competência não avaliada."
        )

    if nota >= 180:
        nivel = "Excelente"
        icone = "✅"
    elif nota >= 120:
        nivel = "Bom"
        icone = "🟡"
    elif nota >= 80:
        nivel = "Regular"
        icone = "🟠"
    else:
        nivel = "Insuficiente"
        icone = "🔴"

    comentarios = {
        "C1": {
            "Excelente": "Demonstra domínio produtivo da modalidade escrita formal, com raros desvios gramaticais.",
            "Bom": "Demonstra bom domínio da modalidade escrita formal, com alguns desvios gramaticais e de convenções da escrita.",
            "Regular": "Demonstra domínio mediano da modalidade escrita formal, com desvios frequentes.",
            "Insuficiente": "Demonstra domínio insuficiente da modalidade escrita formal, com muitos desvios gramaticais.",
        },
        "C2": {
            "Excelente": "Desenvolve o tema por meio de argumentação consistente, com excelente domínio do texto dissertativo-argumentativo.",
            "Bom": "Desenvolve o tema por meio de argumentação consistente, com bom domínio do tipo textual.",
            "Regular": "Desenvolve o tema recorrendo à cópia de trechos dos textos motivadores ou apresenta domínio insuficiente do tipo textual.",
            "Insuficiente": "Fuga ao tema ou não atendimento à estrutura dissertativo-argumentativa.",
        },
        "C3": {
            "Excelente": "Apresenta informações, fatos e opiniões relacionados ao tema, de forma consistente e organizada.",
            "Bom": "Apresenta informações, fatos e opiniões relacionados ao tema, com organização adequada.",
            "Regular": "Apresenta informações e opiniões com pouca organização ou relação superficial com o tema.",
            "Insuficiente": "Apresenta informações, fatos e opiniões pouco relacionados ao tema ou incoerentes.",
        },
        "C4": {
            "Excelente": "Articula bem as partes do texto, com repertório diversificado de recursos coesivos.",
            "Bom": "Articula as partes do texto com poucas inadequações, com repertório adequado de recursos coesivos.",
            "Regular": "Articula as partes do texto de forma insuficiente, com repertório limitado de recursos coesivos.",
            "Insuficiente": "Não articula as informações ou articula as partes do texto de forma precária.",
        },
        "C5": {
            "Excelente": "Elabora proposta de intervenção detalhada, relacionada ao tema e articulada à discussão desenvolvida no texto.",
            "Bom": "Elabora proposta de intervenção relacionada ao tema, com boa articulação com a discussão.",
            "Regular": "Elabora proposta de intervenção relacionada ao tema de forma insuficiente.",
            "Insuficiente": "Não apresenta proposta de intervenção ou apresenta proposta não relacionada ao tema.",
        },
    }

    texto = comentarios.get(comp, {}).get(nivel, "Comentário não disponível para esta competência.")
    return f"{icone} **Nível: {nivel}** — {texto}"


def processar_redacao(file_path: str, tema: str = "Tema Geral") -> None:
    """
    Executes the ingestion and preprocessing workflow, extracting text and simulating
    the validation/calculation stage.
    """
    print(f"[*] Iniciando workflow para o arquivo: {file_path}")
    print(f"[*] Tema cadastrado: {tema}")
    logger = get_logger()
    trace_data = {"run_id": logger.name.split('_')[-1], "steps": []}

    # 1. Extração de Texto (PDF/OCR/Texto Plano)
    try:
        texto_extraido = extract_text(file_path)
        print("[+] Texto extraído com sucesso!")
        print("-" * 50)
        print(texto_extraido)
        print("-" * 50)
        logger.debug("Texto extraído com sucesso")
        trace_data["steps"].append({"name": "extract_text", "status": "success"})
    except Exception as e:
        print(f"[-] Erro na extração de texto: {e}", file=sys.stderr)
        logger.error(f"Falha na extração: {e}")
        trace_data["steps"].append({"name": "extract_text", "status": "error", "detail": str(e)})
        sys.exit(1)

    # 2. Pré-validação de regras de negócio (ex: menos de 7 linhas)
    linhas = [l.strip() for l in texto_extraido.split('\n') if l.strip()]
    contagem_linhas = len(linhas)
    print(f"[*] Estatísticas: {contagem_linhas} linhas válidas detectadas.")
    logger.debug(f"Contagem de linhas: {contagem_linhas}")
    trace_data["steps"].append({"name": "pre_validation", "lines": contagem_linhas})

    motivo_anulacao = None
    if contagem_linhas < 7:
        motivo_anulacao = f"Extensão de apenas {contagem_linhas} linhas manuscritas (Texto insuficiente)"
        print(f"[!] Alerta de anulação automática: {motivo_anulacao}")
        trace_data["steps"].append({"name": "anulacao_check", "status": "anulada", "motivo": motivo_anulacao})

    pontos_interesse = None
    comentarios_llm = None

    if motivo_anulacao:
        notas_ia = {"C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 0}
    else:
        redacao_id = os.path.splitext(os.path.basename(file_path))[0]
        avaliacao = avaliar_redacao(texto_extraido, tema, redacao_id=redacao_id)
        notas_ia = avaliacao["notas"]
        comentarios_llm = avaliacao.get("comentarios") or {}
        pontos_interesse = avaliacao.get("pontos")
        modo = avaliacao.get("modo", "desconhecido")

        if avaliacao.get("motivo_anulacao") and not motivo_anulacao:
            motivo_anulacao = avaliacao["motivo_anulacao"]
            print(f"[!] Anulação indicada pela IA: {motivo_anulacao}")
            trace_data["steps"].append(
                {"name": "anulacao_llm", "status": "anulada", "motivo": motivo_anulacao}
            )

        n_pontos = len((pontos_interesse or {}).get("pontos_interesse", []))
        schema_warnings = (pontos_interesse or {}).get("_schema_warnings", [])
        logger.debug("Avaliação LLM concluída (modo=%s)", modo)
        step_extract = {
            "name": "llm_extraction",
            "modo": modo,
            "pontos_count": n_pontos,
            "schema_valid": len(schema_warnings) == 0,
        }
        if schema_warnings:
            step_extract["schema_warnings"] = len(schema_warnings)
        trace_data["steps"].append(step_extract)
        trace_data["steps"].append({
            "name": "llm_evaluation",
            "modo": modo,
            "notas": notas_ia,
        })

    # 4. Cálculo e Validação Determinística via Tool Calling (calculadora_notas)
    print("[*] Executando calculadora de notas...")
    resultado_calculo_json = calcular_nota_final(notas_ia, motivo_anulacao=motivo_anulacao)
    logger.debug("Cálculo de notas concluído")
    trace_data["steps"].append({"name": "score_calculation", "status": "completed"})
    resultado_calculo = json.loads(resultado_calculo_json)

    # 5. Apresentação do Relatório Consolidado (console)
    print("\n" + "=" * 50)
    print("           RELATÓRIO CONSOLIDADO DE CORREÇÃO")
    print("=" * 50)
    print(f"Status da Correção: {resultado_calculo['status'].upper()}")
    print(f"Nota Final: {resultado_calculo['nota_final']}/1000")
    print("\nNotas por Competência:")
    for comp, nota in resultado_calculo['detalhes'].items():
        print(f"  - {comp}: {nota} pontos")

    if resultado_calculo['mensagens']:
        print("\nObservações:")
        for msg in resultado_calculo['mensagens']:
            print(f"  - {msg}")
    print("=" * 50)

    # 6. Geração do relatório em Markdown (.md)
    md_path = gerar_relatorio_md(
        file_path=file_path,
        tema=tema,
        texto_extraido=texto_extraido,
        contagem_linhas=contagem_linhas,
        motivo_anulacao=motivo_anulacao,
        notas_ia=notas_ia,
        resultado_calculo=resultado_calculo,
        trace_steps=trace_data["steps"],
        comentarios_llm=comentarios_llm,
        pontos_interesse=pontos_interesse,
    )
    print(f"\n[+] Relatório Markdown salvo em: {md_path}")
    logger.info(f"Relatório Markdown gerado: {md_path}")
    trace_data["steps"].append({"name": "report_generation", "status": "completed", "path": md_path})

    # 7. Salvar trace JSON
    json_path = dump_json_log(trace_data, logger.name.split('_')[-1])
    logger.info(f"Process trace saved to {json_path}")


if __name__ == "__main__":
    # Ensure stdout/stderr use UTF-8 to prevent UnicodeEncodeError on Windows terminals
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

    if len(sys.argv) < 2:
        print("Uso: python -m scripts.process_redacao <caminho_do_arquivo> [tema]")
        sys.exit(1)

    caminho = sys.argv[1]
    tema_proposto = sys.argv[2] if len(sys.argv) > 2 else "A importância da leitura na era digital"
    processar_redacao(caminho, tema_proposto)
