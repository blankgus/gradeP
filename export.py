import pandas as pd
from fpdf import FPDF

def exportar_para_excel(aulas, caminho="grade_horaria.xlsx"):
    df = pd.DataFrame([
        {"Turma": a.turma, "Disciplina": a.disciplina, "Professor": a.professor, "Dia": a.dia, "Horário": a.horario, "Sala": a.sala}
        for a in aulas
    ])
    HORARIOS_REAIS = {
        1: "07:00-07:50",
        2: "07:50-08:40",
        3: "08:40-09:30",
        4: "09:30-09:50",
        5: "09:50-10:40",
        6: "10:40-11:30",
        7: "11:30-12:20"
    }
    df["Horário"] = df["Horário"].map(HORARIOS_REAIS).fillna("Horário Inválido")
    tabela = df.pivot_table(
        index=["Turma", "Horário"],
        columns="Dia",
        values="Disciplina",
        aggfunc=lambda x: x.iloc[0],
        fill_value=""
    ).reindex(columns=["dom", "seg", "ter", "qua", "qui", "sex", "sab"], fill_value="")
    with pd.ExcelWriter(caminho, engine='openpyxl') as writer:
        tabela.to_excel(writer, sheet_name="Grade por Turma")
        df.to_excel(writer, sheet_name="Dados Brutos", index=False)

def exportar_para_pdf(aulas, caminho="grade_horaria.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Grade Horária Escolar", ln=True, align='C')
    pdf.ln(10)
    from collections import defaultdict
    turmas_aulas = defaultdict(list)
    for aula in aulas:
        turmas_aulas[aula.turma].append(aula)
    HORARIOS_REAIS = {
        1: "07:00-07:50",
        2: "07:50-08:40",
        3: "08:40-09:30",
        4: "09:30-09:50",
        5: "09:50-10:40",
        6: "10:40-11:30",
        7: "11:30-12:20"
    }
    for turma in sorted(turmas_aulas.keys()):
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt=f"Turma: {turma}", ln=True)
        pdf.set_font("Arial", size=10)
        aulas_ordenadas = sorted(turmas_aulas[turma], key=lambda x: (x.dia, x.horario))
        for aula in aulas_ordenadas:
            pdf.cell(0, 8, txt=f"{HORARIOS_REAIS.get(aula.horario, str(aula.horario))} - {aula.dia.upper()}: {aula.disciplina} ({aula.professor})", ln=True)
        pdf.ln(5)
    pdf.output(caminho)

def gerar_grade_por_turma_semana(aulas, turma_nome, semana=1):
    is_fundamental = any(s in turma_nome for s in ["6ano", "7ano", "8ano", "9ano"])
    dias = ["seg", "ter", "qua", "qui", "sex"]
    if is_fundamental:
        horarios = [1, 2, 3, 4, 5, 6]
        grade = {h: {d: "Sem Aula" for d in dias} for h in horarios}
        for aula in aulas:
            if aula.turma == turma_nome and aula.dia in dias and aula.horario in horarios:
                grade[aula.horario][aula.dia] = aula.disciplina
        for d in dias:
            grade[3][d] = "INTERVALO"
        HORARIOS_REAIS = {
            1: "07:50-08:40",
            2: "08:40-09:30",
            3: "09:30-09:50",
            4: "09:50-10:40",
            5: "10:40-11:30",
            6: "11:30-12:20"
        }
    else:
        horarios = [1, 2, 3, 4, 5, 6, 7]
        grade = {h: {d: "Sem Aula" for d in dias} for h in horarios}
        for aula in aulas:
            if aula.turma == turma_nome and aula.dia in dias and aula.horario in horarios:
                grade[aula.horario][aula.dia] = aula.disciplina
        for d in dias:
            grade[4][d] = "INTERVALO"
        HORARIOS_REAIS = {
            1: "07:00-07:50",
            2: "07:50-08:40",
            3: "08:40-09:30",
            4: "09:30-09:50",
            5: "09:50-10:40",
            6: "10:40-11:30",
            7: "11:30-12:20"
        }
    df = pd.DataFrame(grade).T
    df.index.name = "Horário"
    df.index = [HORARIOS_REAIS.get(h, str(h)) for h in df.index]
    return df

def gerar_grade_por_sala_semana(aulas, sala_nome, semana=1):
    dias = ["seg", "ter", "qua", "qui", "sex"]
    horarios = [1, 2, 3, 4, 5, 6, 7]
    grade = {h: {d: "Sem Aula" for d in dias} for h in horarios}
    for aula in aulas:
        if aula.sala == sala_nome and aula.dia in dias and aula.horario in horarios:
            grade[aula.horario][aula.dia] = aula.disciplina
    for d in dias:
        grade[4][d] = "INTERVALO"
    df = pd.DataFrame(grade).T
    df.index.name = "Horário"
    HORARIOS_REAIS = {
        1: "07:00-07:50",
        2: "07:50-08:40",
        3: "08:40-09:30",
        4: "09:30-09:50",
        5: "09:50-10:40",
        6: "10:40-11:30",
        7: "11:30-12:20"
    }
    df.index = [HORARIOS_REAIS.get(h, str(h)) for h in df.index]
    return df

def gerar_grade_por_professor_semana(aulas, professor_nome, semana=1):
    dias = ["seg", "ter", "qua", "qui", "sex"]
    horarios = [1, 2, 3, 4, 5, 6, 7]
    grade = {h: {d: "Sem Aula" for d in dias} for h in horarios}
    for aula in aulas:
        if aula.professor == professor_nome and aula.dia in dias and aula.horario in horarios:
            grade[aula.horario][aula.dia] = f"{aula.disciplina}\n{aula.turma}"
    for d in dias:
        grade[4][d] = "INTERVALO"
    df = pd.DataFrame(grade).T
    df.index.name = "Horário"
    HORARIOS_REAIS = {
        1: "07:00-07:50",
        2: "07:50-08:40",
        3: "08:40-09:30",
        4: "09:30-09:50",
        5: "09:50-10:40",
        6: "10:40-11:30",
        7: "11:30-12:20"
    }
    df.index = [HORARIOS_REAIS.get(h, str(h)) for h in df.index]
    return df

def exportar_grade_por_tipo(aulas, tipo_grade, caminho="grade_exportada.xlsx"):
    with pd.ExcelWriter(caminho, engine='openpyxl') as writer:
        if tipo_grade == "Grade Completa (Turmas)":
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
            HORARIOS_REAIS = {
                1: "07:00-07:50",
                2: "07:50-08:40",
                3: "08:40-09:30",
                4: "09:30-09:50",
                5: "09:50-10:40",
                6: "10:40-11:30",
                7: "11:30-12:20"
            }
            novo_indice = []
            for turma, horario_num in tabela.index:
                horario_real = HORARIOS_REAIS.get(horario_num, f"{horario_num}ª aula")
                novo_indice.append((turma, horario_real))
            tabela.index = pd.MultiIndex.from_tuples(novo_indice)
            tabela.to_excel(writer, sheet_name="Grade por Turma")
            df.to_excel(writer, sheet_name="Dados Brutos", index=False)
        elif tipo_grade == "Grade por Turma":
            turmas_lista = sorted(list(set(a.turma for a in aulas)))
            for turma in turmas_lista:
                for semana in range(1, 6):
                    df = gerar_grade_por_turma_semana(aulas, turma, semana)
                    nome_aba = f"Turma_{turma}_Sem{semana}"[:31]
                    df.to_excel(writer, sheet_name=nome_aba)
        elif tipo_grade == "Grade por Sala":
            salas_lista = sorted(list(set(a.sala for a in aulas)))
            for sala in salas_lista:
                for semana in range(1, 6):
                    df = gerar_grade_por_sala_semana(aulas, sala, semana)
                    nome_aba = f"Sala_{sala}_Sem{semana}"[:31]
                    df.to_excel(writer, sheet_name=nome_aba)
        elif tipo_grade == "Grade por Professor":
            professores_lista = sorted(list(set(a.professor for a in aulas)))
            for prof in professores_lista:
                for semana in range(1, 6):
                    df = gerar_grade_por_professor_semana(aulas, prof, semana)
                    nome_aba = f"Prof_{prof}_Sem{semana}"[:31]
                    df.to_excel(writer, sheet_name=nome_aba)

def gerar_relatorio_professor(professor_nome, aulas):
    return pd.DataFrame([{"Professor": professor_nome, "Total Aulas": len([a for a in aulas if a.professor == professor_nome])}])

def gerar_relatorio_todos_professores(aulas):
    return pd.DataFrame([
        {"Professor": p, "Total Aulas": c} 
        for p, c in pd.Series([a.professor for a in aulas]).value_counts().items()
    ])

def gerar_relatorio_disciplina_sala(aulas):
    return pd.DataFrame([
        {"Disciplina": a.disciplina, "Sala": a.sala, "Quantidade": 1} 
        for a in aulas
    ]).groupby(["Disciplina", "Sala"]).sum().reset_index()