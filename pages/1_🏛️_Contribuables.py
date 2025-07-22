# pages/1_🏛️_Contribuables.py

import streamlit as st
import pandas as pd
from db import get_connection
from config import DB_CONFIG
from utils import load_css

load_css()
st.header("🏛️ Liste des Contribuables")

instance = st.sidebar.selectbox("📍 Choisir une instance", list(DB_CONFIG.keys()))
conn = get_connection(instance)
cur = conn.cursor()

# --- Filtre commune ---
commune_filtre = st.selectbox("🔎 Filtrer par commune", ["Toutes"] + ["DIBINDI", "MUYA"])

query = "SELECT id, raison_sociale, numero_impot, commune, telephone, email FROM contribuable"
if commune_filtre != "Toutes":
    query += " WHERE commune = %s"
    cur.execute(query, (commune_filtre,))
else:
    cur.execute(query)

rows = cur.fetchall()
df = pd.DataFrame(rows, columns=["ID", "Raison Sociale", "Numéro Impôt", "Commune", "Téléphone", "Email"])

# --- Affichage des contribuables avec actions ---
st.subheader("📋 Liste détaillée")
for row in rows:
    with st.expander(f"🔎 {row[1]} ({row[2]})"):
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"**Commune :** {row[3]}")
        col2.markdown(f"**Téléphone :** {row[4]}")
        col3.markdown(f"**Email :** {row[5]}")

        colA, colB = st.columns(2)

        # --- Modifier ---
        with colA:
            if st.button(f"✏️ Modifier", key=f"edit_{row[0]}"):
                st.session_state["edit_contribuable"] = row

        # --- Supprimer ---
        with colB:
            if st.button(f"🗑 Supprimer", key=f"delete_{row[0]}"):
                cur.execute("DELETE FROM contribuable WHERE id = %s", (row[0],))
                conn.commit()
                st.success("✅ Contribuable supprimé avec succès.")
                st.experimental_rerun()

# --- Formulaire d'ajout ou de mise à jour ---
if "edit_contribuable" in st.session_state:
    st.subheader("✏️ Mettre à jour un Contribuable")
    c = st.session_state["edit_contribuable"]
    with st.form("form_update"):
        rs = st.text_input("Raison Sociale", value=c[1])
        ni = st.text_input("Numéro Impôt", value=c[2])
        adresse = st.text_area("Adresse", value="")
        commune = st.selectbox("Commune", ["DIBINDI", "MUYA"], index=["DIBINDI", "MUYA"].index(c[3]))
        tel = st.text_input("Téléphone", value=c[4])
        email = st.text_input("Email", value=c[5])
        submitted = st.form_submit_button("💾 Mettre à jour")

        if submitted:
            try:
                cur.execute("""
                    UPDATE contribuable
                    SET raison_sociale = %s, numero_impot = %s, adresse = %s,
                        commune = %s, telephone = %s, email = %s
                    WHERE id = %s
                """, (rs, ni, adresse, commune, tel, email, c[0]))
                conn.commit()
                st.success("✅ Contribuable mis à jour avec succès.")
                del st.session_state["edit_contribuable"]
                st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
else:
    st.subheader("➕ Ajouter un Contribuable")
    with st.form("form_contribuable"):
        rs = st.text_input("Raison Sociale")
        ni = st.text_input("Numéro Impôt")
        adresse = st.text_area("Adresse")
        commune = st.selectbox("Commune", ["DIBINDI", "MUYA"])
        tel = st.text_input("Téléphone")
        email = st.text_input("Email")
        submitted = st.form_submit_button("Ajouter")

        if submitted:
            try:
                cur.execute("""
                    INSERT INTO contribuable (raison_sociale, numero_impot, adresse, commune, telephone, email)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (rs, ni, adresse, commune, tel, email))
                conn.commit()
                st.success("✅ Contribuable ajouté avec succès.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ Erreur : {e}")

cur.close()
conn.close()
