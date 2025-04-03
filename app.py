# app.py - Arquivo principal unificado
import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

# Configuração da página
st.set_page_config(
    page_title="Controle Financeiro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funções de utilidade
def format_currency(value, symbol="R$"):
    """Formata um valor para exibição como moeda"""
    return f"{symbol} {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def get_month_name(month_number):
    """Retorna o nome do mês em português"""
    months = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    return months.get(month_number, '')

# Classe para gerenciar o banco de dados
class DatabaseManager:
    def __init__(self, db_path="./data/finance.db"):
        # Garante que o diretório existe
        directory = os.path.dirname(db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        self.db_path = db_path
        self.setup_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def setup_database(self):
        """Cria as tabelas necessárias se não existirem"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Cria tabela de categorias
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            cor TEXT DEFAULT '#808080'
        )
        ''')
        
        # Cria tabela de transações
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id_transacao INTEGER PRIMARY KEY,
            data TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            categoria_id INTEGER,
            tipo TEXT NOT NULL,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id_categoria)
        )
        ''')
        
        # Insere categorias padrão se a tabela estiver vazia
        cursor.execute("SELECT COUNT(*) FROM categorias")
        if cursor.fetchone()[0] == 0:
            categorias_padrao = [
                ('Alimentação', 'despesa', '#FF5733'),
                ('Transporte', 'despesa', '#33A8FF'),
                ('Moradia', 'despesa', '#33FF57'),
                ('Lazer', 'despesa', '#FF33A8'),
                ('Saúde', 'despesa', '#A833FF'),
                ('Educação', 'despesa', '#FFFF33'),
                ('Salário', 'receita', '#33FFA8'),
                ('Investimentos', 'receita', '#A8FF33'),
                ('Outros', 'despesa', '#808080')
            ]
            cursor.executemany(
                "INSERT INTO categorias (nome, tipo, cor) VALUES (?, ?, ?)",
                categorias_padrao
            )
        
        conn.commit()
        conn.close()

    def get_transactions(self):
        """Retorna todas as transações como DataFrame"""
        conn = self.get_connection()
        query = '''
        SELECT t.id_transacao, t.data, t.descricao, t.valor, c.nome as categoria, t.tipo
        FROM transacoes t
        LEFT JOIN categorias c ON t.categoria_id = c.id_categoria
        ORDER BY t.data DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def add_transaction(self, data, descricao, valor, categoria, tipo):
        """Adiciona uma nova transação"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtém o ID da categoria
        cursor.execute("SELECT id_categoria FROM categorias WHERE nome = ?", (categoria,))
        result = cursor.fetchone()
        if result:
            categoria_id = result[0]
        else:
            # Se a categoria não existir, usa "Outros"
            cursor.execute("SELECT id_categoria FROM categorias WHERE nome = 'Outros'")
            categoria_id = cursor.fetchone()[0]
        
        # Insere a transação
        cursor.execute('''
        INSERT INTO transacoes (data, descricao, valor, categoria_id, tipo)
        VALUES (?, ?, ?, ?, ?)
        ''', (data, descricao, valor, categoria_id, tipo))
        
        conn.commit()
        conn.close()
    
    def get_categories(self):
        """Retorna todas as categorias"""
        conn = self.get_connection()
        query = "SELECT nome, tipo, cor FROM categorias ORDER BY nome"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

# Inicializa o banco de dados
db = DatabaseManager()

# Função para mostrar o Dashboard
def show_dashboard():
    st.title("Dashboard Financeiro")
    
    # Obtém as transações
    df = db.get_transactions()
    
    # Se não houver dados, mostra mensagem
    if df.empty:
        st.info("Nenhuma transação encontrada. Adicione transações na página 'Transações'.")
        return
    
    # Converte a coluna de data para datetime
    df['data'] = pd.to_datetime(df['data'])
    
    # Obtém o mês atual para filtrar
    hoje = datetime.now()
    primeiro_dia = datetime(hoje.year, hoje.month, 1)
    ultimo_dia = datetime(hoje.year, hoje.month, calendar.monthrange(hoje.year, hoje.month)[1])
    
    # Filtro de período
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data inicial", value=primeiro_dia)
    with col2:
        data_fim = st.date_input("Data final", value=ultimo_dia)
    
    # Filtra por período
    mask = (df['data'] >= pd.to_datetime(data_inicio)) & (df['data'] <= pd.to_datetime(data_fim))
    df_filtrado = df.loc[mask]
    
    # Se não houver dados no período, mostra mensagem
    if df_filtrado.empty:
        st.info(f"Nenhuma transação encontrada no período de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}.")
        return
    
    # Calcula receitas e despesas
    receitas = df_filtrado[df_filtrado['tipo'] == 'receita']['valor'].sum()
    despesas = df_filtrado[df_filtrado['tipo'] == 'despesa']['valor'].sum()
    saldo = receitas - despesas
    
    # Métricas principais
    col1, col2, col3 = st.columns(3)
    col1.metric("Receitas", f"R$ {receitas:.2f}".replace('.', ','))
    col2.metric("Despesas", f"R$ {despesas:.2f}".replace('.', ','))
    col3.metric("Saldo", f"R$ {saldo:.2f}".replace('.', ','),
               delta=f"{(saldo/receitas*100 if receitas > 0 else 0):.1f}%" if receitas > 0 else "0%")
    
    st.markdown("---")
    
    # Gráficos
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
        # Agrupa por dia
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
    
    # Tabela com as últimas transações
    st.markdown("---")
    st.subheader("Últimas Transações")
    
    df_display = df_filtrado.sort_values('data', ascending=False).head(10)
    df_display['data'] = df_display['data'].dt.strftime('%d/%m/%Y')
    df_display['valor'] = df_display['valor'].apply(lambda x: f"R$ {x:.2f}".replace('.', ','))
    
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

# Função para mostrar a página de Transações
def show_transactions():
    st.title("Gerenciar Transações")
    
    # Interface para adicionar transações
    st.subheader("Adicionar Nova Transação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        data = st.date_input("Data", value=datetime.now())
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor", min_value=0.01, step=0.01)
    
    with col2:
        # Obtém categorias do banco de dados
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
            # Formata a data para string
            data_str = data.strftime("%Y-%m-%d")
            
            # Adiciona a transação
            db.add_transaction(data_str, descricao, valor, categoria, tipo_db)
            st.success(f"Transação '{descricao}' adicionada com sucesso!")
    
    # Exibe as transações
    st.markdown("---")
    st.subheader("Transações Recentes")
    
    df = db.get_transactions()
    
    if not df.empty:
        # Converte a coluna de data para datetime e depois formata para exibição
        df['data'] = pd.to_datetime(df['data']).dt.strftime('%d/%m/%Y')
        
        # Formata o valor
        df['valor'] = df['valor'].apply(lambda x: f"R$ {x:.2f}".replace('.', ','))
        
        # Adiciona ícone para o tipo
        df['tipo'] = df['tipo'].apply(lambda x: "💰 Receita" if x == "receita" else "💸 Despesa")
        
        # Exibe a tabela
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

# Função para mostrar a página de Relatórios
def show_reports():
    st.title("Relatórios Financeiros")
    
    # Obtém as transações
    df = db.get_transactions()
    
    # Se não houver dados, mostra mensagem
    if df.empty:
        st.info("Nenhuma transação encontrada. Adicione transações na página 'Transações'.")
        return
    
    # Converte a coluna de data para datetime
    df['data'] = pd.to_datetime(df['data'])
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Obtém a lista de anos disponíveis
        anos = sorted(df['data'].dt.year.unique().tolist(), reverse=True)
        ano_selecionado = st.selectbox("Ano", anos)
    
    with col2:
        # Obtém a lista de meses disponíveis para o ano selecionado
        meses_disponiveis = df[df['data'].dt.year == ano_selecionado]['data'].dt.month.unique().tolist()
        meses_nomes = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 
                       5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 
                       9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        
        meses_opcoes = [(m, meses_nomes[m]) for m in meses_disponiveis]
        mes_selecionado = st.selectbox(
            "Mês", 
            options=[m[0] for m in meses_opcoes],
            format_func=lambda x: meses_nomes[x]
        )
    
    with col3:
        tipo_selecionado = st.selectbox("Tipo", ["Todos", "Receitas", "Despesas"])
    
    # Filtra os dados
    mask = (df['data'].dt.year == ano_selecionado) & (df['data'].dt.month == mes_selecionado)
    df_filtrado = df.loc[mask]
    
    if tipo_selecionado == "Receitas":
        df_filtrado = df_filtrado[df_filtrado['tipo'] == 'receita']
    elif tipo_selecionado == "Despesas":
        df_filtrado = df_filtrado[df_filtrado['tipo'] == 'despesa']
    
    # Se não houver dados no período, mostra mensagem
    if df_filtrado.empty:
        st.info(f"Nenhuma transação encontrada para {meses_nomes[mes_selecionado]} de {ano_selecionado}.")
        return
    
    # Calcula receitas e despesas
    receitas = df_filtrado[df_filtrado['tipo'] == 'receita']['valor'].sum()
    despesas = df_filtrado[df_filtrado['tipo'] == 'despesa']['valor'].sum()
    saldo = receitas - despesas
    
    # Resumo do período
    st.markdown(f"## Resumo de {meses_nomes[mes_selecionado]} de {ano_selecionado}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Receitas", f"R$ {receitas:.2f}".replace('.', ','))
    col2.metric("Despesas", f"R$ {despesas:.2f}".replace('.', ','))
    col3.metric("Saldo", f"R$ {saldo:.2f}".replace('.', ','),
               delta=f"{(saldo/receitas*100 if receitas > 0 else 0):.1f}%" if receitas > 0 else "0%")
    
    st.markdown("---")
    
    # Análise por categoria
    st.subheader("Análise por Categoria")
    
    if tipo_selecionado != "Receitas":
        # Despesas por categoria
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
                
                # Formata para exibição
                despesas_por_categoria['valor'] = despesas_por_categoria['valor'].apply(lambda x: f"R$ {x:.2f}".replace('.', ','))
                despesas_por_categoria = despesas_por_categoria.rename(columns={'categoria': 'Categoria', 'valor': 'Valor'})
                
                st.dataframe(despesas_por_categoria, use_container_width=True)
    
    if tipo_selecionado != "Despesas":
        # Receitas por categoria
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
                
                # Formata para exibição
                receitas_por_categoria['valor'] = receitas_por_categoria['valor'].apply(lambda x: f"R$ {x:.2f}".replace('.', ','))
                receitas_por_categoria = receitas_por_categoria.rename(columns={'categoria': 'Categoria', 'valor': 'Valor'})
                
                st.dataframe(receitas_por_categoria, use_container_width=True)
    
    # Transações do período
    st.markdown("---")
    st.subheader(f"Todas as Transações de {meses_nomes[mes_selecionado]}")
    
    # Formata para exibição
    df_display = df_filtrado.copy()
    df_display['data'] = df_display['data'].dt.strftime('%d/%m/%Y')
    df_display['valor'] = df_display['valor'].apply(lambda x: f"R$ {x:.2f}".replace('.', ','))
    
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
    
    # Opção para download
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download dos dados (CSV)",
        data=csv,
        file_name=f'financas_{meses_nomes[mes_selecionado]}_{ano_selecionado}.csv',
        mime='text/csv',
    )

# Função principal
def main():
    # Sidebar para navegação
    st.sidebar.title("Controle Financeiro")
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2257/2257295.png", width=100)
    
    # Menu de navegação
    menu = st.sidebar.selectbox(
        "Menu",
        ["Dashboard", "Transações", "Relatórios"]
    )
    
    # Navega para a página selecionada
    if menu == "Dashboard":
        show_dashboard()
    elif menu == "Transações":
        show_transactions()
    elif menu == "Relatórios":
        show_reports()
    
    # Rodapé
    st.sidebar.markdown("---")
    st.sidebar.info("Desenvolvido com Python e Streamlit")
    st.sidebar.text(f"Data atual: {datetime.now().strftime('%d/%m/%Y')}")

if __name__ == "__main__":
    main()