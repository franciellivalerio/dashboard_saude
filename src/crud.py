import pandas as pd
from database import create_connection, create_table

# =========================================================
# Operações CRUD
# =========================================================
def listar_consultas():
    conn = create_connection()
    df = pd.read_sql_query("SELECT * FROM consultas", conn)
    conn.close()
    df["data_consulta"] = pd.to_datetime(df["data_consulta"], errors="coerce")
    return df

def inserir_consulta(dados):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO consultas (
        id_paciente, id_medico, data_consulta, estado, cidade,
        especialidade, idade_paciente, sexo_paciente, valor_consulta,
        forma_pagamento, tempo_espera_min, satisfacao_paciente,
        receita_medicacao, status_consulta
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, dados)
    conn.commit()
    conn.close()

def atualizar_consulta(id_consulta, dados):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE consultas SET
        id_paciente=?, id_medico=?, data_consulta=?, estado=?, cidade=?,
        especialidade=?, idade_paciente=?, sexo_paciente=?, valor_consulta=?,
        forma_pagamento=?, tempo_espera_min=?, satisfacao_paciente=?,
        receita_medicacao=?, status_consulta=?
    WHERE id_consulta=?
    """, dados + (id_consulta,))
    conn.commit()
    conn.close()

def excluir_consulta(id_consulta):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM consultas WHERE id_consulta=?", (id_consulta,))
    conn.commit()
    conn.close()

# =========================================================
# Importar CSV inicial (só se banco estiver vazio)
# =========================================================
def importar_csv_para_banco():
    df_csv = pd.read_csv("data/dataset_saude.csv")
    df_csv["data_consulta"] = pd.to_datetime(df_csv["data_consulta"], errors="coerce")

    conn = create_connection()
    cursor = conn.cursor()

    for _, row in df_csv.iterrows():
        cursor.execute("""
        INSERT INTO consultas (
            id_paciente, id_medico, data_consulta, estado, cidade,
            especialidade, idade_paciente, sexo_paciente, valor_consulta,
            forma_pagamento, tempo_espera_min, satisfacao_paciente,
            receita_medicacao, status_consulta
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(row["id_paciente"]),
            int(row["id_medico"]),
            str(row["data_consulta"].date()) if pd.notna(row["data_consulta"]) else None,
            row["estado"],
            row["cidade"],
            row["especialidade"],
            int(row["idade_paciente"]),
            row["sexo_paciente"],
            float(row["valor_consulta"]),
            row["forma_pagamento"],
            int(row["tempo_espera_min"]),
            float(row["satisfacao_paciente"]) if pd.notna(row["satisfacao_paciente"]) else None,
            row["receita_medicacao"],
            row["status_consulta"]
        ))
    conn.commit()
    conn.close()

def inicializar_banco():
    create_table()

    # Verifica se o banco está vazio
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM consultas")
    count = cursor.fetchone()[0]
    conn.close()

    # Se estiver vazio, importa os dados do CSV
    if count == 0:
        importar_csv_para_banco()
