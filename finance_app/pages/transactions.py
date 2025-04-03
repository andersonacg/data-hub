# pages/transactions.py
import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_manager import format_currency  # Ajustado

def show_transactions(db):
    st.title("Gerenciar Transações")
    
    st.subheader("Adicionar Nova Transação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        data = st.date_input("Data", value=datetime.now())
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor", min_value=0.01, step=0.01)
    
    with col2:
        categorias_df = db.get_categories()
        categorias_receita = categorias_df[categorias_df['tipo'] == 'receita']['nome'].tolist()
        categorias_despesa = categorias_df[categorias_df['tipo'] == 'despesa']['nome'].tolist()
        
        tipo = st.selectbox("Tipo", ["Despesa", "Receita"])
        if tipo == "Receita":
            categoria = st.selectbox("Categoria", categorias_receita)
            tipo_db = "receita"
        else:
            categoria = st.selectbox("Categoria", categorias_despesa)
            tipo_db = "despesa"
    
    if st.button("Adicionar Transação"):
        if not descricao:
            st.error("Por favor, insira uma descrição.")
        elif valor <= 0:
            st.error("O valor deve ser maior que zero.")
        else:
            data_str = data.strftime("%Y-%m-%d")
            db.add_transaction(data_str, descricao, valor, categoria, tipo_db)
            st.success(f"Transação '{descricao}' adicionada com sucesso!")
    
    st.markdown("---")
    st.subheader("Transações Recentes")
    
    df = db.get_transactions()
    
    if not df.empty:
        df['data'] = pd.to_datetime(df['data']).dt.strftime('%d/%m/%Y')
        df['valor'] = df['valor'].apply(format_currency)
        df['tipo'] = df['tipo'].apply(lambda x: "💰 Receita" if x == "receita" else "💸 Despesa")
        
        st.dataframe(
            df[['data', 'descricao', 'categoria', 'valor', 'tipo']],
            column_config={
                "data": "Data",
                "descricao": "Descrição",
                "categoria": "Categoria",
                "valor": "Valor",
                "tipo": "Tipo"
            },
            use_container_width=True
        )
    else:
        st.info("Nenhuma transação encontrada. Adicione sua primeira transação acima.")