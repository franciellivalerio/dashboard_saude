import sqlite3

# Conexão com o banco
def create_connection():
    return sqlite3.connect("consultas.db", check_same_thread=False)

# Criar tabela se não existir
def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS consultas (
        id_consulta INTEGER PRIMARY KEY AUTOINCREMENT,
        id_paciente INTEGER,
        id_medico INTEGER,
        data_consulta TEXT,
        estado TEXT,
        cidade TEXT,
        especialidade TEXT,
        idade_paciente INTEGER,
        sexo_paciente TEXT,
        valor_consulta REAL,
        forma_pagamento TEXT,
        tempo_espera_min INTEGER,
        satisfacao_paciente REAL,
        receita_medicacao TEXT,
        status_consulta TEXT
    )
    """)
    conn.commit()
    conn.close()
