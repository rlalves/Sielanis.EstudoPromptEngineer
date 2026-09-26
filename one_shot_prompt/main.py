"""Gera uma escala mensal em JSON usando a API Gemini."""

import json
import os
import re
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

PROMPT_PATH = Path(__file__).with_name("prompt.txt")
EXPECTED_MONTH = "2026-10"


def load_prompt() -> str:
    """Carrega o prompt mensal mantido ao lado deste script."""
    prompt = PROMPT_PATH.read_text(encoding="utf-8").strip()
    if not prompt:
        raise RuntimeError(f"O prompt está vazio: {PROMPT_PATH}")
    return prompt


def query_gemini(prompt: str) -> str:
    """Envia o prompt à API Gemini solicitando uma resposta JSON."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "A variável de ambiente GEMINI_API_KEY não está definida."
        )

    model = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{quote(model, safe='')}:generateContent"
    )
    request = Request(
        endpoint,
        data=json.dumps(
            {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"},
            }
        ).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    with urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))

    if not isinstance(result, dict):
        raise RuntimeError("A API Gemini retornou uma resposta inválida.")

    candidates = result.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise RuntimeError("A API Gemini não retornou candidatos de resposta.")

    candidate = candidates[0]
    if not isinstance(candidate, dict):
        raise RuntimeError("A API Gemini retornou um candidato inválido.")

    content = candidate.get("content", {})
    parts = content.get("parts", []) if isinstance(content, dict) else []
    answer = "\n".join(
        part["text"]
        for part in parts
        if isinstance(part, dict) and isinstance(part.get("text"), str)
    ).strip()
    if not answer:
        raise RuntimeError("A API Gemini retornou uma resposta vazia ou inválida.")
    return answer


def require_object(value: object, keys: set[str], label: str) -> dict:
    """Confere se um valor é um objeto com exatamente as chaves esperadas."""
    if not isinstance(value, dict) or set(value) != keys:
        raise RuntimeError(f"{label} deve ser um objeto com as chaves esperadas.")
    return value


def require_string(value: object, label: str) -> None:
    if not isinstance(value, str):
        raise RuntimeError(f"{label} deve ser um texto.")


def require_number(value: object, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuntimeError(f"{label} deve ser um número.")


def validate_date(value: object, label: str) -> None:
    require_string(value, label)
    try:
        date.fromisoformat(value)
    except ValueError as error:
        raise RuntimeError(f"{label} deve usar o formato YYYY-MM-DD.") from error
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise RuntimeError(f"{label} deve usar o formato YYYY-MM-DD.")


def validate_time(value: object, label: str) -> None:
    require_string(value, label)
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value):
        raise RuntimeError(f"{label} deve usar o formato HH:MM.")


def validate_json_answer(answer: str) -> dict:
    """Valida o JSON e a estrutura e os tipos exigidos pelo prompt."""
    try:
        result = json.loads(answer)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"A resposta do modelo não é JSON válido: {error}"
        ) from error

    top = require_object(
        result,
        {
            "mes",
            "premissas",
            "analise",
            "escala",
            "resumo_profissionais",
            "periodos_descobertos",
            "necessidade_de_horas_adicionais",
        },
        "A resposta",
    )
    if top["mes"] != EXPECTED_MONTH:
        raise RuntimeError(f"O campo mes deve ser {EXPECTED_MONTH}.")

    if not isinstance(top["premissas"], list):
        raise RuntimeError("premissas deve ser uma lista.")
    for premise in top["premissas"]:
        require_string(premise, "Cada premissa")

    analysis = require_object(
        top["analise"],
        {
            "horas_cobertura_por_dia",
            "horas_cobertura_por_semana",
            "horas_disponiveis_por_semana",
            "deficit_ou_excedente_semanal",
            "cobertura_integral_possivel",
            "horas_adicionais_necessarias_por_semana",
        },
        "analise",
    )
    for key in (
        "horas_cobertura_por_dia",
        "horas_cobertura_por_semana",
        "horas_disponiveis_por_semana",
        "deficit_ou_excedente_semanal",
        "horas_adicionais_necessarias_por_semana",
    ):
        require_number(analysis[key], f"analise.{key}")
    if not isinstance(analysis["cobertura_integral_possivel"], bool):
        raise RuntimeError("analise.cobertura_integral_possivel deve ser booleano.")

    if not isinstance(top["escala"], list):
        raise RuntimeError("escala deve ser uma lista.")
    schedule_keys = {"data", "dia_semana", "profissionais", "cobertura"}
    professional_keys = {
        "nome",
        "posicao",
        "entrada",
        "saida",
        "horas_trabalhadas",
    }
    coverage_keys = {
        "triagem",
        "medicacao",
        "atendimento",
        "cobertura_completa",
    }
    for day_index, schedule_day in enumerate(top["escala"]):
        label = f"escala[{day_index}]"
        day = require_object(schedule_day, schedule_keys, label)
        validate_date(day["data"], f"{label}.data")
        require_string(day["dia_semana"], f"{label}.dia_semana")
        if not isinstance(day["profissionais"], list):
            raise RuntimeError(f"{label}.profissionais deve ser uma lista.")
        for person_index, professional in enumerate(day["profissionais"]):
            person_label = f"{label}.profissionais[{person_index}]"
            person = require_object(professional, professional_keys, person_label)
            for key in ("nome", "posicao"):
                require_string(person[key], f"{person_label}.{key}")
            validate_time(person["entrada"], f"{person_label}.entrada")
            validate_time(person["saida"], f"{person_label}.saida")
            require_number(
                person["horas_trabalhadas"],
                f"{person_label}.horas_trabalhadas",
            )

        coverage = require_object(day["cobertura"], coverage_keys, f"{label}.cobertura")
        for key in coverage_keys:
            if not isinstance(coverage[key], bool):
                raise RuntimeError(f"{label}.cobertura.{key} deve ser booleano.")
        if coverage["cobertura_completa"] != all(
            coverage[key] for key in ("triagem", "medicacao", "atendimento")
        ):
            raise RuntimeError(
                f"{label}.cobertura.cobertura_completa não corresponde "
                "às posições cobertas."
            )

    if not isinstance(top["resumo_profissionais"], list):
        raise RuntimeError("resumo_profissionais deve ser uma lista.")
    summary_keys = {
        "nome",
        "jornada_semanal",
        "saldo_inicial_banco_horas",
        "horas_escaladas",
        "horas_compensadas",
        "saldo_final_banco_horas",
    }
    for index, summary in enumerate(top["resumo_profissionais"]):
        label = f"resumo_profissionais[{index}]"
        person = require_object(summary, summary_keys, label)
        require_string(person["nome"], f"{label}.nome")
        for key in summary_keys - {"nome"}:
            require_number(person[key], f"{label}.{key}")

    if not isinstance(top["periodos_descobertos"], list):
        raise RuntimeError("periodos_descobertos deve ser uma lista.")
    uncovered_keys = {"data", "inicio", "fim", "posicao", "motivo"}
    for index, uncovered in enumerate(top["periodos_descobertos"]):
        label = f"periodos_descobertos[{index}]"
        period = require_object(uncovered, uncovered_keys, label)
        validate_date(period["data"], f"{label}.data")
        validate_time(period["inicio"], f"{label}.inicio")
        validate_time(period["fim"], f"{label}.fim")
        require_string(period["posicao"], f"{label}.posicao")
        require_string(period["motivo"], f"{label}.motivo")

    additional = require_object(
        top["necessidade_de_horas_adicionais"],
        {"necessario", "horas_por_semana", "observacao"},
        "necessidade_de_horas_adicionais",
    )
    if not isinstance(additional["necessario"], bool):
        raise RuntimeError(
            "necessidade_de_horas_adicionais.necessario deve ser booleano."
        )
    require_number(
        additional["horas_por_semana"],
        "necessidade_de_horas_adicionais.horas_por_semana",
    )
    require_string(additional["observacao"], "necessidade_de_horas_adicionais.observacao")

    return top


def main() -> None:
    try:
        result = validate_json_answer(query_gemini(load_prompt()))
    except HTTPError as error:
        details = error.read().decode("utf-8", errors="replace").strip()
        message = f"Erro HTTP da API Gemini ({error.code})."
        if details:
            message = f"{message} {details}"
        raise SystemExit(message) from error
    except URLError as error:
        raise SystemExit(
            "Não foi possível conectar à API Gemini. Verifique sua conexão "
            "com a internet."
        ) from error
    except (OSError, TimeoutError, RuntimeError, json.JSONDecodeError) as error:
        raise SystemExit(f"Falha ao gerar a escala: {error}") from error

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
