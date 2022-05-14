import csv

def result_to_csv(list_issues, list_results):

    # result retorno
    # types_of_priorities[str(journals_priority)], sla_result, delta_time_sla, diff_sla, atuou_em_feriados_ou_finais_de_semana, primeira_atribuicao 

    if (len(list_issues) == len(list_results)):

        list_rows = []

        for i in range(len(list_issues)):

            passou_result = "-"
            sla_result = "FALSE"

            if list_results[i][1] == 0 :
                passou_result = to_hours(list_results[i][3]) 

            if list_results[i][1] == 1 :
                sla_result = "TRUE"    
            
            if list_results[i][1] == 2 :
                sla_result = "NAO ATUOU"

            dict_row = {
                "Tarefa": str(list_issues[i]),
                "Sistema": str(list_results[i][5]),
                "Prioridade":str(list_results[i][0]),
                "SLA": sla_result,
                "Data de atribuicao": str(list_results[i][6]),
                "Data de entrega": str(list_results[i][7]),
                "Data resolvido": str(list_results[i][8]),
                "Delta_tempo":to_hours(list_results[i][2]),
                "Passou": passou_result,
                "Feriado":str(list_results[i][4]) 
                }
            
            list_rows.append(dict_row)

        csv_name = ""

        if len(list_issues) == 1:
            csv_name = 'sla_result.csv'
            
        else:
            csv_name = 'sla_results.csv'

        with open(csv_name, 'w', newline='') as csvfile:
            fieldnames = ['Tarefa', 'Sistema', 'Prioridade', 'SLA', 'Data de atribuicao', 'Data de entrega', 'Data resolvido', 'Delta_tempo','Passou', 'Feriado']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in list_rows:
                writer.writerow(row)

    else:
        print("Por algum motivo a lista de tarefas esta maior que a lista de resultados da análise, arquivo não foi gerado")

def to_hours(string_data):

    string_data = str(string_data)

    tamanho = len(string_data)
    horas_formatada = string_data

    dias_list = []
    dias_str = ""
    dias_num = 0
    i = 0

    if tamanho > 8:

        while string_data[i] != " ":
            dias_list.append(string_data[i])
            i += 1

        for letra in dias_list:
            dias_str = dias_str + str(letra)  
        
        dias_num = int(dias_str)

        divisao = string_data.split(", ")

        hours_minutes_seconds = divisao[1].split(":")

        dias_totais_pre = 24 * dias_num

        dias_totais_pos = dias_totais_pre + int(hours_minutes_seconds[0])

        horas_formatada = "{}:{}:{}".format(str(dias_totais_pos), str(hours_minutes_seconds[1]), str(hours_minutes_seconds[2]))

    return horas_formatada