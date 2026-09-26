# Zero-Shot Prompt

Este exemplo monta um prompt para classificar o sentimento de um texto sem
fornecer exemplos de classificação. A tarefa, as categorias e o formato esperado
estão descritos diretamente na instrução.

## Configurar a API Gemini

Configure a chave de API como variável de ambiente. No PowerShell, para a sessão
atual do terminal:

```powershell
$env:GEMINI_API_KEY = "sua-chave-de-api"
```

Não coloque a chave diretamente no código nem a envie para o Git. O modelo
utilizado por padrão é `gemini-2.5-flash`; ele pode ser alterado com a variável
`GEMINI_MODEL` para outro modelo habilitado para sua chave.

## Executar

Na pasta do repositório, execute:

```powershell
python .\zero_shot_prompt\main.py
```

Digite o texto, inclusive em várias linhas, e finalize com Enter em uma linha
vazia. O programa envia o prompt à API Gemini e exibe a resposta gerada.

Para selecionar outro modelo, defina `GEMINI_MODEL` no PowerShell:

```powershell
$env:GEMINI_MODEL = "gemini-2.5-flash"
python .\zero_shot_prompt\main.py
```

O uso está sujeito à disponibilidade e aos limites de cota gratuitos da API
Gemini associados à sua conta. Consulte o painel do Google AI Studio para
acompanhar a cota aplicável.
