import random
from models import Aula, DIAS_SEMANA, HORARIOS_EFII, HORARIOS_EM, HORARIOS_REAIS
import streamlit as st

class SimpleGradeHoraria:
    def __init__(self, turmas, professores, disciplinas, salas, dias_em_estendido=None):
        self.turmas = turmas
        self.professores = professores
        self.disciplinas = disciplinas
        self.salas = salas
        self.dias_em_estendido = dias_em_estendido or []
        
    def obter_segmento_turma(self, turma_nome):
        """Determina o segmento da turma"""
        if 'em' in turma_nome.lower():
            return "EM"
        else:
            return "EF_II"
    
    def obter_horarios_turma(self, turma_nome):
        """Retorna horários disponíveis para a turma"""
        segmento = self.obter_segmento_turma(turma_nome)
        if segmento == "EM":
            return HORARIOS_EM
        else:
            return HORARIOS_EFII
    
    def obter_horario_real(self, turma_nome, horario):
        """Retorna o horário real formatado"""
        segmento = self.obter_segmento_turma(turma_nome)
        return HORARIOS_REAIS[segmento].get(horario, "")
    
    def _eh_horario_intervalo(self, turma_nome, horario):
        """Verifica se é horário de intervalo"""
        segmento = self.obter_segmento_turma(turma_nome)
        if segmento == "EF_II":
            return horario == 3  # EF II: intervalo no 3º horário
        elif segmento == "EM":
            return horario == 4  # EM: intervalo no 4º horário
        return False
    
    def _professor_disponivel(self, professor, dia, horario, aulas_alocadas):
        """Verifica se professor está disponível no horário"""
        # Converter dia para formato completo para compatibilidade
        dia_completo = self._converter_dia_para_completo(dia)
        
        # Verificar disponibilidade no dia
        if dia_completo not in professor.disponibilidade:
            return False
        
        # Verificar horários indisponíveis
        horario_key = f"{dia}_{horario}"
        if horario_key in professor.horarios_indisponiveis:
            return False
        
        # Verificar se professor já tem aula neste horário
        for aula in aulas_alocadas:
            if (aula.professor == professor.nome and 
                aula.dia == dia and aula.horario == horario):
                return False
        
        return True
    
    def _converter_dia_para_completo(self, dia):
        """Converte dia abreviado para completo"""
        mapping = {
            "seg": "segunda", "ter": "terca", "qua": "quarta",
            "qui": "quinta", "sex": "sexta"
        }
        return mapping.get(dia, dia)
    
    def _sala_disponivel(self, sala, dia, horario, aulas_alocadas):
        """Verifica se sala está disponível no horário"""
        for aula in aulas_alocadas:
            if (aula.sala == sala.nome and 
                aula.dia == dia and aula.horario == horario):
                return False
        return True
    
    def gerar_grade(self):
        """Gera grade usando algoritmo simples"""
        try:
            aulas_alocadas = []
            tentativas_maximas = 1000
            
            # Para cada turma, alocar disciplinas
            for turma in self.turmas:
                turma_nome = turma.nome
                grupo_turma = turma.grupo
                horarios_turma = self.obter_horarios_turma(turma_nome)
                
                # Disciplinas desta turma (do mesmo grupo)
                disciplinas_turma = []
                for disc in self.disciplinas:
                    if turma_nome in disc.turmas and disc.grupo == grupo_turma:
                        # Adicionar múltiplas instâncias baseado na carga horária
                        for _ in range(disc.carga_semanal):
                            disciplinas_turma.append(disc)
                
                # Embaralhar disciplinas para distribuição aleatória
                random.shuffle(disciplinas_turma)
                
                # Tentar alocar cada disciplina
                for disc in disciplinas_turma:
                    alocada = False
                    tentativas = 0
                    
                    while not alocada and tentativas < tentativas_maximas:
                        tentativas += 1
                        
                        # Escolher dia e horário aleatório
                        dia = random.choice(DIAS_SEMANA)
                        horario = random.choice(horarios_turma)
                        
                        # Pular horário de intervalo
                        if self._eh_horario_intervalo(turma_nome, horario):
                            continue
                        
                        # Verificar se turma já tem aula neste horário
                        turma_ocupada = any(
                            a for a in aulas_alocadas 
                            if a.turma == turma_nome and a.dia == dia and a.horario == horario
                        )
                        if turma_ocupada:
                            continue
                        
                        # Encontrar professor disponível
                        professores_validos = []
                        for prof in self.professores:
                            if (disc.nome in prof.disciplinas and 
                                prof.grupo in [grupo_turma, "AMBOS"] and
                                self._professor_disponivel(prof, dia, horario, aulas_alocadas)):
                                professores_validos.append(prof)
                        
                        if not professores_validos:
                            continue
                        
                        # Encontrar sala disponível
                        salas_validas = []
                        for sala in self.salas:
                            if self._sala_disponivel(sala, dia, horario, aulas_alocadas):
                                salas_validas.append(sala)
                        
                        if not salas_validas:
                            continue
                        
                        # Alocar aula
                        professor = random.choice(professores_validos)
                        sala = random.choice(salas_validas)
                        horario_real = self.obter_horario_real(turma_nome, horario)
                        
                        aula = Aula(
                            turma=turma_nome,
                            dia=dia,
                            horario=horario,
                            horario_real=horario_real,
                            disciplina=disc.nome,
                            professor=professor.nome,
                            sala=sala.nome,
                            grupo=grupo_turma
                        )
                        
                        aulas_alocadas.append(aula)
                        alocada = True
                    
                    if not alocada:
                        st.warning(f"⚠️ Não foi possível alocar {disc.nome} para {turma_nome}")
            
            return aulas_alocadas
            
        except Exception as e:
            st.error(f"❌ Erro no algoritmo simples: {str(e)}")
            return None