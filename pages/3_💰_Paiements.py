# pages/3_💰_Paiements.py

import streamlit as st
import pandas as pd
from db import get_connection
from config import DB_CONFIG
from utils import load_css

load_css()
st.header("💰 Paiements d'Impôts")

# Choix de l’instance
instance = st.sidebar.selectbox("📍 Choisir une instance", list(DB_CONFIG.keys()))
conn = get_connection(instance)
cur = conn.cursor()

# 🔍 Liste des paiements
cur.execute("""
    SELECT p.id, c.raison_sociale, d.exercice, p.mode_paiement, p.montant_paye, p.date_paiement
    FROM paiement p
    JOIN declaration d ON p.id_declaration = d.id
    JOIN contribuable c ON d.id_contribuable = c.id
    ORDER BY p.date_paiement DESC
""")
rows = cur.fetchall()
df = pd.DataFrame(rows, columns=["ID", "Contribuable", "Exercice", "Mode Paiement", "Montant Payé", "Date Paiement"])
st.dataframe(df, use_container_width=True)

# ➕ Formulaire d’ajout de paiement
st.subheader("➕ Ajouter un Paiement")

# Liste déroulante des déclarations
cur.execute("""
    SELECT d.id, c.raison_sociale, d.exercice
    FROM declaration d
    JOIN contribuable c ON d.id_contribuable = c.id
    ORDER BY d.date_declaration DESC
""")
decls = cur.fetchall()
decl_map = {f"{r[1]} - {r[2]} (Décl. ID {r[0]})": r[0] for r in decls}

if decl_map:
    with st.form("form_paiement"):
        decl_select = st.selectbox("Déclaration", list(decl_map.keys()))
        mode = st.selectbox("Mode de Paiement", ["Espèces", "Chèque", "Virement", "Mobile Money"])
        montant = st.number_input("Montant Payé", min_value=0.0, step=1000.0)
        submitted = st.form_submit_button("Enregistrer")

        if submitted:
            try:
                cur.execute("""
                    INSERT INTO paiement (id_declaration, mode_paiement, montant_paye)
                    VALUES (%s, %s, %s)
                """, (decl_map[decl_select], mode, montant))
                conn.commit()
                st.success("✅ Paiement enregistré avec succès.")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
else:
    st.warning("Aucune déclaration trouvée. Veuillez d'abord en enregistrer.")

cur.close()
conn.close()
