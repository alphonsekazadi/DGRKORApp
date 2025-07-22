# app.py

import streamlit as st
from config import DB_CONFIG
from db import get_connection
from utils import load_css
from auth import verifier_connexion  # 🔐

st.set_page_config(
    page_title="Gestion des Contribuables",
    layout="wide"
)

verifier_connexion()  # 🔐 Vérifie que l'utilisateur est connecté

load_css()

st.image("assets/logo_dgrk.png", width=100)
st.title("📊 Système de Gestion de l'Impôt Foncier – DGRKOR")

# === SIDEBAR ===
st.sidebar.title("🌐 Choix de l'Instance")
instance = st.sidebar.selectbox("📍 Instance PostgreSQL", list(DB_CONFIG.keys()))
st.sidebar.success(f"Connecté à : {instance}")

# Utilisateur connecté + bouton de déconnexion
if 'utilisateur' in st.session_state:
    st.sidebar.markdown(f"👤 Utilisateur : **{st.session_state['utilisateur']['nom']}**")
    if st.sidebar.button("🔓 Se déconnecter"):
        del st.session_state['utilisateur']
        st.success("Déconnecté avec succès.")
        st.rerun()

# === RÉSUMÉS ===
conn = get_connection(instance)
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM contribuable")
total_contribuables = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM declaration")
total_declarations = cur.fetchone()[0]

cur.execute("SELECT COALESCE(SUM(montant_paye),0) FROM paiement")
total_paiements = cur.fetchone()[0]

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="card">
        <h3>👥 Contribuables</h3>
        <h1>{total_contribuables}</h1>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <h3>📄 Déclarations</h3>
        <h1>{total_declarations}</h1>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <h3>💰 Total Paiements</h3>
        <h1>{total_paiements:,.2f} FC</h1>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
Bienvenue dans l'interface de gestion décentralisée de l'impôt foncier.

Utilisez les pages à gauche pour naviguer :
- 🏛️ Contribuables
- 📄 Déclarations
- 💰 Paiements
""")

cur.close()
conn.close()
