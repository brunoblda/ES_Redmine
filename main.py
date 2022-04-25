from asyncio import run_coroutine_threadsafe
from dataclasses import field
from http.cookiejar import FileCookieJar
from lib2to3.pgen2.token import NEWLINE
from getpass import getpass
from re import I
import requests
import contador
import datetime
import csv

import json

'''
Modelo de chamada basica

url_base = 'https://redmine.iphan.gov.br/redmine'
projects = '/projects.xml'
issues = '/issues.xml'
issue7400 = "/issues/7400.json"
notas = 'include=journals'
sustentacao = 'tracker_id=49'
demanda = 'tracker_id=38'
addfiltro = '&'
iniciarFiltro = '?'

response = requests.get(url_base + issue7400 + iniciarFiltro + sustentacao + addfiltro + notas, auth=('login', 'senha'))
'''

def result_to_csv(list_issues, list_results):

    # result retorno
    # types_of_priorities[str(journals_priority)], sla_result, delta_time_sla, diff_sla, atuou_em_feriados_ou_finais_de_semana 

    if (len(list_issues) == len(list_results)):

        list_rows = []

        for i in range(len(list_issues)):

            passou_result = "-"
            sla_result = "FALSE"

            if list_results[i][1] == 0 :
                passou_result = str(list_results[i][3]) 

            if list_results[i][1] == 1 :
                sla_result = "TRUE"    
            
            if list_results[i][1] == 2 :
                sla_result = "NAO ATUOU"

            dict_row = {
                "Tarefa": str(list_issues[i]),
                "Sistema": str(list_results[i][5]),
                "Prioridade":str(list_results[i][0]),
                "SLA": sla_result,
                "Delta_tempo":str(list_results[i][2]),
                "Passou": passou_result,
                "Feriado":str(list_results[i][4]) 
                }
            
            list_rows.append(dict_row)
            
        with open('sla_results.csv', 'w', newline='') as csvfile:
            fieldnames = ['Tarefa', 'Sistema', 'Prioridade', 'SLA', 'Delta_tempo','Passou', 'Feriado']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in list_rows:
                writer.writerow(row)
    else:
        print("Por algum motivo a lista de tarefas esta maior que a lista de resultados da análise, arquivo não foi gerado")

if __name__ == '__main__':
    offset_numero = 0
    issues_resolved_list = []
    # Percorre por 10 paginas com 50 issues cada
    percorre_quantas_paginas = 10

    url_login = 'https://redmine.iphan.gov.br/redmine/issues.json' 

    login_failed = True

    while login_failed:
        print("")
        login = input("Login: ")
        print("")
        senha = getpass("Senha: ")
        print("")
        response = requests.get(url_login, auth=(login, senha))

        if response.status_code == 200:
            login_failed = False
        else:
            print("Login incorreto ou senha incorreta ou seu perfil não é de administrador ou o Redmine se encontra fora do ar")

    auth_user = (login, senha)

    print("")
    qual_mes = input("Digite o numero do mes que será verificado (MM): ")
    print("")
    qual_ano = input("Digite o numero do ano que será verificado (AAAA): ")
    print("")

    tem_feriado = input("Esse mês teve algum feriado em dia de semana (s/n): ")
    print("")

    verdadeiro = True

    dias_feriados=[]

    if tem_feriado == "s":
        print("Digite -1 se ja informou todos os dias de semana que são feriados !!!")
        print()
        while verdadeiro:
            data_feriado = input("Digite a data do feriado (DD/MM/AAAA): ")

            if data_feriado == '-1':
                break

            split_data = data_feriado.split('/')
            
            data_feriado_date = datetime.date(int(split_data[2]), int(split_data[1]), int(split_data[0]))

            """
            integral = True
            feriado_integral = input("Feriado o dia inteiro (s/n): ")
            if feriado_integral == 'n':
                integral = False 
            """
            dias_feriados.append(data_feriado_date )

    for i in range(percorre_quantas_paginas):

        url_base = 'https://redmine.iphan.gov.br/redmine'
        projects = '/projects.json'
        issues = '/issues.json'
        issue7400 = "/issues/7400.json"
        notas = 'include=journals'
        sustentacao = 'tracker_id=49'
        status_closed = 'status_id=closed'
        add_filtro = '&'
        iniciarFiltro = '?'
        # 100 sao muitos dados, esbarrou no limite de json de itens (5000)
        limit = 'limit=50'
        offset = 'offset='+ str(offset_numero)

        url_request = url_base + issues + iniciarFiltro + \
            status_closed + add_filtro + limit + add_filtro + offset

        response = requests.get(url_request, auth=(login, senha))

        dicionario = response.text

        dicionario_deconding = json.loads(dicionario)

        # Criar um arquivo resultado mostrando a resposta de cada pagina
        """
        json_object = json.dumps(dicionario_deconding, indent=4, ensure_ascii=False)

        with open("resultado.json", "w", encoding='utf-8') as outfile:
            outfile.write(json_object)
        """

        # all_issues_list = dicionario["issues"]

        for tarefa in dicionario_deconding["issues"]:
            closed_on = tarefa["closed_on"]
            mes_closed = closed_on[5:7]
            ano_closed = closed_on[0:4]

            created_on = tarefa["created_on"]
            mes_created = created_on[5:7]    
            ano_created = created_on[0:4]

            status = tarefa["status"]["name"]
            tipo = tarefa["tracker"]["name"]
            if (status == "Resolvida") & (mes_closed == str(qual_mes)) & (ano_closed == str(qual_ano)) & (tipo == "Sustentação"):
                issues_resolved_list.append(tarefa["id"])

        offset_numero = offset_numero + 50

    print("-------------------------------------------------------")

    print(url_request)

    print("-------------------------------------------------------")

    print(issues_resolved_list)

    print("")

    list_of_results = []

    print("Usuários da Fabrica de Software considerados para a verificação do SLA:")
    print("")

    usuarios_da_fabrica = ['204', '279', '269', '259', '250', '165', '164']

    dict_all_users = contador.counting_users(auth_user)
    for usuario in usuarios_da_fabrica:
        print(dict_all_users[usuario])
    print("")
    print("-------------------------------------------------------")
    print("")

    for issue in issues_resolved_list:
        list_of_results.append(contador.execute(issue, dias_feriados, auth_user, usuarios_da_fabrica))
    
    result_to_csv(issues_resolved_list, list_of_results)

    print("-------------------------------------------------------")
    print("")
    print("As informações apresentadas acima também foram sintetizadas no arquivo csv sla_results.")
    print("")
    final_prog = input("Digite enter para sair.")
    print("")