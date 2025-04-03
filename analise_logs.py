import sqlite3
import pandas as pd
import os
from datetime import datetime

db_path = os.path.join(os.path.dirname(__file__), "controle_acessos.db")

if os.path.exists(db_path):
    print("\n Banco de dados encontrado:", db_path)
else:
    print("\n ERRO: Banco de dados NÃO encontrado!")
    exit()

# Conectar ao banco de dados
conn = sqlite3.connect(db_path)

# Listar todas as tabelas existentes
tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
print("\n Tabelas no banco de dados:")
print(tables)

# Escolha a tabela correta
table_name = "logs"  # Certifique-se de que esta é a tabela correta

# Verificar estrutura da tabela
df_info = pd.read_sql_query(f"PRAGMA table_info({table_name});", conn)
print(f"\n Estrutura da tabela '{table_name}':")
print(df_info)

# Ler os dados da tabela logs
df_logs = pd.read_sql_query("SELECT * FROM logs;", conn)
conn.close()

# Converter coluna 'horario' para datetime
df_logs["horario"] = pd.to_datetime(df_logs["horario"])

def analisar_acessos_por_dia(data_desejada):
    """Filtra os registros por uma data específica e exibe o número de entradas e saídas, além do total de pessoas distintas que entraram."""
    df_dia = df_logs[df_logs["horario"].dt.date == datetime.strptime(data_desejada, "%Y-%m-%d").date()]
    total_entradas = df_dia[df_dia["tipo"] == "entrada"].shape[0]
    total_saidas = df_dia[df_dia["tipo"] == "saida"].shape[0]
    total_pessoas = df_dia[df_dia["tipo"] == "entrada"]["nome"].nunique()  # Contar colaboradores únicos

    print(f"\n Registros do dia {data_desejada}:")
    print(df_dia)
    print(f"\n No dia {data_desejada}:")
    print(f" Total de entradas: {total_entradas}")
    print(f" Total de saídas: {total_saidas}")
    print(f" Total de pessoas que entraram: {total_pessoas}")  # Nova linha de saída


def calcular_tempo_na_sala(colaborador_nome, data_desejada):
    """Calcula o tempo total dentro da sala para um colaborador específico."""
    df_colaborador = df_logs[(df_logs["nome"] == colaborador_nome) & (df_logs["horario"].dt.date == datetime.strptime(data_desejada, "%Y-%m-%d").date())]
    df_colaborador = df_colaborador.sort_values(by="horario")
    tempos_entrada = df_colaborador[df_colaborador["tipo"] == "entrada"]["horario"].values
    tempo_total = 0
    for i in range(len(tempos_entrada) - 1):
        tempo_total += (tempos_entrada[i + 1] - tempos_entrada[i]).astype("timedelta64[m]")
    print(f"\n {colaborador_nome} permaneceu na sala por aproximadamente {tempo_total} minutos no dia {data_desejada}.")



import argparse

# Criar parser para entrada de argumentos via terminal
parser = argparse.ArgumentParser(description="Analisa acessos de colaboradores")
parser.add_argument("data", type=str, help="Data a ser analisada (formato: YYYY-MM-DD)")
parser.add_argument("colaborador", type=str, nargs="?", default=None, help="Nome do colaborador (opcional)")

args = parser.parse_args()
data_desejada = args.data
colaborador_nome = args.colaborador

# Chamar a função para analisar acessos no dia
analisar_acessos_por_dia(data_desejada)

# Se um colaborador for fornecido, calcular tempo dentro da sala
if colaborador_nome:
    calcular_tempo_na_sala(colaborador_nome, data_desejada)
