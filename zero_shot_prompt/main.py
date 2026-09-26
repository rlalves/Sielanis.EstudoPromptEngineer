"""Classifica o sentimento de um texto usando a API Gemini."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


def build_prompt(text: str) -> str:
    """Cria uma instrução sem exemplos para classificar o texto informado."""
    return f"""Classifique o sentimento predominante do texto a seguir.

Use somente uma destas categorias: positivo, negativo ou neutro.
Responda no formato:
Sentimento: <categoria>
Justificativa: <explicação breve>

Texto:
{text}"""


def query_gemini(prompt: str) -> str:
    """Envia o prompt à API Gemini e retorna o texto gerado."""
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
            {"contents": [{"parts": [{"text": prompt}]}]}
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


def main() -> None:
    print("Digite o texto para analisar. Encerre com uma linha vazia:")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line.strip():
            break
        lines.append(line)

    text = "\n".join(lines).strip()
    if not text:
        raise SystemExit("O texto não pode ficar vazio.")

    try:
        answer = query_gemini(build_prompt(text))
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
    except (TimeoutError, RuntimeError, json.JSONDecodeError) as error:
        raise SystemExit(f"Falha ao consultar a API Gemini: {error}") from error

    print("\nResultado:\n")
    print(answer)


if __name__ == "__main__":
    main()
