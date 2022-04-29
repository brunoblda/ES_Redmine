from collections import UserList
from re import I
from tarfile import TarError
import requests
import math
from getpass import getpass
import datetime
import numpy as np
import json
import result_to_csv as to_csv

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

    holidays_date = []
    for holiday_p in holidays_p:
        holidays_date.append(holiday_p[0])

    if holidays_p:
        for i in range(diff_data.days):
            if np.is_busday([data], weekmask='1111111', holidays=holidays_date) == False:
                lista_holidays.append(data)
        
            data = data + datetime.timedelta(days=1)
    
    return lista_holidays

def time_counter(fabrica_users, journals_data, data_de_criacao, lista_feriados):
    # limpando as listas vazias [data, old_value, new_value, prioridade]
    primeiro_atribuido = journals_data[0][1] 

    atuou_em_feriados_ou_finais_de_semana = False

    # Identifica se o chamado foi aberto ja atribuindo alguem da fabrica
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
    
    lista_inicios_date_tmz = []
    lista_terminos_date_tmz = []

    for inicio in lista_inicios_str_tratamento:
        lista_inicios_date_tmz.append(datetime.datetime.fromisoformat(inicio))  
    
    if lista_inicios_date_tmz:
        primeira_atribuicao = lista_inicios_date_tmz[0]
        primeira_atribuicao = primeira_atribuicao - datetime.timedelta(hours=3)
    else:
        primeira_atribuicao = "-"
    
    for termino in lista_terminos_str_tratamento:
        lista_terminos_date_tmz.append(datetime.datetime.fromisoformat(termino))

    lista_inicios_date = []

    if lista_inicios_date_tmz:
        for inicios_data in lista_inicios_date_tmz:
            lista_inicios_date.append(inicios_data - datetime.timedelta(hours=3))

    lista_terminos_date = []

    if lista_terminos_date_tmz:
        for terminos_data in lista_terminos_date_tmz:
            lista_terminos_date.append(terminos_data - datetime.timedelta(hours=3))

    for i in range(len(lista_inicios)):

        delta_tempo_lista = lista_terminos_date[i].date() - lista_inicios_date[i].date()

        #saturdays = np.busday_count(lista_terminos_date[i].date(), lista_inicios_date[i].date(), weekmask='Sat') 
        saturdays_list = saturdays_days(lista_inicios_date[i].date(), lista_terminos_date[i].date())
        sundays_list = sundays_days(lista_inicios_date[i].date(), lista_terminos_date[i].date())

        """
        lista_feriados_integrais = []
        for feriados_in_lista in lista_feriados:
            if feriados_in_lista[1] == "i":
                lista_feriados_integrais.append(feriados_in_lista)
        
        lista_feriados_parciais = []
        for feriados_in_lista in lista_feriados:
            if feriados_in_lista[1] != "i":
                lista_feriados_parciais.append(feriados_in_lista)

        print("feriados parciais: ", lista_feriados_parciais)
        
        """
        holidays_list = holidays_days(lista_inicios_date[i].date(), lista_terminos_date[i].date(), lista_feriados)

        if saturdays_list:
            for x in range(len(saturdays_list)):
                delta_tempo_lista = delta_tempo_lista - datetime.timedelta(days=1) 
        if sundays_list:
            for y in range(len(sundays_list)):
                delta_tempo_lista = delta_tempo_lista - datetime.timedelta(days=1) 

        holidays_list_com_periodo = []

        for w in range(len(holidays_list)):
            for feriado in lista_feriados:
                if holidays_list[w] == feriado[0]:
                    holidays_list_com_periodo.append((holidays_list[w], feriado[1]))

        if holidays_list_com_periodo:
            for holiday_com_periodo in holidays_list_com_periodo:
                if ((not (holiday_com_periodo[0] in saturdays_list)) and (not (holiday_com_periodo[0] in sundays_list))):
                    atuou_em_feriados_ou_finais_de_semana = True
                    print("Atuou em feriados") 
                    if holiday_com_periodo[1] == "i":
                        delta_tempo_lista = delta_tempo_lista - datetime.timedelta(days=1) 

        lista_delta_tempo.append((delta_tempo_lista,holidays_list_com_periodo, saturdays_list, sundays_list))

    lista_delta_tempo_pos = []

    data_de_entrega = '-' 

    data_de_entrega_f = '-'
    
    for i in range(len(lista_inicios)):
        
        if lista_delta_tempo[i][0].days < 2:

            if lista_delta_tempo[i][0].days == 1:

                resposta = False
                
                if lista_delta_tempo[i][1] or lista_delta_tempo[i][2] or lista_delta_tempo[i][3]:
                    for j in range(1, 4, 1):
                        if lista_delta_tempo[i][j]:
                            # lista_delta_tempo[i][1] possuiu uma tupla dentro então pegaria a tupla e nao o tempo
                            if j != 1:
                                for dia_de_fim_de_semana in lista_delta_tempo[i][j]:
                                    if dia_de_fim_de_semana == lista_inicios_date[i].date():
                                        
                                        tempo_2 = delta_tempo_termino(lista_terminos_date[i])
                                        
                                        resposta = tempo_2 + datetime.timedelta(hours=12)

                                        lista_delta_tempo_pos.append(resposta)
                                        
                                        data_de_entrega = lista_terminos_date[i]
                                    
                                    if dia_de_fim_de_semana == lista_terminos_date[i].date():

                                        tempo_1 = delta_tempo_inicial(lista_inicios_date[i])

                                        resposta = tempo_1 + datetime.timedelta(hours=12)

                                        lista_delta_tempo_pos.append(resposta)

                                        data_de_entrega = datetime.datetime.combine(lista_inicios_date[i].date(), datetime.time(hour=20)) 
                            else:
                                
                                for feriado in lista_delta_tempo[i][j]:

                                    if feriado[1] == "i":

                                        if feriado[0] == lista_inicios_date[i].date():

                                            tempo_2 = delta_tempo_termino(lista_terminos_date[i])

                                            resposta = tempo_2 + datetime.timedelta(hours=12)

                                            lista_delta_tempo_pos.append(resposta)
                                            
                                            data_de_entrega = lista_terminos_date[i]
                                        
                                        if feriado[0] == lista_terminos_date[i].date():

                                            tempo_1 = delta_tempo_inicial(lista_inicios_date[i])

                                            resposta = tempo_1 + datetime.timedelta(hours=12)

                                            lista_delta_tempo_pos.append(resposta)

                                            data_de_entrega = datetime.datetime.combine(lista_inicios_date[i].date(), datetime.time(hour=20)) 
                                    
                                    else:

                                        if feriado[0] == lista_inicios_date[i].date():

                                            tempo_2 = delta_tempo_termino_parcial(lista_terminos_date[i], feriado[1])

                                            resposta = tempo_2 + datetime.timedelta(hours=12)

                                            lista_delta_tempo_pos.append(resposta)
                                            
                                            data_de_entrega = lista_terminos_date[i]
                                        
                                        if feriado[0] == lista_terminos_date[i].date():

                                            tempo_1 = delta_tempo_inicial_parcial(lista_inicios_date[i], feriado[1])

                                            resposta = tempo_1 + datetime.timedelta(hours=12)

                                            lista_delta_tempo_pos.append(resposta)

                                            data_de_entrega = datetime.datetime.combine(lista_inicios_date[i].date(), datetime.time(hour=20)) 

                if not resposta:

                    tempo_1 = delta_tempo_inicial(lista_inicios_date[i]) 
                    tempo_2 = delta_tempo_termino(lista_terminos_date[i]) 

                    lista_delta_tempo_pos.append(tempo_1 + tempo_2)

                    data_de_entrega = lista_terminos_date[i]

            if lista_delta_tempo[i][0].days == 0:

                resposta = False

                if lista_delta_tempo[i][1] or lista_delta_tempo[i][2] or lista_delta_tempo[i][3]:
                    for j in range(1, 4, 1):
                        if lista_delta_tempo[i][j]:
                            # lista_delta_tempo[i][1] possuiu uma tupla dentro então pegaria a tupla e nao o tempo
                            if j != 1:
                                for dia_de_fim_de_semana in lista_delta_tempo[i][j]:

                                    if dia_de_fim_de_semana == lista_inicios_date[i].date():

                                        tempo_2 = delta_tempo_termino(lista_terminos_date[i])

                                        resposta = tempo_2         

                                        lista_delta_tempo_pos.append(resposta)
                                        
                                        data_de_entrega = lista_terminos_date[i]
                                    
                                    if dia_de_fim_de_semana == lista_terminos_date[i].date():

                                        tempo_1 = delta_tempo_inicial(lista_inicios_date[i])

                                        resposta = tempo_1

                                        lista_delta_tempo_pos.append(resposta)

                                        data_de_entrega = datetime.datetime.combine(lista_inicios_date[i].date(), datetime.time(hour=20)) 
                            else:

                                for feriado in lista_delta_tempo[i][j]:

                                    if feriado[1] == "i":

                                        if feriado[0] == lista_inicios_date[i].date():

                                            tempo_2 = delta_tempo_termino(lista_terminos_date[i])

                                            resposta = tempo_2

                                            lista_delta_tempo_pos.append(resposta)
                                            
                                            data_de_entrega = lista_terminos_date[i]
                                        
                                        if feriado[0] == lista_terminos_date[i].date():

                                            tempo_1 = delta_tempo_inicial(lista_inicios_date[i])

                                            resposta = tempo_1

                                            lista_delta_tempo_pos.append(resposta)

                                            data_de_entrega = datetime.datetime.combine(lista_inicios_date[i].date(), datetime.time(hour=20)) 
                                    else:

                                        if feriado[0] == lista_inicios_date[i].date():

                                            tempo_2 = delta_tempo_termino_parcial(lista_terminos_date[i], feriado[1])

                                            resposta = tempo_2  

                                            lista_delta_tempo_pos.append(resposta)
                                            
                                            data_de_entrega = lista_terminos_date[i]
                                        
                                        if feriado[0] == lista_terminos_date[i].date():

                                            tempo_1 = delta_tempo_inicial_parcial(lista_inicios_date[i], feriado[1])

                                            resposta = tempo_1 

                                            lista_delta_tempo_pos.append(resposta)

                                            data_de_entrega = datetime.datetime.combine(lista_inicios_date[i].date(), datetime.time(hour=20)) 

                if not resposta:
                    if lista_terminos_date[i] > datetime.datetime.combine(lista_terminos_date[i].date(), datetime.time(hour=20)): 
                        lista_delta_tempo_pos.append(delta_tempo_inicial(lista_inicios_date[i]))   

                        data_de_entrega = datetime.datetime.combine(lista_terminos_date[i].date(), datetime.time(hour=20)) 

                    elif lista_inicios_date[i] < datetime.datetime.combine(lista_inicios_date[i].date(), datetime.time(hour=8)): 
                        lista_delta_tempo_pos.append(delta_tempo_termino(lista_terminos_date[i]))   

                        data_de_entrega = lista_terminos_date[i]

                    else:
                        lista_delta_tempo_pos.append(lista_terminos_date[i] - lista_inicios_date[i])

                        data_de_entrega = lista_terminos_date[i]

            if lista_delta_tempo[i][0].days < 0:
                print("Atuou em feriados e/ou finais de semana")
                
                atuou_em_feriados_ou_finais_de_semana = True 

                lista_delta_tempo_pos.append(datetime.timedelta(hours=0))

                data_de_entrega = lista_terminos_date[i]

        else:

            tempo_1 = False
            tempo_3 = False
            tempo_2_count = 0

            if lista_delta_tempo[i][1] or lista_delta_tempo[i][2] or lista_delta_tempo[i][3]:
                for j in range(1, 4, 1):
                    if lista_delta_tempo[i][j]:
                        # lista_delta_tempo[i][1] possuiu uma tupla dentro então pegaria a tupla e nao o tempo
                        if j != 1:
                            for dia_de_fim_de_semana in lista_delta_tempo[i][j]:
                                if dia_de_fim_de_semana == lista_inicios_date[i].date():
                                    
                                    tempo_3 = delta_tempo_termino(lista_terminos_date[i])
                                    
                                    data_de_entrega = lista_terminos_date[i]
                                
                                if dia_de_fim_de_semana == lista_terminos_date[i].date():

                                    tempo_1 = delta_tempo_inicial(lista_inicios_date[i])

                                    data_de_entrega = datetime.datetime.combine(lista_inicios_date[i].date(), datetime.time(hour=20)) 
                        else:
                            
                            for feriado in lista_delta_tempo[i][j]:

                                if feriado[1] == "i":

                                    if feriado[0] == lista_inicios_date[i].date():

                                        tempo_3 = delta_tempo_termino(lista_terminos_date[i])

                                        data_de_entrega = lista_terminos_date[i]
                                    
                                    if feriado[0] == lista_terminos_date[i].date():

                                        tempo_1 = delta_tempo_inicial(lista_inicios_date[i])

                                        resposta = tempo_1 

                                        data_de_entrega = datetime.datetime.combine(lista_inicios_date[i].date(), datetime.time(hour=20)) 
                                
                                else:

                                    if feriado[0] == lista_inicios_date[i].date():

                                        tempo_3 = delta_tempo_termino_parcial(lista_terminos_date[i], feriado[1])

                                        data_de_entrega = lista_terminos_date[i]
                                    
                                    elif feriado[0] == lista_terminos_date[i].date():

                                        tempo_1 = delta_tempo_inicial_parcial(lista_inicios_date[i], feriado[1])

                                        resposta = tempo_1 

                                        data_de_entrega = datetime.datetime.combine(lista_inicios_date[i].date(), datetime.time(hour=20))

                                    else:
                                        tempo_2_count = tempo_2_count + 1
            if not tempo_1:

                tempo_1 = delta_tempo_inicial(lista_inicios_date[i])
                    
            if not tempo_3:

                tempo_3 = delta_tempo_termino(lista_terminos_date[i])

            tempo_2 = datetime.timedelta(hours=12)*(lista_delta_tempo[i][0] - datetime.timedelta(days=1)).days

            if tempo_2_count:

                tempo_2 = tempo_2 - datetime.timedelta(hours=6)*tempo_2_count

            lista_delta_tempo_pos.append(tempo_1 + tempo_3 + tempo_2)

            data_de_entrega = lista_terminos_date[i]

        if lista_delta_tempo_pos[i] != datetime.timedelta(hours=0):
            data_de_entrega_f = data_de_entrega 
    
    tempo_total = datetime.timedelta(hours=0)

    # data_de_entrega_f pega a data do chamado antes do status virar homologado
    if not isinstance(data_de_entrega_f, str):
        data_de_entrega_f = data_de_entrega_f - datetime.timedelta(hours=3)

    for tempo in lista_delta_tempo_pos:

        tempo_total = tempo_total + tempo

    return tempo_total,atuou_em_feriados_ou_finais_de_semana, primeira_atribuicao, data_de_entrega_f

def delta_tempo_inicial(lista_inicios_date):
    tempo_20h = datetime.datetime.combine(lista_inicios_date.date(), datetime.time(hour=20))
    tempo_1 = tempo_20h - lista_inicios_date
    if tempo_1.days < 0:
        tempo_1 = datetime.timedelta(hours=0)
    elif tempo_1.seconds > 12*3600:
        tempo_1 = datetime.timedelta(hours=12)

    return tempo_1

def delta_tempo_termino(lista_terminos_date):
    tempo_8h = datetime.datetime.combine(lista_terminos_date.date(), datetime.time(hour=8))
    tempo_2 = lista_terminos_date - tempo_8h
    if tempo_2.days < 0:
        tempo_2 = datetime.timedelta(hours=0)
    elif tempo_2.seconds > 12*3600:
        tempo_2 = datetime.timedelta(hours=12)

    return tempo_2

def delta_tempo_termino_parcial(lista_terminos_date, tipo):

    if tipo == "m":
        tempo_14h = datetime.datetime.combine(lista_terminos_date.date(), datetime.time(hour=14))
        tempo_2 = lista_terminos_date - tempo_14h
        if tempo_2.days < 0:
            tempo_2 = datetime.timedelta(hours=0)
        elif tempo_2.seconds > 6*3600:
            tempo_2 = datetime.timedelta(hours=6)

    if tipo == "v":
        tempo_8h = datetime.datetime.combine(lista_terminos_date.date(), datetime.time(hour=8))
        tempo_2 = lista_terminos_date - tempo_8h
        if tempo_2.days < 0:
            tempo_2 = datetime.timedelta(hours=0)
        elif tempo_2.seconds > 6*3600:
            tempo_2 = datetime.timedelta(hours=6)

    return tempo_2

def delta_tempo_inicial_parcial(lista_inicios_date, tipo):
    if tipo == "m":
        tempo_20h = datetime.datetime.combine(lista_inicios_date.date(), datetime.time(hour=20))
        tempo_1 = tempo_20h - lista_inicios_date
        if tempo_1.days < 0:
            tempo_1 = datetime.timedelta(hours=0)
        elif tempo_1.seconds > 6*3600:
            tempo_1 = datetime.timedelta(hours=6)

    if tipo == "v":
        tempo_14h = datetime.datetime.combine(lista_inicios_date.date(), datetime.time(hour=14))
        tempo_1 = tempo_14h - lista_inicios_date
        if tempo_1.days < 0:
            tempo_1 = datetime.timedelta(hours=0)
        elif tempo_1.seconds > 6*3600:
            tempo_1 = datetime.timedelta(hours=6)

    return tempo_1

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

def get_data_resolvida(lista_de_journals):

    status_resolvido = "3"
    
    data_resolvido = ""

    for journal in lista_de_journals:
        
        # Cada nota tem detalhes
        detalhes_journal = journal["details"]
        journal_data = [] 

        break_loop = False

        # Cada detalhe é um atributo da nota
        for detalhe in detalhes_journal:
                
            # Quebra o loop se estiver com o status de homologado 
            if "status_id" in detalhe.values():
                if detalhe["new_value"] == status_resolvido:
                    data_resolvido = journal["created_on"]
                    break_loop = True
        
        if break_loop:
            break
    
    data_resolvido_str = data_resolvido.replace("Z","")

    data_resolvido_date = datetime.datetime.fromisoformat(data_resolvido_str)

    data_resolvido_date = data_resolvido_date - datetime.timedelta(hours=3)

    return data_resolvido_date

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

    data_resolvido = get_data_resolvida(lista_de_journals)
    
    types_of_priorities = list_of_priorities(auth_user)

    delta_time, atuou_em_feriados_ou_finais_de_semana, primeira_atribuicao, data_de_entrega = time_counter(usuarios_da_fabrica, journals_data, data_de_criacao_do_chamado, feriados)

    sla_pass, delta_time_sla, diff_sla = sla_verification(sla_especification, journals_priority , delta_time)

    sla_result = 0

    print("Data de atribuição: ", primeira_atribuicao)
    print("Data de entrega: ", data_de_entrega)
    print("Data de resolução: ", data_resolvido)

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

    return  types_of_priorities[str(journals_priority)], sla_result, delta_time_sla, diff_sla, atuou_em_feriados_ou_finais_de_semana, project, primeira_atribuicao, data_de_entrega, data_resolvido

def feriados_lista_out(feriados_lista):
    all_feriados = []
    for feriado in feriados_lista:
        feriado_split = feriado[0].split("/")
        dia = int(feriado_split[0])
        mes = int(feriado_split[1]) 
        ano = int(feriado_split[2])
        data_feriado = (datetime.date(day=dia, month=mes, year=ano), feriado[1])
        all_feriados.append(data_feriado)
    
    return all_feriados
    
if __name__ == '__main__':
    #tarefa = 7489
    # Para testes 7612
    # tarefa = 7319
    # tarefa = 7499
    tarefa = 7358

    feriados_2021=[("01/01/2021", "i"), ("15/02/2021", "i"), ("16/02/2021", "i"), ("17/02/2021", "m"), ("02/04/2021", "i"), ("21/04/2021", "i"), ("01/05/2021", "i"), ("03/06/2021", "i"), ("07/09/2021", "i"), ("12/10/2021", "i"), ("01/11/2021", "i"), ("02/11/2021", "i"), ("15/11/2021", "i"), ("24/12/2021", "v"), ("25/12/2021", "i"), ("31/12/2021", "V")]
    feriados_2022=[("01/01/2022", "i"), ("28/02/2022", "i"), ("01/03/2022", "i"), ("02/03/2022", "m"), ("15/04/2022", "i"), ("21/04/2022", "i"), ("22/04/2022", "i"), ("01/05/2022", "i"), ("16/06/2022", "i"), ("07/09/2022", "i"), ("12/10/2022", "i"), ("28/10/2022", "i"), ("02/11/2022", "i"), ("15/11/2022", "i"), ("25/12/2022", "i")]

    dias_feriados = [] 
    dias_feriados.extend(feriados_lista_out(feriados_2021))
    dias_feriados.extend(feriados_lista_out(feriados_2022))

    # dias_feriado = all_feriados

    # 7473 - não atuou
    # 7358 e 7371 passaram muito
    # 7461 testar chamados fechados atribuidos no final à global sem serem homologados tem um "feriado" 03/02/2022

    # dias de feriado para testar tarefa 7489
    # dias_feriado = [datetime.date(2022,2,15)]
    # dias_feriado = []
    dias_feriado = [(datetime.date(2021,12,7), "i"), (datetime.date(2021,12,9), "i"), (datetime.date(2021,12,14), "i"), (datetime.date(2021,12,15), "i"), (datetime.date(2021,12,16), "i")]

    # dias_feriado = [(datetime.date(2022,2,3), "i"), (datetime.date(2022,2,4), "i")]
    # dias_feriado = [(datetime.date(2022,2,3), "i")]
    # dias_feriado = [(datetime.date(2022,2,3), "i")]
    # dias_feriado = [datetime.date(2021,11,15), datetime.date(2021,12,24), datetime.date(2021,12,25), datetime.date(2022,1,1)]
    # dias_feriado = [datetime.date(2021,12,24)]
    # moving data center 27/01/2022 20:05 as 03/02/2022 20:00

    dias_feriado.extend(dias_feriados)

    #tarefa = 7358
    #dias_feriado = []
    meu_login = input("Digite seu login: ")
    minha_senha = getpass("Digite sua senha: ")

    auth_user = (meu_login, minha_senha)

    print("")

    dict_all_users = counting_users(auth_user)

    # leandro, rhoxanna, mauricio, cristiano, romao, gestor fabrica, desenvolvedor fabrica, sabino
    usuarios_da_fabrica = ['204', '279', '269', '259', '250', '165', '164', '272']
    
    print("Usuários da Fabrica de Software considerados para a verificação do SLA:")
    print("")

    for usuario in usuarios_da_fabrica:
        print(dict_all_users[usuario])

    print("")
    print("-------------------------------------------------------")
    print("")

    result_unic = execute(tarefa, dias_feriado, auth_user, usuarios_da_fabrica )

    to_csv.result_to_csv([tarefa], [result_unic])
    
    #json_object = json.dumps(dicionario_deconding, indent=4, ensure_ascii=False)
