# pages/2_📄_Déclarations.py

import streamlit as st
import pandas as pd
from db import get_connection
from config import DB_CONFIG
from utils import load_css
from io import BytesIO

load_css()
st.header("📄 Déclarations d'Impôts")

# Choix instance
instance = st.sidebar.selectbox("📍 Choisir une instance", list(DB_CONFIG.keys()))
conn = get_connection(instance)
cur = conn.cursor()

# 🔍 Chargement des déclarations
cur.execute("""
    SELECT d.id, c.raison_sociale, d.exercice, d.montant_declare, d.date_declaration
    FROM declaration d
    JOIN contribuable c ON c.id = d.id_contribuable
    ORDER BY d.date_declaration DESC
""")
rows = cur.fetchall()
columns = ["ID", "Contribuable", "Exercice", "Montant Déclaré", "Date Déclaration"]
df = pd.DataFrame(rows, columns=columns)

# Export Excel
def export_excel(dataframe):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Déclarations')
    return output.getvalue()

st.download_button(
    label="📥 Exporter en Excel",
    data=export_excel(df),
    file_name="declarations.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Affichage détaillé
st.subheader("📋 Liste des Déclarations")
for row in rows:
    with st.expander(f"{row[1]} – {row[2]}"):
        st.markdown(f"**Montant :** {row[3]} FC")
        st.markdown(f"**Date :** {row[4]}")

        col1, col2 = st.columns(2)

        # Supprimer
        if col1.button("🗑 Supprimer", key=f"delete_{row[0]}"):
            cur.execute("DELETE FROM declaration WHERE id = %s", (row[0],))
            conn.commit()
            st.success("✅ Déclaration supprimée.")
            st.experimental_rerun()

        # Modifier
        if col2.button("✏️ Modifier", key=f"edit_{row[0]}"):
            st.session_state["edit_declaration"] = {
                "id": row[0], "contribuable": row[1], "exercice": row[2], "montant": row[3]
            }

# Formulaire : ajout ou mise à jour
cur.execute("SELECT id, raison_sociale FROM contribuable")
contribuables = cur.fetchall()
contrib_map = {f"{r[1]} (ID {r[0]})": r[0] for r in contribuables}

if "edit_declaration" in st.session_state:
    st.subheader("✏️ Modifier une Déclaration")
    edit = st.session_state["edit_declaration"]

    with st.form("form_update"):
        contrib_select = st.selectbox("Contribuable", list(contrib_map.keys()), index=[
            i for i, key in enumerate(contrib_map) if edit["contribuable"] in key
        ][0])
        exercice = st.number_input("Exercice", min_value=2000, max_value=2100, value=edit["exercice"])
        montant = st.number_input("Montant Déclaré", min_value=0.0, step=1000.0, value=float(edit["montant"]))
        submitted = st.form_submit_button("💾 Mettre à jour")

        if submitted:
            cur.execute("""
                UPDATE declaration
                SET id_contribuable = %s, exercice = %s, montant_declare = %s
                WHERE id = %s
            """, (contrib_map[contrib_select], exercice, montant, edit["id"]))
            conn.commit()
            del st.session_state["edit_declaration"]
            st.success("✅ Déclaration mise à jour.")
            st.experimental_rerun()
else:
    st.subheader("➕ Ajouter une Déclaration")

    if contrib_map:
        with st.form("form_add_declaration"):
            contrib_select = st.selectbox("Contribuable", list(contrib_map.keys()))
            exercice = st.number_input("Exercice", min_value=2000, max_value=2100, value=2024)
            montant = st.number_input("Montant Déclaré", min_value=0.0, step=1000.0)
            submitted = st.form_submit_button("Ajouter")

            if submitted:
                cur.execute("""
                    INSERT INTO declaration (id_contribuable, exercice, montant_declare)
                    VALUES (%s, %s, %s)
                """, (contrib_map[contrib_select], exercice, montant))
                conn.commit()
                st.success("✅ Déclaration ajoutée.")
                st.experimental_rerun()
    else:
        st.warning("⚠️ Aucun contribuable trouvé. Veuillez d'abord en ajouter.")

cur.close()
conn.close()
