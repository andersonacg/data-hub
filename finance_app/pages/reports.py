# pages/reports.py
import streamlit as st
import pandas as pd  # Certifique-se de que está aqui
import plotly.express as px
from database.db_manager import format_currency, get_month_name

def show_reports(db):
    st.title("Relatórios Financeiros")
    
    df = db.get_transactions()
    
    if df.empty:
        st.info("Nenhuma transação encontrada. Adicione transações na página 'Transações'.")
        return
    
    df['data'] = pd.to_datetime(df['data'])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        anos = sorted(df['data'].dt.year.unique().tolist(), reverse=True)
        ano_selecionado = st.selectbox("Ano", anos)
    
    with col2:
        meses_disponiveis = df[df['data'].dt.year == ano_selecionado]['data'].dt.month.unique().tolist()
        mes_selecionado = st.selectbox("Mês", meses_disponiveis, format_func=get_month_name)
    
    with col3:
        tipo_selecionado = st.selectbox("Tipo", ["Todos", "Receitas", "Despesas"])
    
    mask = (df['data'].dt.year == ano_selecionado) & (df['data'].dt.month == mes_selecionado)
    df_filtrado = df.loc[mask]
    
    if tipo_selecionado == "Receitas":
        df_filtrado = df_filtrado[df_filtrado['tipo'] == 'receita']
    elif tipo_selecionado == "Despesas":
        df_filtrado = df_filtrado[df_filtrado['tipo'] == 'despesa']
    
    if df_filtrado.empty:
        st.info(f"Nenhuma transação encontrada para {get_month_name(mes_selecionado)} de {ano_selecionado}.")
        return
    
    receitas = df_filtrado[df_filtrado['tipo'] == 'receita']['valor'].sum()
    despesas = df_filtrado[df_filtrado['tipo'] == 'despesa']['valor'].sum()
    saldo = receitas - despesas
    
    st.markdown(f"## Resumo de {get_month_name(mes_selecionado)} de {ano_selecionado}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Receitas", format_currency(receitas))
    col2.metric("Despesas", format_currency(despesas))
    col3.metric("Saldo", format_currency(saldo),
               delta=f"{(saldo/receitas*100 if receitas > 0 else 0):.1f}%" if receitas > 0 else "0%")
    
    st.markdown("---")
    
    st.subheader("Análise por Categoria")
    
    if tipo_selecionado != "Receitas":
        despesas_por_categoria = df_filtrado[df_filtrado['tipo'] == 'despesa'].groupby('categoria')['valor'].sum().reset_index()
        if not despesas_por_categoria.empty:
            despesas_por_categoria = despesas_por_categoria.sort_values('valor', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Despesas por Categoria")
                fig = px.pie(
                    despesas_por_categoria,
                    values='valor',
                    names='categoria',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Maiores Despesas")
                despesas_por_categoria['valor'] = despesas_por_categoria['valor'].apply(format_currency)
                despesas_por_categoria = despesas_por_categoria.rename(columns={'categoria': 'Categoria', 'valor': 'Valor'})
                st.dataframe(despesas_por_categoria, use_container_width=True)
    
    if tipo_selecionado != "Despesas":
        receitas_por_categoria = df_filtrado[df_filtrado['tipo'] == 'receita'].groupby('categoria')['valor'].sum().reset_index()
        if not receitas_por_categoria.empty:
            receitas_por_categoria = receitas_por_categoria.sort_values('valor', ascending=False)
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Receitas por Categoria")
                fig = px.pie(
                    receitas_por_categoria,
                    values='valor',
                    names='categoria',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Maiores Receitas")
                receitas_por_categoria['valor'] = receitas_por_categoria['valor'].apply(format_currency)
                receitas_por_categoria = receitas_por_categoria.rename(columns={'categoria': 'Categoria', 'valor': 'Valor'})
                st.dataframe(receitas_por_categoria, use_container_width=True)
    
    st.markdown("---")
    st.subheader(f"Todas as Transações de {get_month_name(mes_selecionado)}")
    
    df_display = df_filtrado.copy()
    df_display['data'] = df_display['data'].dt.strftime('%d/%m/%Y')
    df_display['valor'] = df_display['valor'].apply(format_currency)
    
    st.dataframe(
        df_display[['data', 'descricao', 'categoria', 'valor', 'tipo']].sort_values('data'),
        column_config={
            "data": "Data",
            "descricao": "Descrição",
            "categoria": "Categoria",
            "valor": "Valor",
            "tipo": "Tipo"
        },
        use_container_width=True
    )
    
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download dos dados (CSV)",
        data=csv,
        file_name=f'financas_{get_month_name(mes_selecionado)}_{ano_selecionado}.csv',
        mime='text/csv',
    )