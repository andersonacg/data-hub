# pages/dashboard.py
import streamlit as st
import pandas as pd  # Certifique-se de que está aqui
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import calendar
from database.db_manager import format_currency

def show_dashboard(db):
    st.title("Dashboard Financeiro")
    
    df = db.get_transactions()
    
    if df.empty:
        st.info("Nenhuma transação encontrada. Adicione transações na página 'Transações'.")
        return
    
    df['data'] = pd.to_datetime(df['data'])
    
    hoje = datetime.now()
    primeiro_dia = datetime(hoje.year, hoje.month, 1)
    ultimo_dia = datetime(hoje.year, hoje.month, calendar.monthrange(hoje.year, hoje.month)[1])
    
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data inicial", value=primeiro_dia)
    with col2:
        data_fim = st.date_input("Data final", value=ultimo_dia)
    
    mask = (df['data'] >= pd.to_datetime(data_inicio)) & (df['data'] <= pd.to_datetime(data_fim))
    df_filtrado = df.loc[mask]
    
    if df_filtrado.empty:
        st.info(f"Nenhuma transação encontrada no período de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}.")
        return
    
    receitas = df_filtrado[df_filtrado['tipo'] == 'receita']['valor'].sum()
    despesas = df_filtrado[df_filtrado['tipo'] == 'despesa']['valor'].sum()
    saldo = receitas - despesas
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Receitas", format_currency(receitas))
    col2.metric("Despesas", format_currency(despesas))
    col3.metric("Saldo", format_currency(saldo),
               delta=f"{(saldo/receitas*100 if receitas > 0 else 0):.1f}%" if receitas > 0 else "0%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Despesas por Categoria")
        despesas_por_categoria = df_filtrado[df_filtrado['tipo'] == 'despesa'].groupby('categoria')['valor'].sum().reset_index()
        if not despesas_por_categoria.empty:
            despesas_por_categoria = despesas_por_categoria.sort_values('valor', ascending=False)
            fig = px.pie(
                despesas_por_categoria,
                values='valor',
                names='categoria',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há despesas no período selecionado.")
    
    with col2:
        st.subheader("Receitas vs Despesas")
        df_diario = df_filtrado.groupby([df_filtrado['data'].dt.date, 'tipo'])['valor'].sum().reset_index()
        if not df_diario.empty:
            df_diario_pivot = df_diario.pivot(index='data', columns='tipo', values='valor').reset_index()
            df_diario_pivot.fillna(0, inplace=True)
            
            if 'receita' not in df_diario_pivot.columns:
                df_diario_pivot['receita'] = 0
            if 'despesa' not in df_diario_pivot.columns:
                df_diario_pivot['despesa'] = 0
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_diario_pivot['data'],
                y=df_diario_pivot['receita'],
                name='Receitas',
                marker_color='#76D7C4'
            ))
            fig.add_trace(go.Bar(
                x=df_diario_pivot['data'],
                y=df_diario_pivot['despesa'],
                name='Despesas',
                marker_color='#F5B7B1'
            ))
            fig.update_layout(barmode='group', margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há dados suficientes para o gráfico de comparação.")
    
    st.markdown("---")
    st.subheader("Últimas Transações")
    
    df_display = df_filtrado.sort_values('data', ascending=False).head(10)
    df_display['data'] = df_display['data'].dt.strftime('%d/%m/%Y')
    df_display['valor'] = df_display['valor'].apply(format_currency)
    
    st.dataframe(
        df_display[['data', 'descricao', 'categoria', 'valor', 'tipo']],
        column_config={
            "data": "Data",
            "descricao": "Descrição",
            "categoria": "Categoria",
            "valor": "Valor",
            "tipo": "Tipo"
        },
        use_container_width=True
    )