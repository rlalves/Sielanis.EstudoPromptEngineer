# Instruction Prompting

Este exemplo demonstra **Instruction Prompting**: a tarefa é orientada por
instruções explícitas sobre objetivo, fidelidade ao texto, idioma, tamanho e
formato da resposta. O prompt não inclui exemplos de respostas.

## Configurar a API Gemini

Configure a chave de API como variável de ambiente no PowerShell:

```powershell
$env:GEMINI_API_KEY = "sua-chave-de-api"
```

Não coloque a chave no código nem a envie para o Git. O modelo padrão é
`gemini-3.8-flash`; para usar outro modelo habilitado para sua chave, defina
`GEMINI_MODEL` no mesmo terminal.

## Executar

Na raiz do repositório:

```powershell
python .\instruction_prompting\main.py
```

Digite o texto em uma ou mais linhas e finalize com Enter em uma linha vazia.
O programa envia o texto ao Gemini e exibe a resposta no formato solicitado
pelas instruções do prompt.

O uso está sujeito às cotas e condições da conta Gemini. Consulte o Google AI
Studio para verificar os limites aplicáveis.
