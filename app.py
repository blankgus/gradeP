import streamlit as st
import json
import pandas as pd
import io
import traceback
from session_state import init_session_state
from models import Turma, Professor, Disciplina, Sala, DIAS_SEMANA
from scheduler_ortools import GradeHorariaORTools
from export import (
    exportar_para_excel,
    exportar_para_pdf,
    gerar_relatorio_professor,
    gerar_relatorio_todos_professores,
    gerar_relatorio_disciplina_sala,
    gerar_grade_por_turma_semana,
    gerar_grade_por_sala_semana,
    gerar_grade_por_professor_semana,
    exportar_grade_por_tipo
)
import database
from simple_scheduler import SimpleGradeHoraria
import uuid

HORARIOS_REAIS = {
    1: "07:00-07:50",
    2: "07:50-08:40",
    3: "08:40-09:30",
    4: "09:30-09:50",
    5: "09:50-10:40",
    6: "10:40-11:30",
    7: "11:30-12:20"
}

try:
    init_session_state()
    if "aulas" not in st.session_state:
        st.session_state.aulas = []
except Exception as e:
    st.error(f"❌ Erro na inicialização: {str(e)}")
    st.code(traceback.format_exc())
    st.stop()

def color_disciplina(val):
    if val:
        for d in st.session_state.disciplinas:
            if d.nome == val:
                return f'background-color: {d.cor_fundo}; color: {d.cor_fonte}; font-weight: bold'
    if val == "INTERVALO":
        return 'background-color: #FFD700; color: black; font-weight: bold; text-align: center'
    if val == "Sem Aula":
        return 'background-color: #F0F0F0; color: #666666; font-style: italic; text-align: center'
    return ''

st.set_page_config(page_title="Escola Timetable", layout="wide")
st.title("🕒 Gerador Inteligente de Grade Horária")

abas = st.tabs([
    "🏠 Início", "📚 Disciplinas", "👩‍🏫 Professores", "🎒 Turmas",
    "🏫 Salas", "📅 Calendário", "⚙️ Configurações", "🗓️ Feriados",
    "🎒 Grade por Turma", "🏫 Grade por Sala", "👨‍🏫 Grade por Professor"
])
(aba1, aba2, aba3, aba4, aba5, aba6, aba7, aba8, aba9, aba10, aba11) = abas

# =================== ABA 2: DISCIPLINAS ===================
with aba2:
    st.header("Disciplinas")
    with st.form("add_disc"):
        nome = st.text_input("Nome")
        carga = st.number_input("Carga", 1, 7, 3)
        tipo = st.selectbox("Tipo", ["pesada", "media", "leve", "pratica"])
        series = st.text_input("Séries", "6ano,7ano,8ano,9ano,1em,2em,3em")
        cor_fundo = st.color_picker("Cor de Fundo", "#4A90E2")
        cor_fonte = st.color_picker("Cor da Fonte", "#000000")
        if st.form_submit_button("➕ Adicionar"):
            if nome:
                series_list = [s.strip() for s in series.split(",") if s.strip()]
                st.session_state.disciplinas.append(Disciplina(nome, carga, tipo, series_list, cor_fundo, cor_fonte))
                st.rerun()
    for d in st.session_state.disciplinas[:]:
        with st.expander(f"{d.nome}"):
            with st.form(f"edit_disc_{d.id}"):
                nome = st.text_input("Nome", d.nome, key=f"n_{d.id}")
                carga = st.number_input("Carga", 1, 7, d.carga_semanal, key=f"c_{d.id}")
                tipo = st.selectbox("Tipo", ["pesada", "media", "leve", "pratica"], 
                                   index=["pesada", "media", "leve", "pratica"].index(d.tipo), key=f"t_{d.id}")
                series = st.text_input("Séries", ", ".join(d.series), key=f"s_{d.id}")
                cor_fundo = st.color_picker("Cor de Fundo", d.cor_fundo, key=f"cor_fundo_{d.id}")
                cor_fonte = st.color_picker("Cor da Fonte", d.cor_fonte, key=f"cor_fonte_{d.id}")
                col1, col2 = st.columns(2)
                if col1.form_submit_button("💾 Salvar"):
                    series_list = [s.strip() for s in series.split(",") if s.strip()]
                    st.session_state.disciplinas = [
                        Disciplina(nome, carga, tipo, series_list, cor_fundo, cor_fonte, d.id) if item.id == d.id else item
                        for item in st.session_state.disciplinas
                    ]
                    st.rerun()
                if col2.form_submit_button("🗑️ Excluir"):
                    st.session_state.disciplinas = [
                        item for item in st.session_state.disciplinas if item.id != d.id
                    ]
                    st.rerun()

# =================== ABA 3: PROFESSORES ===================
with aba3:
    st.header("Professores")
    disc_nomes = [d.nome for d in st.session_state.disciplinas] or ["Nenhuma"]
    with st.form("add_prof"):
        nome = st.text_input("Nome")
        discs = st.multiselect("Disciplinas", disc_nomes)
        dias = st.multiselect("Dias disponíveis", DIAS_SEMANA, default=["seg", "ter", "qua", "qui", "sex"])
        horarios_disp = st.multiselect("Horários disponíveis", [1,2,3,4,5,6,7], default=[1,2,3,5,6,7])
        if st.form_submit_button("➕ Adicionar"):
            if nome and discs:
                st.session_state.professores.append(Professor(
                    nome=nome,
                    disciplinas=discs,
                    disponibilidade_dias=set(dias),
                    disponibilidade_horarios=set(horarios_disp)
                ))
                st.rerun()
    for p in st.session_state.professores[:]:
        with st.expander(p.nome):
            with st.form(f"edit_prof_{p.id}"):
                nome = st.text_input("Nome", p.nome, key=f"pn_{p.id}")
                discs_validas = [d for d in p.disciplinas if d in disc_nomes]
                discs = st.multiselect("Disciplinas", disc_nomes, default=discs_validas, key=f"pd_{p.id}")
                dias = st.multiselect("Dias disponíveis", DIAS_SEMANA, 
                                     default=list(p.disponibilidade_dias), key=f"pdias_{p.id}")
                horarios_disp = st.multiselect("Horários disponíveis", [1,2,3,4,5,6,7],
                                              default=list(p.disponibilidade_horarios), key=f"phor_{p.id}")
                col1, col2 = st.columns(2)
                if col1.form_submit_button("💾 Salvar"):
                    st.session_state.professores = [
                        Professor(nome, discs, set(dias), set(horarios_disp), p.restricoes, p.id) if item.id == p.id else item
                        for item in st.session_state.professores
                    ]
                    st.rerun()
                if col2.form_submit_button("🗑️ Excluir"):
                    st.session_state.professores = [
                        item for item in st.session_state.professores if item.id != p.id
                    ]
                    st.rerun()

# =================== ABAS 4-8: IGUAIS AO ORIGINAL ===================
# (Mantenha seu código existente para Turmas, Salas, Calendário, Configurações, Feriados)

# ... [copie seu código original das abas 4 a 8] ...

# =================== ABA 1: INÍCIO ===================
with aba1:
    st.header("Gerar Grade Horária")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Salvar no Banco"):
            try:
                database.salvar_turmas(st.session_state.turmas)
                database.salvar_professores(st.session_state.professores)
                database.salvar_disciplinas(st.session_state.disciplinas)
                database.salvar_salas(st.session_state.salas)
                database.salvar_periodos(getattr(st.session_state, 'periodos', []))
                database.salvar_feriados(getattr(st.session_state, 'feriados', []))
                if "aulas" in st.session_state:
                    database.salvar_grade(st.session_state.aulas)
                st.success("✅ Dados salvos!")
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    with col2:
        if st.button("🔄 Carregar do Banco"):
            try:
                st.session_state.turmas = database.carregar_turmas()
                st.session_state.professores = database.carregar_professores()
                st.session_state.disciplinas = database.carregar_disciplinas()
                st.session_state.salas = database.carregar_salas()
                st.session_state.periodos = database.carregar_periodos() or []
                st.session_state.feriados = database.carregar_feriados() or []
                st.session_state.aulas = database.carregar_grade()
                st.success("✅ Dados carregados!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    if not st.session_state.turmas or not st.session_state.professores or not st.session_state.disciplinas:
        st.warning("⚠️ Cadastre dados antes de gerar grade.")
        st.stop()
    if st.button("🚀 Gerar Grade Completa"):
        with st.spinner("Gerando grade..."):
            try:
                grade = GradeHorariaORTools(
                    st.session_state.turmas,
                    st.session_state.professores,
                    st.session_state.disciplinas,
                    relaxar_horario_ideal=getattr(st.session_state, 'relaxar_horario_ideal', False)
                )
                aulas = grade.resolver()
                metodo = "Google OR-Tools"
            except Exception as e1:
                st.warning("⚠️ OR-Tools falhou. Tentando método simples...")
                try:
                    simple_grade = SimpleGradeHoraria(
                        st.session_state.turmas,
                        st.session_state.professores,
                        st.session_state.disciplinas
                    )
                    aulas = simple_grade.gerar_grade()
                    metodo = "Algoritmo Simples"
                except Exception as e2:
                    st.error(f"❌ Falha total: {str(e2)}")
                    st.stop()
            st.session_state.aulas = aulas
            database.salvar_grade(aulas)
            st.success(f"✅ Grade gerada com {metodo}!")

            df = pd.DataFrame([
                {"Turma": a.turma, "Disciplina": a.disciplina, "Professor": a.professor, "Dia": a.dia, "Horário": a.horario, "Sala": a.sala}
                for a in aulas
            ])
            tabela = df.pivot_table(
                index=["Turma", "Horário"],
                columns="Dia",
                values="Disciplina",
                aggfunc=lambda x: x.iloc[0],
                fill_value=""
            ).reindex(columns=["dom", "seg", "ter", "qua", "qui", "sex", "sab"], fill_value="")
            novo_indice = []
            for turma, horario_num in tabela.index:
                horario_real = HORARIOS_REAIS.get(horario_num, f"{horario_num}ª aula")
                novo_indice.append((turma, horario_real))
            tabela.index = pd.MultiIndex.from_tuples(novo_indice)
            st.dataframe(tabela.style.applymap(color_disciplina), use_container_width=True)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                tabela.to_excel(writer, sheet_name="Grade")
                df.to_excel(writer, sheet_name="Dados", index=False)
            st.download_button("📥 Excel", output.getvalue(), "grade.xlsx")
            pdf_path = "grade_horaria.pdf"
            exportar_para_pdf(aulas, pdf_path)
            with open(pdf_path, "rb") as f:
                st.download_button("📄 PDF", f.read(), "grade.pdf")

            if st.button("📤 Exportar Grade Completa"):
                output = io.BytesIO()
                exportar_grade_por_tipo(aulas, "Grade Completa (Turmas)", output)
                st.download_button(
                    "📥 Baixar Grade",
                    output.getvalue(),
                    "grade_exportada.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# =================== ABAS 9-11: GRADE POR TURMA/SALA/PROFESSOR ===================
with aba9:
    st.header("Grade Semanal por Turma")
    if st.session_state.aulas:
        aulas = st.session_state.aulas
        turmas_lista = sorted(list(set(a.turma for a in aulas)))
        if turmas_lista:
            turma_selecionada = st.selectbox("Selecione a turma", turmas_lista, key="turma_semanal")
            for semana in range(1, 6):
                st.markdown(f"#### Semana {semana}")
                df = gerar_grade_por_turma_semana(aulas, turma_selecionada, semana)
                st.dataframe(df.style.applymap(color_disciplina), use_container_width=True)
        else:
            st.info("Nenhuma turma encontrada.")
    else:
        st.info("⚠️ Gere a grade na aba 'Início' primeiro.")

with aba10:
    st.header("Ocupação Semanal por Sala")
    if st.session_state.aulas:
        aulas = st.session_state.aulas
        salas_lista = sorted(list(set(a.sala for a in aulas)))
        if salas_lista:
            sala_selecionada = st.selectbox("Selecione a sala", salas_lista, key="sala_semanal")
            for semana in range(1, 6):
                st.markdown(f"#### Semana {semana}")
                df = gerar_grade_por_sala_semana(aulas, sala_selecionada, semana)
                st.dataframe(df.style.applymap(color_disciplina), use_container_width=True)
        else:
            st.info("Nenhuma sala encontrada.")
    else:
        st.info("⚠️ Gere a grade na aba 'Início' primeiro.")

with aba11:
    st.header("Grade Semanal por Professor")
    if st.session_state.aulas:
        aulas = st.session_state.aulas
        professores_lista = sorted(list(set(a.professor for a in aulas)))
        if professores_lista:
            prof_selecionado = st.selectbox("Selecione o professor", professores_lista, key="prof_semanal")
            for semana in range(1, 6):
                st.markdown(f"#### Semana {semana}")
                df = gerar_grade_por_professor_semana(aulas, prof_selecionado, semana)
                st.dataframe(df.style.applymap(color_disciplina), use_container_width=True)
        else:
            st.info("Nenhum professor encontrado.")
    else:
        st.info("⚠️ Gere a grade na aba 'Início' primeiro.")