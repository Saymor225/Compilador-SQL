import csv
import os

def get_csv_path(table_name):
    return f"{table_name}.csv"

def executar(consulta):
    try:
        if consulta['type'] == 'select':
            if consulta['columns'] == ['COUNT(*)']:
                executar_count(consulta)
            else:
                executar_select(consulta)
        elif consulta['type'] == 'insert':
            executar_insert(consulta)
        elif consulta['type'] == 'update':
            executar_update(consulta)
        elif consulta['type'] == 'delete':
            executar_delete(consulta)
    except Exception as e:
        print(f'Erro durante execução: {e}')

def executar_select(consulta):
    table_name = consulta['table']
    arquivo = get_csv_path(table_name)
    colunas = consulta['columns']
    condicao = consulta['where']
    order_by = consulta['order_by']

    try:
        with open(arquivo, newline='', encoding='utf-8') as csvfile:
            leitor = csv.DictReader(csvfile)
            resultado = []

            for linha in leitor:
                if condicao is None or verifica_condicao(linha, condicao):
                    if colunas == ['*']:
                        resultado.append(linha)
                    else:
                        resultado.append({col: linha[col] for col in colunas})

            if order_by:
                resultado = ordenar_resultado(resultado, order_by)

            imprimir_resultado(resultado, colunas)

    except FileNotFoundError:
        print(f'Tabela "{table_name}" não encontrada (arquivo: {arquivo})')
    except KeyError as e:
        print(f'Coluna inexistente: {e}')

def executar_count(consulta):
    table_name = consulta['table']
    arquivo = get_csv_path(table_name)
    condicao = consulta['where']

    try:
        with open(arquivo, newline='', encoding='utf-8') as csvfile:
            leitor = csv.DictReader(csvfile)
            contador = 0

            for linha in leitor:
                if condicao is None or verifica_condicao(linha, condicao):
                    contador += 1

            print(f"Total de registros: {contador}")

    except FileNotFoundError:
        print(f'Tabela "{table_name}" não encontrada (arquivo: {arquivo})')
    except KeyError as e:
        print(f'Coluna inexistente: {e}')

def executar_insert(consulta):
    table_name = consulta['table']
    arquivo = get_csv_path(table_name)
    colunas = consulta['columns']
    valores = consulta['values']

    try:
        file_exists = os.path.isfile(arquivo)
        
        with open(arquivo, 'a', newline='', encoding='utf-8') as csvfile:
            if colunas is None and file_exists:
                with open(arquivo, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    colunas = next(reader)
            
            writer = csv.DictWriter(csvfile, fieldnames=colunas)
            
            if not file_exists:
                writer.writeheader()
            
            linha = dict(zip(colunas, valores))
            writer.writerow(linha)
            print("1 registro inserido.")

    except Exception as e:
        print(f'Erro durante inserção: {e}')

def executar_update(consulta):
    table_name = consulta['table']
    arquivo = get_csv_path(table_name)
    set_list = consulta['set']
    condicao = consulta['where']

    try:
        with open(arquivo, 'r', newline='', encoding='utf-8') as csvfile:
            leitor = csv.DictReader(csvfile)
            linhas = list(leitor)
            fieldnames = leitor.fieldnames

        atualizados = 0
        for linha in linhas:
            if condicao is None or verifica_condicao(linha, condicao):
                for col, val in set_list.items():
                    linha[col] = val
                atualizados += 1

        with open(arquivo, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(linhas)

        print(f"{atualizados} registros atualizados.")

    except FileNotFoundError:
        print(f'Tabela "{table_name}" não encontrada (arquivo: {arquivo})')
    except KeyError as e:
        print(f'Coluna inexistente: {e}')

def executar_delete(consulta):
    table_name = consulta['table']
    arquivo = get_csv_path(table_name)
    condicao = consulta['where']

    try:
        with open(arquivo, 'r', newline='', encoding='utf-8') as csvfile:
            leitor = csv.DictReader(csvfile)
            linhas = list(leitor)
            fieldnames = leitor.fieldnames

        linhas_filtradas = [linha for linha in linhas 
                          if condicao is None or not verifica_condicao(linha, condicao)]

        removidos = len(linhas) - len(linhas_filtradas)

        with open(arquivo, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(linhas_filtradas)

        print(f"{removidos} registros removidos.")

    except FileNotFoundError:
        print(f'Tabela "{table_name}" não encontrada (arquivo: {arquivo})')
    except KeyError as e:
        print(f'Coluna inexistente: {e}')

def verifica_condicao(linha, cond):
    if 'operator' in cond and cond['operator'] in ['AND', 'OR', 'NOT']:
        if cond['operator'] == 'AND':
            return verifica_condicao(linha, cond['left']) and verifica_condicao(linha, cond['right'])
        elif cond['operator'] == 'OR':
            return verifica_condicao(linha, cond['left']) or verifica_condicao(linha, cond['right'])
        elif cond['operator'] == 'NOT':
            return not verifica_condicao(linha, cond['condition'])
    else:
        valor = linha[cond['column']]
        alvo = cond['value']
        operador = cond['operator']

        try:
            valor = float(valor)
            alvo = float(alvo)
        except ValueError:
            pass

        if operador == '=':
            return valor == alvo
        elif operador == '!=':
            return valor != alvo
        elif operador == '>':
            return valor > alvo
        elif operador == '<':
            return valor < alvo
        elif operador == '>=':
            return valor >= alvo
        elif operador == '<=':
            return valor <= alvo
        else:
            return False

def ordenar_resultado(resultado, order_by):
    for ordem in reversed(order_by):
        coluna = ordem['column']
        direcao = ordem['direction']
        resultado.sort(key=lambda x: x[coluna], reverse=(direcao == 'DESC'))
    return resultado

def imprimir_resultado(linhas, colunas):
    if not linhas:
        print("Nenhum resultado encontrado.")
        return

    if colunas == ['*']:
        colunas = list(linhas[0].keys())

    print(" | ".join(colunas))
    print("-" * 40)

    for linha in linhas:
        print(" | ".join(str(linha[col]) for col in colunas))