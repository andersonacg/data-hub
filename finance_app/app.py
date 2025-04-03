# app.py
import streamlit as st
from database.db_manager import DatabaseManager
from pages.dashboard import show_dashboard
from pages.transactions import show_transactions
from pages.reports import show_reports
from datetime import datetime

st.set_page_config(
    page_title="Controle Financeiro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

db = DatabaseManager()

def main():
    st.sidebar.title("Controle Financeiro")
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2257/2257295.png", width=100)
    
    menu = st.sidebar.selectbox("Menu", ["Dashboard", "Transações", "Relatórios"])
    
    if menu == "Dashboard":
        show_dashboard(db)
    elif menu == "Transações":
        show_transactions(db)
    elif menu == "Relatórios":
        show_reports(db)
    
    st.sidebar.markdown("---")
    st.sidebar.info("Desenvolvido com Python e Streamlit")
    st.sidebar.text(f"Data atual: {datetime.now().strftime('%d/%m/%Y')}")

if __name__ == "__main__":
    main()