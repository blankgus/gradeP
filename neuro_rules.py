def eh_horario_ideal(tipo_disciplina: str, horario: int) -> bool:
    """Horários ideais considerando recreio na posição 4"""
    if tipo_disciplina == "pesada":
        return horario <= 3  # Até 09:30
    elif tipo_disciplina == "pratica":
        return horario >= 5  # Após recreio
    else:
        return horario != 4  # Qualquer horário exceto recreio