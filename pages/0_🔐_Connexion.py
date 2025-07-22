# pages/0_🔐_Connexion.py

import streamlit as st
import hashlib
from db import get_connection
from config import DB_CONFIG
from utils import load_css

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
    
load_css()
st.title("🔐 Connexion Utilisateur")

instance = st.sidebar.selectbox("📍 Choisir une instance", list(DB_CONFIG.keys()))
conn = get_connection(instance)
cur = conn.cursor()

email = st.text_input("Email")
password = st.text_input("Mot de passe", type="password")
if st.button("Se connecter"):
    hpass = hash_password(password)
    cur.execute("SELECT id, nom, role FROM utilisateur WHERE email = %s AND mot_de_passe = %s AND actif = TRUE", (email, hpass))
    user = cur.fetchone()
    if user:
        st.success(f"Bienvenue, {user[1]} ! (Rôle : {user[2]})")
        st.session_state['utilisateur'] = {"id": user[0], "nom": user[1], "role": user[2]}
    else:
        st.error("Email ou mot de passe incorrect.")

cur.close()
conn.close()
