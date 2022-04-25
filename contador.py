from collections import UserList
import requests
import math
import datetime
import numpy as np
import json
import csv

from setuptools import PEP420PackageFinder

def request_module(url, auth_p):
    response = requests.get(url, auth=(auth_p))
    dicionario = response.text
    try:    
        dicio_deconding = json.loads(dicionario)
        return dicio_deconding 
    except:
        print()
        print("Redmine não respondeu a solicitacao")
        print()
        quit()

def counting_users(auth_p):
    url_base_users = 'https://redmine.iphan.gov.br/redmine/users.json?status=' 
    url_base_groups = 'https://redmine.iphan.gov.br/redmine/groups.json?status=' 
    dicio_decoding_users = request_module(url_base_users, auth_p)

    total_users = dicio_decoding_users['total_count']
    # O request retorna apenas 100 paginas por vez
    n_de_loops = math.ceil(float(total_users)/100)
    offset_numero = 0
    users_list = []

    for i in range (n_de_loops):
        add_filtro = '&'
        limit = 'limit=100'
        offset = 'offset='+ str(offset_numero)

        dicio_users_decoded = request_module(url_base_users + add_filtro + offset + add_filtro + limit,
        auth_p)

        users_list.append(dicio_users_decoded['users'])

        offset_numero = offset_numero + 100
    
    dicio_decoding_groups = request_module(url_base_groups, auth_p)
    groups_list = dicio_decoding_groups['groups']

    users_list_tratada = []

    for user_group in users_list:
        for user in user_group:
            users_list_tratada.append(user)

    # lista de users 
    users_id_login_list = [{'id': user['id'], 'login': user['login']} for user in users_list_tratada]

    for group in groups_list:
        users_id_login_list.append(group)

    # dicionario de users 
    dict_users_id_login_name = {'{}'.format(user.get('id')): ('{}'.format(user.get('login')) 
    if user.get('login') else '{}'.format(user.get('name'))) for user in users_id_login_list}

    return dict_users_id_login_name

def list_of_priorities(auth_p):
    url_base_priorities = 'https://redmine.iphan.gov.br/redmine/enumerations/issue_priorities.json' 
    dicio_decoding_priorities = request_module(url_base_priorities, auth_p)
    priorities_list = dicio_decoding_priorities['issue_priorities']

    list_priorities = [] 

    # lista de prioridades
    for priority in priorities_list:
       list_priorities.append({'id': priority['id'], 'name': priority['name']}) 

    # dicionario de prioridades
    dict_priorities= {'{}'.format(priority.get('id')): '{}'.format(priority.get('name')) for priority in list_priorities}

    return dict_priorities

def esta_na_lista(elemento, lista):
    elemento_esta_na_lista = lista.count(elemento)
    if elemento_esta_na_lista > 0:
        return True
    else:
        return False

# Calcula a quantidade de sabados entre 2 datas
def saturdays_days(data_inicial, data_final):
    data = data_inicial
    # Não pega o ultimo dia, tem que somar mais 1
    diff_data = data_final - data + datetime.timedelta(days=1)
    lista_saturdays = []

    for i in range(diff_data.days):
        if np.is_busday([data], weekmask='Sat'):
            lista_saturdays.append(data)
    
        data = data + datetime.timedelta(days=1)

    return lista_saturdays

# Calcula a quantidade de domingos entre 2 datas
def sundays_days(data_inicial, data_final):
    data = data_inicial
    # Não pega o ultimo dia, tem que somar mais 1
    diff_data = data_final - data + datetime.timedelta(days=1)
    lista_sundays= []

    for i in range(diff_data.days):
        if np.is_busday([data], weekmask='Sun'):
            lista_sundays.append(data)
    
        data = data + datetime.timedelta(days=1)
    
    return lista_sundays

def holidays_days(data_inicial, data_final, holidays_p):
    data = data_inicial
    # Não pega o ultimo dia, tem que somar mais 1
    diff_data = data_final - data + datetime.timedelta(days=1)
    lista_holidays= []
    if holidays_p:
        for i in range(diff_data.days):
            if np.is_busday([data], weekmask='1111111', holidays=holidays_p) == False:
                lista_holidays.append(data)
        
            data = data + datetime.timedelta(days=1)
    
    return lista_holidays

def time_counter(fabrica_users, journals_data, data_de_criacao, lista_feriados):
    # limpando as listas vazias [data, old_value, new_value, prioridade]
    primeiro_atribuido = journals_data[0][1] 

    atuou_em_feriados_ou_finais_de_semana = False

    primeiro_eh_fabrica= esta_na_lista(primeiro_atribuido, fabrica_users)

    lista_inicios = []
    lista_terminos = []

    lista_delta_tempo = []

    if primeiro_eh_fabrica:
        journal_insert = [data_de_criacao, "0", journals_data[0][1], journals_data[0][3]]
        journals_data.insert(0,journal_insert)
        
    for journal in journals_data:
        if esta_na_lista(journal[2], fabrica_users):
            inicio_tempo = journal[0]
            lista_inicios.append(inicio_tempo)
        
        if esta_na_lista(journal[1], fabrica_users):
            termino_tempo = journal[0]
            lista_terminos.append(termino_tempo)

    # casos em que foi homologado mas nao foi alterada a atribuição
    if len(lista_inicios) > len(lista_terminos):
       lista_terminos.append(journals_data[-1][0]) 
    
    lista_inicios_str_tratamento = []
    lista_terminos_str_tratamento = []

    for inicio in lista_inicios:
        lista_inicios_str_tratamento.append(inicio.replace("Z", ""))

    for termino in lista_terminos:
        lista_terminos_str_tratamento.append(termino.replace("Z", ""))
    
    lista_inicios_date = []
    lista_terminos_date = []

    for inicio in lista_inicios_str_tratamento:
        lista_inicios_date.append(datetime.datetime.fromisoformat(inicio))  
    
    for termino in lista_terminos_str_tratamento:
        lista_terminos_date.append(datetime.datetime.fromisoformat(termino))

    for i in range(len(lista_inicios)):

        sabado = False
        domingo = False

        delta_tempo_lista = lista_terminos_date[i].date() - lista_inicios_date[i].date()

        #saturdays = np.busday_count(lista_terminos_date[i].date(), lista_inicios_date[i].date(), weekmask='Sat') 
        saturdays_list = saturdays_days(lista_inicios_date[i].date(), lista_terminos_date[i].date())
        sundays_list = sundays_days(lista_inicios_date[i].date(), lista_terminos_date[i].date())
        holidays_list = holidays_days(lista_inicios_date[i].date(), lista_terminos_date[i].date(), lista_feriados)

        if saturdays_list:
            for i in range(len(saturdays_list)):
                delta_tempo_lista = delta_tempo_lista - datetime.timedelta(days=1) 
        if sundays_list:
            for i in range(len(sundays_list)):
                delta_tempo_lista = delta_tempo_lista - datetime.timedelta(days=1) 


        if holidays_list:
            for i in range(len(holidays_list)):
                delta_tempo_lista = delta_tempo_lista - datetime.timedelta(days=1) 
        
        lista_delta_tempo.append((delta_tempo_lista,holidays_list, saturdays_list, sundays_list))

    lista_delta_tempo_pos = []
    
    for i in range(len(lista_inicios)):
        if lista_delta_tempo[i][0].days < 2:

            if lista_delta_tempo[i][0].days == 1:

                tempo_1 = delta_tempo_inicial(lista_inicios_date[i]) 
                    
                tempo_2 = delta_tempo_termino(lista_terminos_date[i]) 

                lista_delta_tempo_pos.append(tempo_1 + tempo_2)

            if lista_delta_tempo[i][0].days == 0:

                if lista_delta_tempo[i][1] or lista_delta_tempo[i][2] or lista_delta_tempo[i][3]:
                    for j in range(1, 4, 1):
                        if lista_delta_tempo[i][j] == lista_inicios_date[i]:

                            tempo_2 = delta_tempo_termino(lista_terminos_date[i])

                            lista_delta_tempo_pos.append(tempo_2)
                        
                        if lista_delta_tempo[i][j] == lista_terminos_date[i]:

                            tempo_1 = delta_tempo_inicial(lista_inicios_date[i])

                            lista_delta_tempo_pos.append(tempo_1)
                else:
                    lista_delta_tempo_pos.append(lista_terminos_date[i] - lista_inicios_date[i])
                

            if lista_delta_tempo[i][0].days < 0:
                print("Atuou em feriados ou finais de semana")
                
                atuou_em_feriados_ou_finais_de_semana = True 

                lista_delta_tempo_pos.append(datetime.timedelta(hours=0))

        else:

            tempo_1 = delta_tempo_inicial(lista_inicios_date[i])
                
            tempo_3 = delta_tempo_termino(lista_terminos_date[i])

            tempo_2 = datetime.timedelta(hours=12)*(lista_delta_tempo[i][0] - datetime.timedelta(days=1)).days

            lista_delta_tempo_pos.append(tempo_1 + tempo_3 + tempo_2)
    
    tempo_total = datetime.timedelta(hours=0)

    for tempo in lista_delta_tempo_pos:
        tempo_total = tempo_total + tempo

    return tempo_total,atuou_em_feriados_ou_finais_de_semana

def delta_tempo_inicial(lista_inicios_date):
    tempo_23h = datetime.datetime.combine(lista_inicios_date.date(), datetime.time(hour=23))
    tempo_1 = tempo_23h - lista_inicios_date
    if tempo_1.seconds > 12*3600:
        tempo_1 = datetime.timedelta(hours=12)
    elif tempo_1.days < 0:
        tempo_1 = datetime.timedelta(hours=0)

    return tempo_1

def delta_tempo_termino(lista_terminos_date):
    tempo_11h = datetime.datetime.combine(lista_terminos_date.date(), datetime.time(hour=11))
    tempo_2 = lista_terminos_date - tempo_11h
    if tempo_2.seconds > 12*3600:
        tempo_2 = datetime.timedelta(hours=12)
    elif tempo_2.days < 0:
        tempo_2 = datetime.timedelta(hours=0)

    return tempo_2

def sla_verification(sla_especification, prioridade, delta_time):
    sla_valor = 0
    for sla in sla_especification:
        if prioridade == sla[0]:
            sla_valor = sla[1]
    
    sla_time = datetime.timedelta(hours=12)
    sla_time_priority = sla_time * sla_valor


    if sla_time_priority < delta_time:
        diff = delta_time - sla_time_priority  
        return (False, delta_time, diff)
    else:
        if delta_time == datetime.timedelta(hours=0):
            diff = datetime.timedelta(hours=0)
        else:
            diff = sla_time_priority - delta_time
        return (True, delta_time, diff)

def execute(tarefa, feriados, auth_params, usuarios_da_fabrica):
    url_base = 'https://redmine.iphan.gov.br/redmine'
    projects = '/projects.xml'
    issues = '/issues.xml'
    issue = '/issues/{}.json'.format(str(tarefa))
    notas = 'include=journals'
    sustentacao = 'tracker_id=49'
    demanda = 'tracker_id=38'
    addfiltro = '&'
    iniciarFiltro = '?'

    auth_user =  auth_params

    # Ver os trackers
    #https://redmine.iphan.gov.br/redmine/trackers.json

    # Ver todos os usuários
    #https://redmine.iphan.gov.br/redmine/users.json?status=

    # Ver os tipos de status das tarefas
    #https://redmine.iphan.gov.br/redmine/issue_statuses.json

    # URI usada
    #https://redmine.iphan.gov.br/redmine/issues/7400.json?include=journals

    # Listas de prioridades
    #https://redmine.iphan.gov.br/redmine/enumerations/issue_priorities.json

    status_homologado = "9"

    # baixa - 3dias; normal - 2 dias; alta, urgente e imediata - 1dia
    sla_especification = [(1,3),(2,2),(3,1),(4,1),(5,1)]

    url = url_base + issue + iniciarFiltro + notas

    dicionario_deconding = request_module(url, auth_user)

    lista_de_journals = dicionario_deconding['issue']['journals']
    tamanho_lista_de_journals = len(lista_de_journals)

    data_de_criacao_do_chamado = dicionario_deconding['issue']['created_on'] 

    priority = dicionario_deconding['issue']['priority']['id'] 
    
    project = dicionario_deconding['issue']['project']['name']

    print("Verificação da Tarefa: ",tarefa, " - ", project)

    journals_data = []

    # Cada journal é uma nota
    for journal in lista_de_journals:
        
        # Cada nota tem detalhes
        detalhes_journal = journal["details"]
        journal_data = [] 

        break_loop = False

        # Cada detalhe é um atributo da nota
        for detalhe in detalhes_journal:
            if "assigned_to_id" in detalhe.values():

                journal_data.append(journal['created_on'])
                journal_data.append(detalhe["old_value"])
                journal_data.append(detalhe["new_value"])
                journal_data.append(priority)
                
            # Quebra o loop se estiver com o status de homologado 
            if "status_id" in detalhe.values():
                if detalhe["new_value"] == status_homologado:
                    break_loop = True
        
        journals_data.append(journal_data)

        if break_loop:
            break

    # limpando as listas vazias [data, old_value, new_value, prioridade]
    journals_data = [x for x in journals_data if x]

    journals_priority = journals_data[0][3]

    
    types_of_priorities = list_of_priorities(auth_user)

    delta_time, atuou_em_feriados_ou_finais_de_semana = time_counter(usuarios_da_fabrica, journals_data, data_de_criacao_do_chamado, feriados)

    sla_pass, delta_time_sla, diff_sla = sla_verification(sla_especification, journals_priority , delta_time)

    sla_result = 0

    if sla_pass:
        sla_result = 1
        if delta_time_sla == datetime.timedelta(hours=0) and atuou_em_feriados_ou_finais_de_semana:
            print("Cumpriu o SLA do chamado atuando em feriados e finais de semana") 
            print()
        elif delta_time_sla == datetime.timedelta(hours=0):
            print("A fabrica de software não atuou na Tarefa") 
            print()
            sla_result = 2
        else:
            print('Compriu o SLA do chamado de prioridade {}, executando em {}'
            .format(types_of_priorities[str(journals_priority)],delta_time_sla))
            print()

    else:
        sla_result = 0
        print('Não compriu o SLA do chamado de prioridade {}, passando em {}'
        .format(types_of_priorities[str(journals_priority)],diff_sla))
        print()

    return  types_of_priorities[str(journals_priority)], sla_result, delta_time_sla, diff_sla, atuou_em_feriados_ou_finais_de_semana, project
    
def result_to_csv(issue, result):

    # result retorno
    # types_of_priorities[str(journals_priority)], sla_result, delta_time_sla, diff_sla, atuou_em_feriados_ou_finais_de_semana 

    passou_result = "-"
    sla_result = "FALSE"

    if result[1] == 0 :
        passou_result = str(result[3]) 

    if result[1] == 1 :
        sla_result = "TRUE"    
    
    if result[1] == 2 :
        sla_result = "NÂO ATUOU"

    dict_row = {
        "Tarefa": str(issue),
        "Sistema": str(result[5]),
        "Prioridade":str(result[0]),
        "SLA": sla_result,
        "Delta_tempo":str(result[2]),
        "Passou": passou_result,
        "Feriado":str(result[4]) 
        }
        
    with open('sla_result.csv', 'w', newline='') as csvfile:
        fieldnames = ['Tarefa','Sistema', 'Prioridade', 'SLA', 'Delta_tempo','Passou', 'Feriado']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow(dict_row)

if __name__ == '__main__':
    tarefa = 7489
    # Para testes 7612
    dias_feriado = [datetime.date(2022,2,15)]
    #dias_feriado = []
    meu_login = ""
    minha_senha = ""

    auth_user = (meu_login, minha_senha)

    print("")

    dict_all_users = counting_users(auth_user)

    # leandro, rhoxanna, mauricio, cristiano, romao, gestor fabrica, desenvolvedor fabrica
    usuarios_da_fabrica = ['204', '279', '269', '259', '250', '165', '164']
    
    print("Usuários da Fabrica de Software considerados para a verificação do SLA:")
    print("")

    for usuario in usuarios_da_fabrica:
        print(dict_all_users[usuario])

    print("")
    print("-------------------------------------------------------")
    print("")

    result_unic = execute(tarefa, dias_feriado, auth_user, usuarios_da_fabrica )

    result_to_csv(tarefa, result_unic)
    
    #json_object = json.dumps(dicionario_deconding, indent=4, ensure_ascii=False)
