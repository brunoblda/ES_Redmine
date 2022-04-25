# Extrator de Sustentação do REDMINE

A aplicação extrai as tarefas de sustentação do mês escolhido.

Após extração, a aplicação realiza a verificação de cumprimento dos SLAs das tarefas de sustentação, considerando os parametros de baixa, normal e alta (alta, imediata e urgente) prioridade imprimindo-os na tela do terminal e gerando uma arquivo CSV.

O login e senha são as utulizadas para se acessar o Redmine, o sistema não salva nenhuma dessas informações.

## Executável

Para se criar um arquivo executavel, realizar a seguinte procedimento:
```cmd
pyinstaller --onefile --paths .\venv\Lib\site-packages main.py
```
Para ver erros do executável execute o arquivo .exe pelo terminal

## Resultados

Os resultados são escritos na tela do terminal.

Exemplo:

> Verificação da Tarefa:  7543 - SICG
> Compriu o SLA do chamado de prioridade Baixa, executando em 2:35:50

> Verificação da Tarefa:  7537 - SAIP
> Não compriu o SLA do chamado de prioridade Normal, passando em 7:46:05

> Verificação da Tarefa:  7589 - CNART
> A global não atuou na Tarefa

E também são exportados em uma tabela csv.

Exemplo:

|Tarefa|Sistema|Prioridade|SLA|Delta_tempo|Passou|Feriado|
|------|-------|----------|---|-----------|------|-------|
| 7543 | SICG | Baixa | TRUE | 2:35:59 | - | FALSO |
| 7537 | SAIP | Normal | FALSE | 1 day, 12:05:22 | 1 day, 0:05:22 | FALSO |
| 7589 | CNART | Normal | NAO ATUOU | 0:00:00 | - | FALSO |

## Obs:.

Deve-se considerar que o Delta tempo dos SLAs consideram o tempo de 8:00 as 20:00 do dia, resultando em 12:00 de tempo líquido. Assim, valores que informem que o deltaTempo é de 1 day, significam que passou 2 dias (cada dia conta 12h).

Os dias de feriados devem ser informados somente se cairem em dias de semana, caso tenha algum feriado no final de semana por favor não informar estes dia.

Por favor informar os inputs conforme indicado em cada pergunta.

