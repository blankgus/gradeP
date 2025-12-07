import uuid
from dataclasses import dataclass, field
from typing import List, Set

# Constantes
DIAS_SEMANA = ["seg", "ter", "qua", "qui", "sex"]
HORARIOS_EFII = [1, 2, 3, 4, 5, 6]  # EF II: 6 períodos
HORARIOS_EM = [1, 2, 3, 4, 5, 6, 7]  # EM: 7 períodos (alguns dias)

# Horários reais para cada segmento
HORARIOS_REAIS = {
    "EF_II": {
        1: "07:50-08:40",
        2: "08:40-09:30", 
        3: "09:30-09:50",  # Intervalo EF II
        4: "09:50-10:40",
        5: "10:40-11:30",
        6: "11:30-12:20"
    },
    "EM": {
        1: "07:00-07:50",
        2: "07:50-08:40",
        3: "08:40-09:30",
        4: "09:30-09:50",  # Intervalo EM
        5: "09:50-10:40", 
        6: "10:40-11:30",
        7: "11:30-12:20"   # EM estendido: até 13:10 em alguns dias
    }
}

@dataclass
class Disciplina:
    nome: str
    carga_semanal: int
    tipo: str  # "pesada", "media", "leve", "pratica"
    turmas: List[str]  # ✅ MUDANÇA: Lista de turmas específicas em vez de séries
    grupo: str = "A"  # "A" ou "B"
    cor_fundo: str = "#4A90E2"
    cor_fonte: str = "#FFFFFF"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Professor:
    nome: str
    disciplinas: List[str]  # Nomes das disciplinas que leciona
    disponibilidade: Set[str]  # Dias disponíveis (formato completo: "segunda", "terca", etc.)
    grupo: str = "A"  # "A", "B" ou "AMBOS"
    horarios_indisponiveis: Set[str] = field(default_factory=set)  # Formato: "dia_horario" ex: "seg_1"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Turma:
    nome: str
    serie: str
    turno: str
    grupo: str = "A"  # "A" ou "B"
    segmento: str = "EF_II"  # "EF_II" ou "EM"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Sala:
    nome: str
    capacidade: int
    tipo: str = "normal"  # "normal", "laboratorio", "auditorio"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Aula:
    turma: str
    dia: str  # "seg", "ter", etc.
    horario: int  # 1-7
    horario_real: str  # Horário real no formato "HH:MM-HH:MM"
    disciplina: str
    professor: str
    sala: str
    grupo: str = "A"  # "A" ou "B"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))