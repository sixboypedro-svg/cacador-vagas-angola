import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client

# Conexão com Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qzuhxfugpmollvueqihk.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_Z_t4cGcEgtLy3m-3QxMajg_leBgVLd-")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

KEYWORDS = [
    # Electricidade
    "electricidade", "eletricidade", "electricista", "eletricista", "técnico eléctrico", "técnico eletrico",
    "electricista industrial", "electricista predial", "ajudante de electricista",
    # Manutenção
    "técnico de manutenção", "técnico electromecânico", "electromecânico", "manutenção industrial", "manutenção eléctrica",
    # Energia
    "técnico solar", "técnico fotovoltaico", "energia solar", "instalador fotovoltaico", "o&m solar",
    # Telecom
    "telecomunicações", "técnico de redes", "fibra óptica", "fibra optica", "ftth", "radiocomunicação", "rf", "field technician",
    # Electrónica
    "técnico de electrónica", "automação", "instrumentação", "controlo", "iot",
    # Canalização & Hidráulica
    "canalização", "canalizador", "técnico de canalização", "canalizador industrial", "técnico hidráulico",
    "instalações hidráulicas", "redes de água", "redes de esgoto", "bombeamento", "manutenção hidráulica", "picheleiro",
    # Frio Industrial
    "técnico de frio", "técnico de refrigeração", "frio industrial", "refrigeração industrial", "mecânico de refrigeração",
    "refrigeração comercial", "sistemas de refrigeração", "câmaras frigoríficas", "chillers", "sistemas de arrefecimento",
    # Climatização / HVAC
    "climatização", "hvac", "avac", "instalação hvac", "manutenção hvac", "ar condicionado",
    "climatização industrial", "ventilação industrial", "vrf", "ahu",
    # Engenharia & Supervisão
    "técnico de obras", "técnico de instalações", "supervisor técnico", "encarregado de manutenção",
    "chefe de equipa", "técnico de projecto", "engenheiro electrotécnico", "engenheiro de manutenção", "engenheiro de energia"
]

def vaga_e_relevante(titulo):
    titulo_lower = titulo.lower()
    return any(keyword in titulo_lower for keyword in KEYWORDS)

def obter_titulos_existentes():
    try:
        dados = supabase.table("jobs").select("title").execute()
        return {item["title"].strip().lower() for item in dados.data if item.get("title")}
    except Exception as e:
        print(f"⚠️ Erro ao buscar vagas existentes: {e}")
        return set()

def raspar_ango_emprego():
    url = "https://www.angoemprego.com/"
    print("🔍 A raspar Ango Emprego...")
    vagas = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)
        titulos_vistos = set()
        
        for link in links:
            texto = link.text.strip()
            href = link['href']
            if "angoemprego.com" in href and len(texto) > 10:
                if texto not in titulos_vistos and vaga_e_relevante(texto):
                    titulos_vistos.add(texto)
                    vagas.append({"title": texto, "company": "Ango Emprego", "location": "Angola"})
    except Exception as e:
        print(f"❌ Erro no Ango Emprego: {e}")
    return vagas

def raspar_jobartis():
    url = "https://www.jobartis.com/"
    print("🔍 A raspar Jobartis...")
    vagas = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        elementos = soup.find_all(["h2", "h3", "a"])
        titulos_vistos = set()
        
        for el in elementos:
            texto = el.text.strip()
            if len(texto) > 10 and texto not in titulos_vistos and vaga_e_relevante(texto):
                titulos_vistos.add(texto)
                vagas.append({"title": texto, "company": "Jobartis", "location": "Angola"})
    except Exception as e:
        print(f"❌ Erro no Jobartis: {e}")
    return vagas

if __name__ == "__main__":
    titulos_existentes = obter_titulos_existentes()
    print(f"📊 Vagas no banco: {len(titulos_existentes)}")

    todas_vagas = raspar_ango_emprego() + raspar_jobartis()
    print(f"🎯 Vagas filtradas da área capturadas: {len(todas_vagas)}")

    novas_vagas = [v for v in todas_vagas if v["title"].strip().lower() not in titulos_existentes]

    if novas_vagas:
        print(f"🚀 A enviar {len(novas_vagas)} novas vagas qualificadas...")
        sucesso = 0
        for vaga in novas_vagas:
            try:
                supabase.table("jobs").insert(vaga).execute()
                sucesso += 1
            except Exception as err:
                print(f"⚠️ Erro ao inserir: {err}")
        print(f"✅ Concluído! {sucesso} vagas qualificadas salvas.")
    else:
        print("✨ Nenhuma vaga nova da tua área encontrada neste momento.")
