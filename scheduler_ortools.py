from ortools.sat.python import cp_model
from models import Aula, DIAS_SEMANA, HORARIOS_EFII, HORARIOS_EM, HORARIOS_REAIS
import streamlit as st

class GradeHorariaORTools:
    def __init__(self, turmas, professores, disciplinas, salas, dias_em_estendido=None):
        self.turmas = turmas
        self.professores = professores
        self.disciplinas = disciplinas
        self.salas = salas
        self.dias_em_estendido = dias_em_estendido or []
        
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        
        # Variáveis de decisão
        self.aulas_vars = {}  # (turma, disciplina, dia, horario) -> (professor, sala)
        
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
    
    def gerar_grade(self):
        """Gera a grade horária usando OR-Tools"""
        try:
            self._criar_variaveis()
            self._adicionar_restricoes()
            
            # Resolver
            status = self.solver.Solve(self.model)
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                return self._extrair_solucao()
            else:
                st.error(f"❌ Não foi possível encontrar solução. Status: {status}")
                return None
                
        except Exception as e:
            st.error(f"❌ Erro no OR-Tools: {str(e)}")
            return None
    
    def _criar_variaveis(self):
        """Cria variáveis de decisão"""
        for turma in self.turmas:
            turma_nome = turma.nome
            grupo_turma = turma.grupo
            horarios_turma = self.obter_horarios_turma(turma_nome)
            
            # Disciplinas desta turma (do mesmo grupo)
            disciplinas_turma = []
            for disc in self.disciplinas:
                if turma_nome in disc.turmas and disc.grupo == grupo_turma:
                    disciplinas_turma.append(disc)
            
            for disc in disciplinas_turma:
                for dia in DIAS_SEMANA:
                    for horario in horarios_turma:
                        # Verificar se é horário de intervalo
                        if self._eh_horario_intervalo(turma_nome, horario):
                            continue
                            
                        # Professores que podem lecionar esta disciplina
                        professores_validos = []
                        for prof in self.professores:
                            if (disc.nome in prof.disciplinas and 
                                prof.grupo in [grupo_turma, "AMBOS"] and
                                self._professor_disponivel(prof, dia, horario)):
                                professores_validos.append(prof.nome)
                        
                        # Salas disponíveis
                        salas_validas = [sala.nome for sala in self.salas]
                        
                        if professores_validos and salas_validas:
                            key = (turma_nome, disc.nome, dia, horario)
                            self.aulas_vars[key] = {
                                'professor': self.model.NewIntVar(0, len(professores_validos)-1, f'prof_{key}'),
                                'sala': self.model.NewIntVar(0, len(salas_validas)-1, f'sala_{key}'),
                                'professores_list': professores_validos,
                                'salas_list': salas_validas
                            }
    
    def _eh_horario_intervalo(self, turma_nome, horario):
        """Verifica se é horário de intervalo"""
        segmento = self.obter_segmento_turma(turma_nome)
        if segmento == "EF_II":
            return horario == 3  # EF II: intervalo no 3º horário
        elif segmento == "EM":
            return horario == 4  # EM: intervalo no 4º horário
        return False
    
    def _professor_disponivel(self, professor, dia, horario):
        """Verifica se professor está disponível no horário"""
        # Converter dia para formato completo para compatibilidade
        dia_completo = self._converter_dia_para_completo(dia)
        
        # Verificar disponibilidade no dia
        if dia_completo not in professor.disponibilidade:
            return False
        
        # Verificar horários indisponíveis
        horario_key = f"{dia}_{horario}"
        return horario_key not in professor.horarios_indisponiveis
    
    def _converter_dia_para_completo(self, dia):
        """Converte dia abreviado para completo"""
        mapping = {
            "seg": "segunda", "ter": "terca", "qua": "quarta",
            "qui": "quinta", "sex": "sexta"
        }
        return mapping.get(dia, dia)
    
    def _adicionar_restricoes(self):
        """Adiciona restrições ao modelo"""
        self._adicionar_restricao_uma_aula_por_turma_horario()
        self._adicionar_restricao_professor_uma_aula_por_horario()
        self._adicionar_restricao_sala_uma_aula_por_horario()
        self._adicionar_restricao_carga_horaria()
    
    def _adicionar_restricao_uma_aula_por_turma_horario(self):
        """Cada turma tem no máximo uma aula por horário"""
        for turma in self.turmas:
            turma_nome = turma.nome
            horarios_turma = self.obter_horarios_turma(turma_nome)
            
            for dia in DIAS_SEMANA:
                for horario in horarios_turma:
                    aulas_no_horario = []
                    for key in self.aulas_vars:
                        if key[0] == turma_nome and key[2] == dia and key[3] == horario:
                            aulas_no_horario.append(1)  # Usar constante 1 para indicar presença
                    
                    if aulas_no_horario:
                        self.model.Add(sum(aulas_no_horario) <= 1)
    
    def _adicionar_restricao_professor_uma_aula_por_horario(self):
        """Cada professor tem no máximo uma aula por horário"""
        for prof in self.professores:
            for dia in DIAS_SEMANA:
                for horario in range(1, 8):  # Todos horários possíveis 1-7
                    aulas_prof = []
                    for key, var_info in self.aulas_vars.items():
                        if (key[2] == dia and key[3] == horario and 
                            prof.nome in var_info['professores_list']):
                            # Adicionar variável indicadora se este professor foi escolhido
                            prof_index = var_info['professores_list'].index(prof.nome)
                            aulas_prof.append(var_info['professor'] == prof_index)
                    
                    if aulas_prof:
                        self.model.Add(sum(aulas_prof) <= 1)
    
    def _adicionar_restricao_sala_uma_aula_por_horario(self):
        """Cada sala tem no máximo uma aula por horário"""
        for sala in self.salas:
            sala_nome = sala.nome
            for dia in DIAS_SEMANA:
                for horario in range(1, 8):
                    aulas_sala = []
                    for key, var_info in self.aulas_vars.items():
                        if (key[2] == dia and key[3] == horario and
                            sala_nome in var_info['salas_list']):
                            sala_index = var_info['salas_list'].index(sala_nome)
                            aulas_sala.append(var_info['sala'] == sala_index)
                    
                    if aulas_sala:
                        self.model.Add(sum(aulas_sala) <= 1)
    
    def _adicionar_restricao_carga_horaria(self):
        """Garante que cada disciplina tenha sua carga horária atendida"""
        for turma in self.turmas:
            turma_nome = turma.nome
            grupo_turma = turma.grupo
            
            for disc in self.disciplinas:
                if turma_nome in disc.turmas and disc.grupo == grupo_turma:
                    aulas_disc = []
                    for key in self.aulas_vars:
                        if key[0] == turma_nome and key[1] == disc.nome:
                            aulas_disc.append(1)  # Constante 1 para cada aula
                    
                    if aulas_disc:
                        self.model.Add(sum(aulas_disc) == disc.carga_semanal)
    
    def _extrair_solucao(self):
        """Extrai a solução do solver"""
        aulas = []
        
        for key, var_info in self.aulas_vars.items():
            turma_nome, disc_nome, dia, horario = key
            
            prof_index = self.solver.Value(var_info['professor'])
            sala_index = self.solver.Value(var_info['sala'])
            
            professor = var_info['professores_list'][prof_index]
            sala = var_info['salas_list'][sala_index]
            
            # Obter grupo da turma
            turma_grupo = next((t.grupo for t in self.turmas if t.nome == turma_nome), "A")
            
            # Obter horário real
            horario_real = self.obter_horario_real(turma_nome, horario)
            
            aula = Aula(
                turma=turma_nome,
                dia=dia,
                horario=horario,
                horario_real=horario_real,
                disciplina=disc_nome,
                professor=professor,
                sala=sala,
                grupo=turma_grupo
            )
            aulas.append(aula)
        
        return aulas