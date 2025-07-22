# auth.py

import streamlit as st

def est_connecte():
    return 'utilisateur' in st.session_state

def role_utilisateur():
    if est_connecte():
        return st.session_state['utilisateur']['role']
    return None

def verifier_connexion():
    if not est_connecte():
        st.warning("🔐 Veuillez vous connecter pour accéder à cette page.")
        st.stop()  # Arrête la page ici
