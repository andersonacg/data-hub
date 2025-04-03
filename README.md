# Convenções de Nomenclatura - Aplicação de Controle Financeiro

## Estrutura do Projeto

```
finance_app/
├── app.py                # Ponto de entrada principal da aplicação
├── database/             # Módulo para conectar e interagir com o banco de dados
│   ├── __init__.py
│   ├── db_connector.py   # Conexão com o banco de dados
│   └── models.py         # Definição de modelos/tabelas
├── utils/                # Funções auxiliares
│   ├── __init__.py
│   ├── date_utils.py     # Funções para manipulação de datas
│   └── currency_utils.py # Funções para formatação de moeda
├── services/             # Lógica de negócios
│   ├── __init__.py
│   ├── transaction_service.py  # Operações relacionadas a transações
│   └── report_service.py       # Geração de relatórios
└── pages/                # Páginas da interface Streamlit
    ├── __init__.py
    ├── dashboard.py      # Página de visão geral
    ├── transactions.py   # Página de transações
    └── reports.py        # Página de relatórios
```


## Convenções de Nomenclatura

### Arquivos e Diretórios
- Utilize `snake_case` para nomes de arquivos e diretórios (ex: `date_utils.py`)
- Utilize nomes claros e descritivos que indiquem a função do arquivo
- Arquivos de módulos Python devem ter o arquivo `__init__.py`

### Classes
- Utilize `PascalCase` para nomes de classes (ex: `TransactionService`)
- Os nomes devem ser substantivos que descrevem o que a classe representa
- Exemplos: `ExpenseCategory`, `MonthlyReport`, `DatabaseConnector`

### Funções e Métodos
- Utilize `snake_case` para funções e métodos
- Comece com verbos que descrevem a ação realizada
- Exemplos: `calculate_monthly_total()`, `get_transactions_by_category()`, `save_expense()`

### Variáveis
- Utilize `snake_case` para variáveis
- Nomes descritivos que indicam o propósito
- Exemplos: `monthly_income`, `total_expenses`, `savings_percentage`

### Constantes
- Utilize `UPPER_SNAKE_CASE` para constantes
- Exemplos: `DEFAULT_CURRENCY`, `MAX_CATEGORIES`, `DATE_FORMAT`

### Banco de Dados
- Tabelas: nomes no plural em `snake_case` (ex: `transactions`, `expense_categories`)
- Colunas: nomes em `snake_case` (ex: `transaction_date`, `category_id`)
- Chaves primárias: prefixo `id_` (ex: `id_transaction`, `id_category`)
- Chaves estrangeiras: nome da tabela no singular seguido de `_id` (ex: `category_id`, `user_id`)

## Exemplos Práticos

### Exemplos de Classes
```python
class Transaction:
    """Representa uma transação financeira."""
    
class ExpenseCategory:
    """Representa uma categoria de despesa."""
    
class FinancialReport:
    """Gera relatórios financeiros."""
```

### Exemplos de Funções
```python
def calculate_monthly_balance(income, expenses):
    """Calcula o saldo mensal."""
    
def format_currency(value, currency_symbol="R$"):
    """Formata um valor para exibição como moeda."""
    
def get_transactions_by_period(start_date, end_date):
    """Obtém transações em um período específico."""
```

### Exemplos de Variáveis
```python
# Boas práticas
monthly_income = 5000.00
total_expenses = 3500.00
savings_rate = 0.30

# Evitar
inc = 5000.00  # não descritivo
totalexp = 3500.00  # mistura de convenções
svrate = 0.30  # abreviações não claras
```

## Convenções para Streamlit

### Páginas e Componentes
- Nome de páginas: `snake_case` (ex: `expense_analysis.py`)
- Títulos de páginas: utilizar `st.title()` com texto capitalizado (ex: "Análise de Despesas")
- Seções: utilizar `st.header()` para seções principais e `st.subheader()` para subseções

### Exemplos de Código Streamlit
```python
# Em dashboard.py
import streamlit as st

def show_dashboard():
    st.title("Painel de Controle Financeiro")
    
    st.header("Resumo Mensal")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Renda Total", "R$ 5.000,00", "+8%")
    
    with col2:
        st.metric("Despesas", "R$ 3.500,00", "-3%")
    
    with col3:
        st.metric("Economia", "R$ 1.500,00", "+30%")
```

## Boas Práticas Adicionais

1. **Comentários**: Use comentários para explicar "por quê", não "o quê"
2. **Documentação**: Use docstrings para documentar classes e funções
3. **Consistência**: Mantenha a consistência ao longo do projeto
4. **Evite abreviações**: A menos que sejam muito conhecidas (ex: URL, HTTP)
5. **Prefixos semânticos**: Use prefixos como `is_`, `has_` para booleanos (ex: `is_expense_paid`)