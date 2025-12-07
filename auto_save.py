from database import salvar_disciplinas, salvar_professores, salvar_turmas, salvar_salas
import streamlit as st

def salvar_tudo():
    """Salva todos os dados no banco"""
    try:
        success = True
        
        if 'disciplinas' in st.session_state:
            if not salvar_disciplinas(st.session_state.disciplinas):
                success = False
                
        if 'professores' in st.session_state:
            if not salvar_professores(st.session_state.professores):
                success = False
                
        if 'turmas' in st.session_state:
            if not salvar_turmas(st.session_state.turmas):
                success = False
                
        if 'salas' in st.session_state:
            if not salvar_salas(st.session_state.salas):
                success = False
                
        return success
        
    except Exception as e:
        print(f"Erro ao salvar tudo: {e}")
        return False