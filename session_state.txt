import streamlit as st
from models import Turma, Professor, Disciplina, Sala, DIAS_SEMANA
import database
import uuid

def init_session_state():
    database.init_db()
    if "turmas" not in st.session_state:
        st.session_state.turmas = database.carregar_turmas() or [
            Turma("6anoA", "6ano", "manha"),
            Turma("6anoB", "6ano", "manha"),
            Turma("7anoA", "7ano", "manha"),
            Turma("7anoB", "7ano", "manha"),
            Turma("8anoA", "8ano", "manha"),
            Turma("8anoB", "8ano", "manha"),
            Turma("9anoA", "9ano", "manha"),
            Turma("9anoB", "9ano", "manha"),
            Turma("1emA", "1em", "manha"),
            Turma("1emB", "1em", "manha"),
            Turma("2emA", "2em", "manha"),
            Turma("2emB", "2em", "manha"),
            Turma("3emA", "3em", "manha"),
            Turma("3emB", "3em", "manha"),
        ]
    if "professores" not in st.session_state:
        st.session_state.professores = database.carregar_professores() or [
            Professor("Ana A", ["Matemática"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Ana B", ["Matemática"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Bruno A", ["Português"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Bruno B", ["Português"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Carla A", ["História", "Geografia"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Carla B", ["História", "Geografia"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Diego A", ["Ciências", "Biologia"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Diego B", ["Ciências", "Biologia"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Eliane A", ["Inglês"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Eliane B", ["Inglês"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Fábio A", ["Educação Física"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Fábio B", ["Educação Física"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Gisele A", ["Artes"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Gisele B", ["Artes"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Hugo A", ["Física", "Matemática"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Hugo B", ["Física", "Matemática"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Isabel A", ["Química"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Isabel B", ["Química"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Jorge A", ["Filosofia", "Sociologia"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
            Professor("Jorge B", ["Filosofia", "Sociologia"], {"seg", "ter", "qua", "qui", "sex"}, {1,2,3,5,6,7}),
        ]
    if "disciplinas" not in st.session_state:
        st.session_state.disciplinas = database.carregar_disciplinas() or [
            Disciplina("Matemática", 4, "pesada", ["6ano", "7ano", "8ano", "9ano", "1em", "2em", "3em"], "#4A90E2", "#FFFFFF"),
            Disciplina("Português", 4, "pesada", ["6ano", "7ano", "8ano", "9ano", "1em", "2em", "3em"], "#D35400", "#FFFFFF"),
            Disciplina("Ciências", 3, "media", ["6ano", "7ano", "8ano"], "#1ABC9C", "#000000"),
            Disciplina("Biologia", 3, "media", ["9ano", "1em", "2em", "3em"], "#27AE60", "#FFFFFF"),
            Disciplina("Física", 3, "pesada", ["2em", "3em"], "#8E44AD", "#FFFFFF"),
            Disciplina("Química", 3, "pesada", ["9ano", "1em", "2em", "3em"], "#2980B9", "#FFFFFF"),
            Disciplina("História", 3, "media", ["6ano", "7ano", "8ano", "9ano", "1em", "2em", "3em"], "#C0392B", "#FFFFFF"),
            Disciplina("Geografia", 3, "media", ["6ano", "7ano", "8ano", "9ano", "1em"], "#F39C12", "#000000"),
            Disciplina("Inglês", 3, "media", ["6ano", "7ano", "8ano", "9ano", "1em", "2em", "3em"], "#2C3E50", "#FFFFFF"),
            Disciplina("Artes", 1, "leve", ["6ano", "7ano", "8ano", "9ano", "1em", "2em", "3em"], "#E67E22", "#FFFFFF"),
            Disciplina("Educação Física", 2, "pratica", ["6ano", "7ano", "8ano", "9ano", "1em", "2em", "3em"], "#2ECC71", "#000000"),
            Disciplina("Filosofia", 2, "leve", ["1em", "2em", "3em"], "#9B59B6", "#FFFFFF"),
            Disciplina("Sociologia", 2, "leve", ["2em", "3em"], "#16A085", "#FFFFFF"),
        ]
    if "salas" not in st.session_state:
        st.session_state.salas = database.carregar_salas() or [
            Sala("Sala 1", 30, "normal"),
            Sala("Sala 2", 30, "normal"),
            Sala("Sala 3", 30, "normal"),
            Sala("Sala 4", 30, "normal"),
            Sala("Sala 5", 30, "normal"),
            Sala("Sala 6", 30, "normal"),
            Sala("Sala 7", 30, "normal"),
            Sala("Sala 8", 30, "normal"),
            Sala("Sala 9", 30, "normal"),
            Sala("Sala 10", 30, "normal"),
            Sala("Sala 11", 30, "normal"),
            Sala("Sala 12", 30, "normal"),
            Sala("Laboratório de Ciências", 25, "laboratório"),
            Sala("Auditório", 100, "auditório"),
        ]