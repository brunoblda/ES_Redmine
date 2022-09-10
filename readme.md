# Extrator de Sustentação do REDMINE

A aplicação extrai as tarefas de sustentação do mês escolhido.

Após extração, a aplicação realiza a verificação de cumprimento dos SLAs das tarefas de sustentação, considerando os parametros de baixa, normal e alta (alta, imediata e urgente) prioridade imprimindo-os na tela do terminal e gerando uma arquivo CSV.

O terminal e o arquivo CSV também trazem as datas de atribuição, data de entrega (homologado) e a data de resolvido.

O login e senha são as utulizadas para se acessar o Redmine, o sistema não salva nenhuma dessas informações.

Os feriados de 2021 e 2022 estão incluídos no sistema devendo apenas adicionar novas datas de feriados caso os mesmos não estejam na lista de feriados apresentada.
Os feriados podem ser classificadas em integrais (o SLA de 12h é retirado do dia inteiro), matutinos (somente são considerados os tempos liquidos das 14:00 às 18h) e vespertinos (somente são considerados os tempos líquidos das 08:00 às 14:00))

2021
* https://www.gov.br/pt-br/noticias/financas-impostos-e-gestao-publica/2021/01/governo-divulga-feriados-e-pontos-facultativos-de-2021

2022
* https://www.gov.br/pt-br/noticias/financas-impostos-e-gestao-publica/2021/12/governo-federal-divulga-calendario-2022-de-feriados-e-pontos-facultativos
* https://www.in.gov.br/en/web/dou/-/portaria-me-n-3.413-de-18-de-abril-de-2022-394165228
* Adicionado os dias de moving do data center (28/01/2022 à 03/02/2022)

Documentação da Api Rest do Redmine:

* https://www.redmine.org/projects/redmine/wiki/rest_api

Usuários da fábrica considerados na contagem do tempo líquido:

> Nomes: leandro, rhoxanna, mauricio, cristiano, romao, gestor fabrica, desenvolvedor fabrica, sabino, michel, henrique, testador fabrica, valter, domingos e vinicius

> Ids: 204, 279, 269, 259, 250, 165, 164, 272, 167, 277, 244, 290, 289 e 292

## Executável

Para se criar um arquivo executavel, realizar a seguinte procedimento:
```cmd
pyinstaller --onefile --paths .\venv\Lib\site-packages main.py
```
Para ver erros do executável execute o arquivo .exe pelo terminal

## Resultados

Os resultados são escritos na tela do terminal.

Exemplo:
```
Verificação da Tarefa:  7422  -  FISCALIS
Data de atribuição:  2021-12-29 12:26:24
Data de entrega:  2022-01-06 11:41:19
Data de resolução:  2022-02-14 16:46:40
Compriu o SLA do chamado de prioridade Normal, executando em 14:11:33
```
```
Verificação da Tarefa:  7471  -  SICG
Atuou em feriados
Data de atribuição:  2022-02-03 14:35:44
Data de entrega:  2022-02-08 19:43:44
Data de resolução:  2022-02-23 17:28:30
Não compriu o SLA do chamado de prioridade Normal, passando em 11:43:44
```
```
Verificação da Tarefa:  7473  -  Pergamum
Data de atribuição:  -
Data de entrega:  -
Data de resolução:  2022-02-09 15:03:08
A fabrica de software não atuou na Tarefa
```
E também são exportados em uma tabela csv.

Exemplo:

|Tarefa|Sistema|Prioridade|SLA|Data de atribuicao|Data de entrega|Data de resolvido|Delta_tempo|Passou|Feriado|
|------|----------|--------|-----------|---|---|------------------|---------|---|-------|
| 7473 | Pergamum | Normal | NAO ATUOU | - | - | 09/02/2022 15:03 | 0:00:00 | - | FALSO |
| 7471 | SICG | Normal | FALSE | 2022-03-03 14:35:44 | 2022-02-08 19:43:44 | 23/02/2022 17:28 | 1 day, 11:43:44 | 11:43:44 | VERDADEIRO|
| 7422 | FISCALIS | Normal | TRUE |2021-12-29 12:26:24 | 2022-01-06 11:41:19 | 14/02/2022 16:46 | 14:11:33 | - | FALSO |

## Obs:.

Deve-se considerar que o Delta tempo dos SLAs consideram o tempo de 8:00 as 20:00 do dia, resultando em 12:00 de tempo líquido. Assim, valores que informem que o deltaTempo é de 1 day, significam que passou 2 dias (cada dia conta 12h).

O sistema trabalha com o calculo de delta tempos entre o início da atribuição para alguem da fabrica até a mudança de atribuição para qualquer outro usuário.

Por favor informar os inputs conforme indicado em cada pergunta.

