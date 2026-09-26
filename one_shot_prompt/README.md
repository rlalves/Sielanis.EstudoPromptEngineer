# Escala mensal de enfermagem em JSON

O arquivo `prompt.txt` contém o prompt para gerar uma escala de enfermagem para
outubro de 2026, com a equipe, regras de cobertura e estrutura JSON fornecidas.
O script envia esse prompt à API Gemini, solicita saída JSON e valida a
estrutura, os tipos dos campos, as datas e os horários antes de imprimir o
resultado.

## Configurar a API Gemini

Configure a chave de API como variável de ambiente no PowerShell:

```powershell
$env:GEMINI_API_KEY = "sua-chave-de-api"
```

Não coloque a chave no código nem a envie para o Git. O modelo padrão é
`gemini-3.8-flash`, configurável pela variável de ambiente `GEMINI_MODEL` para
qualquer modelo habilitado para sua chave.

## Executar

Na raiz do repositório:

```powershell
python .\one_shot_prompt\main.py
```

O programa imprime somente o JSON validado. Para alterar a equipe, as regras ou
o mês, edite `prompt.txt`.

**Atenção:** o quinto profissional está identificado no prompt como
`"Enfermeiro "` (com espaço ao final), conforme o texto recebido. Corrija esse
nome em `prompt.txt` antes de usar, se o espaço for um erro de digitação. Além
disso, a validação do script verifica formato e estrutura, mas não comprova a
correção matemática da escala nem conformidade com regras trabalhistas ou
institucionais. Revise cuidadosamente o resultado antes de qualquer uso.

O uso da API está sujeito às cotas e condições da conta Gemini.
