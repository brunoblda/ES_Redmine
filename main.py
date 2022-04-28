from asyncio import run_coroutine_threadsafe
from dataclasses import field
from http.cookiejar import FileCookieJar
from lib2to3.pgen2.token import NEWLINE
from getpass import getpass
from re import I
import requests
import contador
import datetime
import result_to_csv as to_csv

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

def feriados_lista_out(feriados_lista):
    all_feriados = []
    for feriado in feriados_lista:
        feriado_split = feriado.split("/")
        dia = int(feriado_split[0])
        mes = int(feriado_split[1]) 
        ano = int(feriado_split[2])
        data_feriado = datetime.date(day=dia, month=mes, year=ano)
        all_feriados.append(data_feriado)
    
    return all_feriados

if __name__ == '__main__':
    offset_numero = 0
    issues_resolved_list = []

    feriados_2021=["01/01/2021", "15/02/2021", "16/02/2021", "17/02/2021", "02/04/2021", "21/04/2021", "01/05/2021", "03/06/2021", "07/09/2021", "12/10/2021", "28/10/2021", "02/11/2021", "15/11/2021", "24/12/2021", "25/12/2021", "31/12/2021"]
    feriados_2022=["01/01/2022", "28/02/2022", "01/03/2022", "02/03/2022", "15/04/2022", "21/04/2022", "22/04/2022", "01/05/2022", "16/06/2022", "07/09/2022", "12/10/2022", "28/10/2022", "02/11/2022", "15/11/2022", "25/12/2022"]

    # percorre por 10 paginas com 50 issues cada
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

    print("Feriados 2021: ")
    print("")
    print(feriados_2021)
    print("")
    print("Feriados 2022: ")
    print("")
    print(feriados_2022)
    print("")

    tem_feriado = input("Você gostaria de adicionar mais algum feriado além dos mencionados acima? (s/n): ")
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
    
    dias_feriados.extend(feriados_lista_out(feriados_2021))
    dias_feriados.extend(feriados_lista_out(feriados_2022))

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

        # criar um arquivo resultado mostrando a resposta de cada pagina
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

    print("usuários da Fabrica de Software considerados para a verificação do SLA:")
    print("")

    # leandro, rhoxanna, mauricio, cristiano, romao, gestor fabrica, desenvolvedor fabrica, sabino
    usuarios_da_fabrica = ['204', '279', '269', '259', '250', '165', '164', '272']

    dict_all_users = contador.counting_users(auth_user)
    for usuario in usuarios_da_fabrica:
        print(dict_all_users[usuario])
    print("")
    print("-------------------------------------------------------")
    print("")

    for issue in issues_resolved_list:
        list_of_results.append(contador.execute(issue, dias_feriados, auth_user, usuarios_da_fabrica))
    
    to_csv.result_to_csv(issues_resolved_list, list_of_results)

    print("-------------------------------------------------------")
    print("")
    print("As informações apresentadas acima também foram sintetizadas no arquivo csv sla_results.")
    print("")
    final_prog = input("Digite enter para sair.")
    print("")