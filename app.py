import streamlit as st
import pandas as pd
from supabase import create_client
import os

# Configuração da página
st.set_page_config(page_title="Caçador de Vagas Angola", page_icon="💼", layout="wide")

# Conexão Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qzuhxfugpmollvueqihk.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_Z_t4cGcEgtLy3m-3QxMajg_leBgVLd-")

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.title("💼 Caçador de Vagas Angola — Painel Técnico")
st.write("Agregador centralizado de oportunidades em Engenharia, Manutenção, Energia e Telecomunicações.")

# Carregar dados
@st.cache_data(ttl=300)
def load_data():
    try:
        response = supabase.table("jobs").select("*").execute()
        df = pd.DataFrame(response.data)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados do Supabase: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Sidebar - Filtros
    st.sidebar.header("🔍 Filtros de Pesquisa")
    
    search_term = st.sidebar.text_input("Buscar no título da vaga:", "")
    
    if "company" in df.columns:
        companies = ["Todas"] + list(df["company"].dropna().unique())
        selected_company = st.sidebar.selectbox("Origem / Fonte:", companies)
    else:
        selected_company = "Todas"

    # Filtragem
    filtered_df = df.copy()
    
    if search_term:
        filtered_df = filtered_df[filtered_df["title"].str.contains(search_term, case=False, na=False)]
        
    if selected_company != "Todas" and "company" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["company"] == selected_company]

    # Métricas
    col1, col2 = st.columns(2)
    col1.metric("Total de Vagas Registadas", len(df))
    col2.metric("Vagas Filtradas Exibidas", len(filtered_df))

    st.markdown("---")

    # Exibição das Vagas
    for idx, row in filtered_df.iterrows():
        with st.container():
            st.subheader(f"📌 {row.get('title', 'Sem título')}")
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"**Fonte:** {row.get('company', 'N/A')} | **Local:** {row.get('location', 'Angola')}")
            st.markdown("---")
else:
    st.warning("Nenhuma vaga encontrada na base de dados.")
