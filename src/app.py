import streamlit as st
import pandas as pd
import plotly.express as px
from crud import listar_consultas, inserir_consulta, atualizar_consulta, excluir_consulta, inicializar_banco

# =========================================================
# Inicialização do Banco
# =========================================================

inicializar_banco()
df = listar_consultas()

# =========================================================
# Configurações da página
# =========================================================

st.set_page_config(page_title="Dashboard de Saúde", layout="wide")

st.title("🏥 Dashboard de Saúde - Consultas Médicas")
st.markdown("Este dashboard apresenta insights sobre consultas médicas fictícias (2023-2025).")

# =========================================================
# Funções auxiliares de formatação
# =========================================================

def format_currency(value):
    if value >= 1e6:
        return f"R$ {value/1e6:.1f}M"
    elif value >= 1e3:
        return f"R$ {value/1e3:.1f}k"
    else:
        return f"R$ {value:.1f}"

def format_number(value):
    return f"{value:.1f}"

# =========================================================
# Mapeamentos para entrada/saída
# =========================================================

map_status = {
    "Realizada": "realizada",
    "Cancelada": "cancelada",
    "Não compareceu": "nao compareceu"
}

map_pagamento = {
    "Dinheiro": "Dinheiro",
    "Cartão": "Cartao",
    "Pix": "Pix",
    "Convênio": "Convenio"
}

map_receita = {
    "Sim": "Sim",
    "Não": "Nao"
}

map_sexo = {
    "Masculino": "M",
    "Feminino": "F",
    "Outro": "O"
}

def reverse_map(mapping, value):
    """Retorna a chave (com acento) a partir do valor armazenado (sem acento)."""
    for k, v in mapping.items():
        if v == value:
            return k
    return value


# =========================================================
# Filtros laterais
# =========================================================
st.sidebar.header("Filtros")

estados = st.sidebar.multiselect("Selecione os estados:", df["estado"].unique())
especialidades = st.sidebar.multiselect("Selecione as especialidades:", df["especialidade"].unique())
meses = st.sidebar.multiselect(
    "Selecione os meses:", 
    options=list(range(1, 13)), 
    format_func=lambda x: ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"][x-1]
)

ano = st.sidebar.multiselect("Selecione os anos:", sorted(df["data_consulta"].dt.year.unique()))

df_filtrado = df.copy()
if estados:
    df_filtrado = df_filtrado[df_filtrado["estado"].isin(estados)]
if especialidades:
    df_filtrado = df_filtrado[df_filtrado["especialidade"].isin(especialidades)]
if meses:
    df_filtrado = df_filtrado[df_filtrado["data_consulta"].dt.month.isin(meses)]
if ano:
    df_filtrado = df_filtrado[df_filtrado["data_consulta"].dt.year.isin(ano)]

aba1, aba2 = st.tabs(["📊 Dashboard", "🗂️ Gestão de Consultas"])

# =========================================================
# Volume de consultas ao longo do tempo
# =========================================================
with aba1:
    st.subheader("📊 Volume de Consultas ao longo do tempo")
    consultas_tempo = df_filtrado.groupby([df_filtrado["data_consulta"].dt.to_period("M"), "status_consulta"]).size().reset_index(name="total_consultas")
    consultas_tempo["mês"] = consultas_tempo["data_consulta"].astype(str)

    fig1 = px.line(
        consultas_tempo, x="mês", y="total_consultas", color="status_consulta",
        markers=True, title="Evolução mensal de consultas por status"
    )
    fig1.update_traces(hovertemplate="mês, ano: %{x}<br>Consultas: %{y:.1f}<extra></extra>")
    st.plotly_chart(fig1, use_container_width=True)

    # =========================================================
    # Distribuição de especialidades médicas
    # =========================================================
    st.subheader("🩺 Distribuição de Especialidades Médicas")
    esp = df_filtrado["especialidade"].value_counts().reset_index()
    esp.columns = ["especialidade", "consultas"]

    fig2 = px.bar(
        esp, x="consultas", y="especialidade", orientation="h",
        title="Consultas por Especialidade",
        text=esp["consultas"].apply(format_number)
    )
    fig2.update_traces(textposition="outside", hovertemplate="Consultas: %{x:.1f}<extra></extra>")
    st.plotly_chart(fig2, use_container_width=True)

    # =========================================================
    # Receita por especialidade
    # =========================================================
    st.subheader("💰 Receita por Especialidade")

    # Soma por especialidade
    receita_esp = df_filtrado.groupby("especialidade")["valor_consulta"].sum().reset_index()
    fig3 = px.bar(
        receita_esp, x="especialidade", y="valor_consulta",
        title="Receita total por Especialidade",
        text=receita_esp["valor_consulta"].apply(format_currency)
    )
    fig3.update_traces(textposition="outside", hovertemplate="Receita: R$ %{y:.1f}<extra></extra>")
    fig3.update_yaxes(title="Receita (R$)", tickprefix="R$ ")
    st.plotly_chart(fig3, use_container_width=True)

    # Top 5 especialidades por receita (substitui o antigo Top 10 médicos)
    top_especialidades = (
        df_filtrado.groupby("especialidade")["valor_consulta"]
        .sum()
        .reset_index()
        .sort_values(by="valor_consulta", ascending=False)
        .head(5)
    )

    fig_top5 = px.bar(
        top_especialidades,
        x="valor_consulta",
        y="especialidade",
        orientation="h",
        title="Top 5 Especialidades por Receita",
        text=top_especialidades["valor_consulta"].apply(format_currency)
    )
    fig_top5.update_traces(textposition="outside", hovertemplate="Receita: R$ %{x:.1f}<extra></extra>")
    fig_top5.update_xaxes(title="Receita (R$)", tickprefix="R$ ")
    st.plotly_chart(fig_top5, use_container_width=True)

    # =========================================================
    # Análise geográfica
    # =========================================================
    st.subheader("🌍 Análise Geográfica")
    geo = df_filtrado["estado"].value_counts().reset_index()
    geo.columns = ["estado", "consultas"]

    fig7 = px.bar(
        geo, x="estado", y="consultas",
        title="Número de Consultas por Estado",
        text=geo["consultas"].apply(format_number)
    )
    fig7.update_traces(textposition="outside", hovertemplate="Consultas: %{y:.1f}<extra></extra>")
    st.plotly_chart(fig7, use_container_width=True)

    # =========================================================
    # Perfil dos Pacientes
    # =========================================================
    st.subheader("👨‍👩‍👧 Perfil dos Pacientes")

    # Histograma idade (ajuste no hover)
    fig8 = px.histogram(df_filtrado, x="idade_paciente", nbins=20, title="Distribuição da Idade dos Pacientes")
    fig8.update_traces(
        hovertemplate="Idade: %{x:.0f} anos<br>Total: %{y} pessoas<extra></extra>"
    )
    fig8.update_yaxes(title="Total de Pacientes")
    fig8.update_xaxes(title="Idade (anos)")
    st.plotly_chart(fig8, use_container_width=True)

    # Média idade por especialidade
    idade_esp = df_filtrado.groupby("especialidade")["idade_paciente"].mean().reset_index()
    fig9 = px.bar(
        idade_esp, x="especialidade", y="idade_paciente",
        title="Idade média por Especialidade",
        text=idade_esp["idade_paciente"].apply(format_number)
    )
    fig9.update_traces(textposition="outside", hovertemplate="Idade média: %{y:.1f}<extra></extra>")
    st.plotly_chart(fig9, use_container_width=True)

    # =========================================================
    #  Tempo de espera
    # =========================================================
    st.subheader("⏱️ Tempo de Espera")

    fig11 = px.box(df_filtrado, x="especialidade", y="tempo_espera_min", title="Tempo de espera por Especialidade")
    fig11.update_traces(hovertemplate="Tempo: %{y:.1f} min<extra></extra>")
    st.plotly_chart(fig11, use_container_width=True)

    # Correlação espera x satisfação
    corr = df_filtrado.dropna(subset=["satisfacao_paciente"])
    fig12 = px.scatter(
        corr, x="tempo_espera_min", y="satisfacao_paciente", color="especialidade",
        title="Correlação entre tempo de espera e satisfação"
    )
    fig12.update_traces(hovertemplate="Espera: %{x:.1f} min<br>Satisfação: %{y:.1f}<extra></extra>")
    st.plotly_chart(fig12, use_container_width=True)

    # =========================================================
    #  Satisfação dos pacientes
    # =========================================================
    st.subheader("⭐ Satisfação dos Pacientes")

    sat_esp = df_filtrado.groupby("especialidade")["satisfacao_paciente"].mean().reset_index()
    fig13 = px.bar(
        sat_esp, x="especialidade", y="satisfacao_paciente",
        title="Satisfação média por Especialidade",
        text=sat_esp["satisfacao_paciente"].apply(format_number)
    )
    fig13.update_traces(textposition="outside", hovertemplate="Satisfação: %{y:.1f}<extra></extra>")
    st.plotly_chart(fig13, use_container_width=True)

    sat_sexo = df_filtrado.groupby("sexo_paciente")["satisfacao_paciente"].mean().reset_index()
    fig14 = px.bar(
        sat_sexo, x="sexo_paciente", y="satisfacao_paciente",
        title="Satisfação média por Sexo",
        text=sat_sexo["satisfacao_paciente"].apply(format_number)
    )
    fig14.update_traces(textposition="outside", hovertemplate="Satisfação: %{y:.1f}<extra></extra>")
    st.plotly_chart(fig14, use_container_width=True)

    sat_estado = df_filtrado.groupby("estado")["satisfacao_paciente"].mean().reset_index()
    fig15 = px.bar(
        sat_estado, x="estado", y="satisfacao_paciente",
        title="Satisfação média por Estado",
        text=sat_estado["satisfacao_paciente"].apply(format_number)
    )
    fig15.update_traces(textposition="outside", hovertemplate="Satisfação: %{y:.1f}<extra></extra>")
    st.plotly_chart(fig15, use_container_width=True)

    # =========================================================
    #  Receita de medicação
    # =========================================================
    st.subheader("💊 Receita de Medicação")

    receita_percentual = df_filtrado["receita_medicacao"].value_counts(normalize=True).reset_index()
    receita_percentual.columns = ["receita_medicacao", "percentual"]

    fig16 = px.pie(receita_percentual, names="receita_medicacao", values="percentual", title="Percentual de Consultas com Receita")
    fig16.update_traces(textinfo="label+percent", hovertemplate="%{label}: %{percent:.1%}<extra></extra>")
    st.plotly_chart(fig16, use_container_width=True)

    receita_esp = df_filtrado[df_filtrado["receita_medicacao"] == "Sim"].groupby("especialidade").size().reset_index(name="receitas")
    fig17 = px.bar(
        receita_esp, x="especialidade", y="receitas",
        title="Receitas de Medicação por Especialidade",
        text=receita_esp["receitas"].apply(format_number)
    )
    fig17.update_traces(textposition="outside", hovertemplate="Receitas: %{y:.1f}<extra></extra>")
    st.plotly_chart(fig17, use_container_width=True)

    receita_estado = df_filtrado[df_filtrado["receita_medicacao"] == "Sim"].groupby("estado").size().reset_index(name="receitas")
    fig18 = px.bar(
        receita_estado, x="estado", y="receitas",
        title="Receitas de Medicação por Estado",
        text=receita_estado["receitas"].apply(format_number)
    )
    fig18.update_traces(textposition="outside", hovertemplate="Receitas: %{y:.1f}<extra></extra>")
    st.plotly_chart(fig18, use_container_width=True)

# =========================================================
# CRUD - Gestão de Consultas
# =========================================================

with aba2:
    st.header("🗂️ Gestão de Consultas (CRUD)")

    # ----------------------------
    # 1. Cadastro
    with st.expander("➕ Cadastrar nova consulta"):
        with st.form("form_cadastro", clear_on_submit=False):
            id_paciente = st.number_input("ID do paciente:", min_value=1001, step=1)
            id_medico = st.number_input("ID do médico:", min_value=1, step=1)
            data = st.date_input("Data da consulta")
            estado = st.selectbox("Estado", df["estado"].unique())
            cidade = st.text_input("Cidade")
            especialidade = st.selectbox("Especialidade", df["especialidade"].unique())
            idade = st.number_input("Idade do paciente", min_value=0, max_value=120)
            sexo = st.selectbox("Sexo do paciente", list(map_sexo.keys()))
            valor = st.number_input("Valor da consulta (R$)", min_value=0.0, step=50.0)
            forma_pagamento = st.selectbox("Forma de pagamento", list(map_pagamento.keys()))
            tempo_espera = st.number_input("Tempo de espera (min)", min_value=0, step=1)
            satisfacao = st.slider("Satisfação do paciente (0 a 5)", 0, 5, 1)
            receita = st.selectbox("Receita de medicação", list(map_receita.keys()))
            status = st.selectbox("Status da consulta", list(map_status.keys()))

            cadastrar = st.form_submit_button("Salvar", use_container_width=True)

        if cadastrar:
            inserir_consulta((
                id_paciente, id_medico, str(data), estado, cidade,
                especialidade, idade, map_sexo[sexo], valor, map_pagamento[forma_pagamento],
                tempo_espera, satisfacao, map_receita[receita], map_status[status]
            ))
            st.success("✅ Consulta cadastrada com sucesso!")
            st.rerun()

    # ----------------------------
    # 2. Visualizar
    st.subheader("📋 Consultas registradas")
    st.dataframe(df)

    # ----------------------------
    # 3. Atualizar
    with st.expander("✏️ Atualizar consulta"):
        if not df.empty:
            id_update = st.selectbox("Escolha a consulta pelo ID:", df["id_consulta"].tolist(), key="update")
            registro = df[df["id_consulta"] == int(id_update)].iloc[0]

            with st.form("form_update", clear_on_submit=False):
                novo_paciente = st.number_input("ID do paciente", value=int(registro["id_paciente"]))
                novo_medico = st.number_input("ID do médico", value=int(registro["id_medico"]))
                nova_data = st.date_input("Data da consulta", registro["data_consulta"].date())
                novo_estado = st.selectbox("Estado", df["estado"].unique(), index=list(df["estado"].unique()).index(registro["estado"]))
                nova_cidade = st.text_input("Cidade", registro["cidade"])
                nova_especialidade = st.selectbox("Especialidade", df["especialidade"].unique(), index=list(df["especialidade"].unique()).index(registro["especialidade"]))
                nova_idade = st.number_input("Idade do paciente", value=int(registro["idade_paciente"]))
                novo_sexo = st.selectbox("Sexo", list(map_sexo.keys()),
                                         index=list(map_sexo.values()).index(registro["sexo_paciente"]))
                novo_valor = st.number_input("Valor", value=float(registro["valor_consulta"]))
                nova_forma = st.selectbox("Forma de pagamento", list(map_pagamento.keys()),
                                          index=list(map_pagamento.values()).index(registro["forma_pagamento"]))
                novo_tempo = st.number_input("Tempo de espera (min)", value=int(registro["tempo_espera_min"]))
                nova_satisfacao = st.slider("Satisfação", 0, 5, int(registro["satisfacao_paciente"]) if pd.notna(registro["satisfacao_paciente"]) else 5)
                nova_receita = st.selectbox("Receita de medicação", list(map_receita.keys()),
                                            index=list(map_receita.values()).index(registro["receita_medicacao"]))
                novo_status = st.selectbox("Status", list(map_status.keys()),
                                           index=list(map_status.values()).index(registro["status_consulta"]))

                atualizar = st.form_submit_button("Atualizar", use_container_width=True)

            if atualizar:
                atualizar_consulta(int(id_update), (
                    novo_paciente, novo_medico, str(nova_data), novo_estado, nova_cidade,
                    nova_especialidade, nova_idade, map_sexo[novo_sexo], novo_valor, map_pagamento[nova_forma],
                    novo_tempo, nova_satisfacao, map_receita[nova_receita], map_status[novo_status]
                ))
                st.success(f"✅ Consulta {id_update} atualizada!")
                st.rerun()

    # ----------------------------
    # 4. Excluir
    with st.expander("🗑️ Excluir consulta"):
        if not df.empty:
            id_delete = st.selectbox("Escolha a consulta pelo ID:", df["id_consulta"].tolist(), key="delete")

            if id_delete:
                registro = df[df["id_consulta"] == int(id_delete)].iloc[0]
                st.info(f"""
                Consulta selecionada:
                • Paciente: {registro['id_paciente']}
                • Cidade: {registro['cidade']} - {registro['estado']}
                • Especialidade: {registro['especialidade']}
                • Sexo: {reverse_map(map_sexo, registro['sexo_paciente'])}
                • Forma de Pagamento: {reverse_map(map_pagamento, registro['forma_pagamento'])}
                • Status: {reverse_map(map_status, registro['status_consulta'])}
                • Receita: {reverse_map(map_receita, registro['receita_medicacao'])}
                • Satisfação: {registro['satisfacao_paciente']}
                """)

                confirmar = st.checkbox("✅ Confirmo exclusão", key="confirm_delete")

                if st.button("Excluir", use_container_width=True, key="btn_excluir"):
                    if confirmar:
                        excluir_consulta(int(id_delete))
                        st.success(f"✅ Consulta {id_delete} excluída!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Confirme a exclusão antes de prosseguir.")
