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
                "Data de atribuicao": str(list_results[i][6]),
                "Data de entrega": str(list_results[i][7]),
                "Data resolvido": str(list_results[i][8]),
                "Delta_tempo":str(list_results[i][2]),
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
