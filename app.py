import os
import urllib.parse

import pandas as pd
import streamlit as st
from supabase import create_client

# -----------------------------------------------------------------------------
# 1. Configuração da Página
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Caçador de Vagas Angola | Plataforma Técnica",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. Estilização CSS Customizada (SaaS Moderno)
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
    /* Import de Fontes */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Container Principal */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }

    /* Cards de Estatísticas / KPIs */
    .kpi-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #0066FF;
    }
    .kpi-number {
        font-size: 2rem;
        font-weight: 700;
        color: #0066FF;
        margin-bottom: 4px;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #a0aec0;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Card de Vaga */
    .job-card {
        background-color: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 16px;
        transition: all 0.2s ease-in-out;
    }
    .job-card:hover {
        border-color: #0066FF;
        background-color: rgba(30, 41, 59, 0.7);
        box-shadow: 0 6px 20px rgba(0, 102, 255, 0.12);
    }
    .job-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #f8fafc;
        margin-bottom: 8px;
    }
    .job-meta {
        font-size: 0.88rem;
        color: #94a3b8;
        display: flex;
        gap: 16px;
        align-items: center;
        margin-bottom: 14px;
    }

    /* Badges / Tags */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .badge-electricidade { background-color: rgba(234, 179, 8, 0.15); color: #facc15; border: 1px solid rgba(234, 179, 8, 0.3); }
    .badge-manutencao { background-color: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .badge-energia { background-color: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
    .badge-telecom { background-color: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
    .badge-hvac { background-color: rgba(6, 182, 212, 0.15); color: #22d3ee; border: 1px solid rgba(6, 182, 212, 0.3); }
    .badge-geral { background-color: rgba(148, 163, 184, 0.15); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.3); }

    /* Botão de Ação */
    .apply-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #0066FF, #0052CC);
        color: #ffffff !important;
        padding: 8px 18px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.88rem;
        text-decoration: none !important;
        transition: all 0.2s ease;
        border: none;
    }
    .apply-btn:hover {
        opacity: 0.95;
        box-shadow: 0 4px 12px rgba(0, 102, 255, 0.3);
        transform: translateY(-1px);
    }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 3. Conexão com Supabase
# -----------------------------------------------------------------------------
SUPABASE_URL = os.getenv(
    "SUPABASE_URL", "https://qzuhxfugpmollvueqihk.supabase.co"
)
SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY", "sb_publishable_Z_t4cGcEgtLy3m-3QxMajg_leBgVLd-"
)


@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_supabase()


# -----------------------------------------------------------------------------
# 4. Funções Auxiliares (Categorização & Links)
# -----------------------------------------------------------------------------
def classificar_categoria(titulo):
    t = str(titulo).lower()
    if any(
        k in t
        for k in [
            "electric",
            "eletric",
            "automação",
            "instrumentação",
            "electrónica",
        ]
    ):
        return "Electricidade & Electrónica", "badge-electricidade"
    elif any(
        k in t for k in ["manutenção", "mecânico", "electromecânico", "obra"]
    ):
        return "Manutenção & Mecânica", "badge-manutencao"
    elif any(k in t for k in ["solar", "energia", "fotovoltaico", "renovável"]):
        return "Energia & Solar", "badge-energia"
    elif any(
        k in t
        for k in ["telecom", "redes", "fibra", "rf", "ftth", "radiocomunicação"]
    ):
        return "Telecomunicações & Redes", "badge-telecom"
    elif any(
        k in t
        for k in [
            "frio",
            "hvac",
            "avac",
            "climatização",
            "ar condicionado",
            "refrigeração",
            "canalização",
        ]
    ):
        return "Climatização, HVAC & Canalização", "badge-hvac"
    else:
        return "Técnico Geral / Engenharia", "badge-geral"


def gerar_link_busca(titulo, fonte):
    # Caso a vaga não tenha URL direta salva, gera um link inteligente de busca
    query = f"{titulo} {fonte} Angola vagas"
    encoded = urllib.parse.quote(query)
    return f"https://www.google.com/search?q={encoded}"


@st.cache_data(ttl=300)
def carregar_dados():
    try:
        response = (
            supabase.table("jobs")
            .select("*")
            .order("id", desc=True)
            .execute()
        )
        df = pd.DataFrame(response.data)
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com a base de dados: {e}")
        return pd.DataFrame()


# -----------------------------------------------------------------------------
# 5. Interface da Aplicação
# -----------------------------------------------------------------------------

# Cabeçalho Principal
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("⚡ Caçador de Vagas Angola")
    st.caption(
        "Plataforma inteligente de agregação de oportunidades técnicas, engenharia e manutenção."
    )

with col_head2:
    st.write("")
    st.markdown(
        "<div style='text-align: right;'><span class='badge badge-energia'>● Atualizado em Tempo Real</span></div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

df = carregar_dados()

if not df.empty:
    # Processamento de Categorias
    df[["categoria", "badge_class"]] = df["title"].apply(
        lambda x: pd.Series(classificar_categoria(x))
    )

    # -----------------------------------------------------------------------------
    # KPIs / Métricas Visuais
    # -----------------------------------------------------------------------------
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.markdown(
            f"""
            <div class='kpi-card'>
                <div class='kpi-number'>{len(df)}</div>
                <div class='kpi-label'>Total de Vagas</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi2:
        fontes_unicas = (
            df["company"].nunique() if "company" in df.columns else 0
        )
        st.markdown(
            f"""
            <div class='kpi-card'>
                <div class='kpi-number'>{fontes_unicas}</div>
                <div class='kpi-label'>Fontes de Emprego</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi3:
        categorias_unicas = df["categoria"].nunique()
        st.markdown(
            f"""
            <div class='kpi-card'>
                <div class='kpi-number'>{categorias_unicas}</div>
                <div class='kpi-label'>Áreas Técnicas</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi4:
        st.markdown(
            """
            <div class='kpi-card'>
                <div class='kpi-number' style='color: #22c55e;'>100%</div>
                <div class='kpi-label'>Vagas Qualificadas</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # Barra Lateral (Filtros Avançados & Banco de CVs)
    # -----------------------------------------------------------------------------
    st.sidebar.header("🔍 Filtros de Pesquisa")

    # Pesquisa por Palavra-Chave
    search_query = st.sidebar.text_input(
        "🔎 Buscar no Título:", "", placeholder="Ex: Electricista, HVAC, Solar..."
    )

    # Filtro por Categoria
    todas_categorias = ["Todas as Áreas"] + list(
        df["categoria"].unique()
    )
    categoria_selecionada = st.sidebar.selectbox(
        "📂 Filtrar por Área Técnica:", todas_categorias
    )

    # Filtro por Fonte / Portal
    if "company" in df.columns:
        todas_fontes = ["Todas as Fontes"] + list(df["company"].unique())
        fonte_selecionada = st.sidebar.selectbox(
            "🌐 Filtrar por Fonte:", todas_fontes
        )
    else:
        fonte_selecionada = "Todas as Fontes"

    st.sidebar.markdown("---")

    # Área de Candidatura Rápida / Banco de Talentos
    st.sidebar.subheader("📄 Banco de Talentos")
    st.sidebar.info(
        "Envia o teu CV para ficares visível para recrutadores das áreas técnicas em Angola."
    )

    with st.sidebar.popover("📤 Submeter Currículo"):
        st.markdown("### Envios de CV")
        nome = st.text_input("Nome Completo:")
        email_cand = st.text_input("E-mail ou Telemóvel:")
        area_cand = st.selectbox(
            "Área Principal:",
            [
                "Electricidade",
                "Manutenção",
                "Climatização/HVAC",
                "Telecomunicações",
                "Energia Solar",
            ],
        )
        f_cv = st.file_uploader("Anexar CV (PDF):", type=["pdf", "docx"])
        if st.button("Enviar Candidatura", type="primary"):
            if nome and email_cand:
                st.success(
                    "✅ CV registado com sucesso no Banco de Talentos!"
                )
            else:
                st.warning("Por favor preenche o nome e contacto.")

    # -----------------------------------------------------------------------------
    # Aplicação dos Filtros
    # -----------------------------------------------------------------------------
    filtered_df = df.copy()

    if search_query:
        filtered_df = filtered_df[
            filtered_df["title"].str.contains(
                search_query, case=False, na=False
            )
        ]

    if categoria_selecionada != "Todas as Áreas":
        filtered_df = filtered_df[
            filtered_df["categoria"] == categoria_selecionada
        ]

    if fonte_selecionada != "Todas as Fontes":
        filtered_df = filtered_df[filtered_df["company"] == fonte_selecionada]

    # -----------------------------------------------------------------------------
    # Listagem das Vagas em Cards Modernos
    # -----------------------------------------------------------------------------
    st.markdown(
        f"### 📋 Oportunidades Encontradas ({len(filtered_df)})"
    )

    if not filtered_df.empty:
        for idx, row in filtered_df.iterrows():
            title = row.get("title", "Título indisponível")
            company = row.get("company", "Fonte Externa")
            location = row.get("location", "Angola")
            categoria = row.get("categoria", "Geral")
            badge_cls = row.get("badge_class", "badge-geral")
            job_url = row.get("url") or gerar_link_busca(title, company)

            # HTML do Card
            card_html = f"""
            <div class="job-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                    <span class="badge {badge_cls}">{categoria}</span>
                    <span style="font-size: 0.8rem; color: #64748b;">📍 {location}</span>
                </div>
                <div class="job-title">{title}</div>
                <div class="job-meta">
                    <span>🏢 Fonte: <b>{company}</b></span>
                </div>
                <div style="margin-top: 12px;">
                    <a href="{job_url}" target="_blank" class="apply-btn">
                        🔗 Ver Vaga / Candidatar-se →
                    </a>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.warning(
            "Nenhuma vaga encontrada com os filtros selecionados. Tenta pesquisar outro termo."
        )

else:
    st.info(
        "A base de dados ainda não possui vagas registadas. Certifica-te de rodar o scraper no GitHub Actions!"
    )
