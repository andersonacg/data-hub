import sqlite3
import pandas as pd
import os

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

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(__file__))  # Ajustado para nova estrutura
            db_path = os.path.join(base_dir, "database", "finance.db")
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
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            cor TEXT DEFAULT '#808080'
        )
        ''')
        
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
        try:
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
        except Exception as e:
            print(f"Erro ao buscar transações: {e}")
            return pd.DataFrame(columns=['id_transacao', 'data', 'descricao', 'valor', 'categoria', 'tipo'])
    
    def add_transaction(self, data, descricao, valor, categoria, tipo):
        """Adiciona uma nova transação"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_categoria FROM categorias WHERE nome = ?", (categoria,))
        result = cursor.fetchone()
        if result:
            categoria_id = result[0]
        else:
            cursor.execute("SELECT id_categoria FROM categorias WHERE nome = 'Outros'")
            categoria_id = cursor.fetchone()[0]
        
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