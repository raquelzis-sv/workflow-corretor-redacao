"""
Avaliação de redações via Ollama (Llama 3.2) — extração de pontos e notas ENEM.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import yaml

try:
    from scripts.calculadora_notas import calcular_nota_final
    from scripts.validacao_schema import validar_pontos_interesse
except ImportError:
    from calculadora_notas import calcular_nota_final
    from validacao_schema import validar_pontos_interesse

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONTRATO = ROOT_DIR / "contracts" / "contrato.yaml"
NOTAS_VALIDAS = [0, 40, 80, 120, 160, 200]
COMPETENCIAS = ["C1", "C2", "C3", "C4", "C5"]

PONTOS_TIPOS = [
    "desvio_ortografico",
    "desvio_sintatico",
    "falha_coesao",
    "fuga_tema",
    "argumento_excelente",
    "repertorio_legitimado",
]
GRAVIDADES = ["positiva", "leve", "moderada", "grave", "anulacao"]


def _env_model() -> str:
    return os.getenv("OLLAMA_MODEL", "llama3.2")


def _env_host() -> str:
    return os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")


def _llm_habilitada() -> bool:
    if os.getenv("OLLAMA_DISABLED", "").lower() in ("1", "true", "yes"):
        return False
    return True


def carregar_contrato(caminho: str | Path | None = None) -> dict:
    path = Path(caminho) if caminho else DEFAULT_CONTRATO
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def resumo_contrato_para_prompt(contrato: dict) -> str:
    """Versão compacta do contrato para caber no contexto do modelo."""
    linhas = [
        "Competências ENEM — use APENAS estas notas por competência: 0, 40, 80, 120, 160, 200.",
        f"Nota máxima total: {contrato.get('regras_gerais', {}).get('nota_maxima', 1000)}.",
    ]
    for comp in contrato.get("competencias", []):
        cid = comp.get("id", "")
        nome = comp.get("nome", "")
        niveis = ", ".join(str(n["nota"]) for n in comp.get("niveis", []))
        linhas.append(f"- {cid}: {nome} | notas permitidas: {niveis}")
    anulacao = contrato.get("regras_gerais", {}).get("anulacao", [])
    if anulacao:
        linhas.append("Motivos de anulação (nota 0 em todas): " + "; ".join(anulacao[:6]))
    return "\n".join(linhas)


def _parse_json_resposta(texto: str) -> dict:
    texto = texto.strip()
    if texto.startswith("```"):
        texto = re.sub(r"^```(?:json)?\s*", "", texto)
        texto = re.sub(r"\s*```$", "", texto)
    return json.loads(texto)


def _chat_json(system: str, user: str, model: str, host: str) -> dict:
    import ollama

    client = ollama.Client(host=host)
    response = client.chat(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        format="json",
        options={"temperature": 0.2},
    )
    content = response["message"]["content"]
    return _parse_json_resposta(content)


def ollama_disponivel(host: str | None = None) -> bool:
    if not _llm_habilitada():
        return False
    try:
        import ollama

        client = ollama.Client(host=host or _env_host())
        client.list()
        return True
    except Exception:
        return False


def extrair_pontos_interesse(
    texto: str,
    tema: str,
    redacao_id: str = "local",
    model: str | None = None,
    host: str | None = None,
) -> dict:
    model = model or _env_model()
    host = host or _env_host()

    system = (
        "Você é corretor ENEM. Responda SOMENTE com JSON válido, sem markdown.\n"
        "Schema obrigatório:\n"
        '{"redacao_id": "string", "pontos_interesse": ['
        '{"tipo": "desvio_ortografico|desvio_sintatico|falha_coesao|fuga_tema|'
        'argumento_excelente|repertorio_legitimado", '
        '"trecho": "citação curta do texto", '
        '"comentario": "explicação pedagógica", '
        '"gravidade": "positiva|leve|moderada|grave|anulacao"}]}\n'
        "Liste entre 3 e 12 pontos relevantes (erros e acertos)."
    )
    user = f'redacao_id: "{redacao_id}"\nTema: {tema}\n\nRedação:\n{texto}'
    data = _chat_json(system, user, model, host)

    if "redacao_id" not in data:
        data["redacao_id"] = redacao_id
    if "pontos_interesse" not in data:
        data["pontos_interesse"] = []

    for p in data["pontos_interesse"]:
        if p.get("tipo") not in PONTOS_TIPOS:
            p["tipo"] = "desvio_ortografico"
        if p.get("gravidade") not in GRAVIDADES:
            p["gravidade"] = "moderada"

    ok, erros = validar_pontos_interesse(data)
    if not ok:
        data["_schema_warnings"] = erros

    return data


def avaliar_competencias(
    texto: str,
    tema: str,
    pontos: dict,
    contrato: dict,
    model: str | None = None,
    host: str | None = None,
    erro_validacao: str | None = None,
) -> dict:
    model = model or _env_model()
    host = host or _env_host()
    resumo = resumo_contrato_para_prompt(contrato)

    system = (
        "Você é corretor oficial ENEM. Responda SOMENTE com JSON válido.\n"
        f"{resumo}\n\n"
        "Schema de resposta:\n"
        '{"notas": {"C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 0}, '
        '"comentarios": {"C1": "...", "C2": "...", "C3": "...", "C4": "...", "C5": "..."}, '
        '"motivo_anulacao": null}\n'
        "Regras: notas apenas entre 0,40,80,120,160,200; C2=0 se fuga total ao tema; "
        "se houver fuga total, preencha motivo_anulacao e zere todas as competências; "
        "comentários em português, 1-3 frases por competência; não calcule a soma final."
    )
    if erro_validacao:
        system += f"\n\nCORREÇÃO OBRIGATÓRIA: {erro_validacao}"

    pontos_json = json.dumps(pontos, ensure_ascii=False, indent=2)
    user = (
        f"Tema: {tema}\n\n"
        f"Pontos de interesse já extraídos:\n{pontos_json}\n\n"
        f"Redação:\n{texto}"
    )
    data = _chat_json(system, user, model, host)

    notas = data.get("notas", {})
    comentarios = data.get("comentarios", {})
    motivo = data.get("motivo_anulacao")

    notas_norm = {}
    for c in COMPETENCIAS:
        valor = notas.get(c, 0)
        try:
            valor = int(valor)
        except (TypeError, ValueError):
            valor = 0
        if valor not in NOTAS_VALIDAS:
            valor = max((n for n in NOTAS_VALIDAS if n <= valor), default=0)
            if valor not in NOTAS_VALIDAS:
                valor = 0
        notas_norm[c] = valor

    if motivo:
        notas_norm = {c: 0 for c in COMPETENCIAS}

    comentarios_norm = {c: str(comentarios.get(c, "")).strip() for c in COMPETENCIAS}

    return {
        "notas": notas_norm,
        "comentarios": comentarios_norm,
        "motivo_anulacao": motivo if motivo else None,
    }


def _avaliacao_simulada() -> dict:
    return {
        "pontos": {
            "redacao_id": "simulacao",
            "pontos_interesse": [],
        },
        "notas": {"C1": 120, "C2": 160, "C3": 120, "C4": 160, "C5": 120},
        "comentarios": {},
        "motivo_anulacao": None,
        "modo": "simulacao",
    }


def avaliar_redacao(
    texto: str,
    tema: str,
    contrato_path: str | Path | None = None,
    redacao_id: str | None = None,
) -> dict[str, Any]:
    """
    Executa extração + avaliação via Ollama, valida notas com calculadora_notas
    e re-tenta uma vez se as notas forem inválidas.

    Retorna dict com: pontos, notas, comentarios, motivo_anulacao, modo.
    """
    contrato = carregar_contrato(contrato_path)
    rid = redacao_id or "local"
    model = _env_model()
    host = _env_host()

    if not ollama_disponivel(host):
        print(
            "[!] Ollama indisponível ou OLLAMA_DISABLED ativo — usando avaliação simulada.",
            file=__import__("sys").stderr,
        )
        return _avaliacao_simulada()

    print(f"[*] Ollama ({model}): extraindo pontos de interesse...")
    pontos = extrair_pontos_interesse(texto, tema, redacao_id=rid, model=model, host=host)
    if pontos.get("_schema_warnings"):
        print(
            "[!] Avisos de validação do schema pontos_interesse:",
            "; ".join(pontos["_schema_warnings"][:3]),
        )

    erro_validacao = None
    avaliacao = None
    for tentativa in range(2):
        print(
            f"[*] Ollama ({model}): avaliando competências"
            + (f" (retry: {erro_validacao})" if erro_validacao else "")
            + "..."
        )
        avaliacao = avaliar_competencias(
            texto,
            tema,
            pontos,
            contrato,
            model=model,
            host=host,
            erro_validacao=erro_validacao,
        )
        notas = avaliacao["notas"]
        motivo = avaliacao.get("motivo_anulacao")
        resultado_json = calcular_nota_final(notas, motivo_anulacao=motivo)
        resultado = json.loads(resultado_json)

        if resultado.get("status") != "erro":
            break

        erro_validacao = "; ".join(resultado.get("mensagens", []))
        if tentativa == 1:
            print(f"[-] Notas inválidas após retry: {erro_validacao}")

    return {
        "pontos": pontos,
        "notas": avaliacao["notas"],
        "comentarios": avaliacao["comentarios"],
        "motivo_anulacao": avaliacao.get("motivo_anulacao"),
        "modo": "ollama",
    }
