import streamlit as st
from database import carregar_disciplinas, carregar_professores, carregar_turmas, carregar_salas

def init_session_state():
    """Inicializa o session state com dados do banco"""
    
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        
        # Carregar dados do banco
        st.session_state.disciplinas = carregar_disciplinas()
        st.session_state.professores = carregar_professores() 
        st.session_state.turmas = carregar_turmas()
        st.session_state.salas = carregar_salas()
        
        # Estado para grade gerada
        if 'grade_gerada' not in st.session_state:
            st.session_state.grade_gerada = None
        if 'turmas_grade' not in st.session_state:
            st.session_state.turmas_grade = []