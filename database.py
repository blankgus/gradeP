import json
import os
from models import Disciplina, Professor, Turma, Sala

# Nome do arquivo de banco de dados
DB_FILE = "escola_db.json"

def carregar_dados():
    """Carrega todos os dados do arquivo JSON"""
    if not os.path.exists(DB_FILE):
        return {
            "disciplinas": [],
            "professores": [], 
            "turmas": [],
            "salas": []
        }
    
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return {
            "disciplinas": [],
            "professores": [],
            "turmas": [],
            "salas": []
        }

def salvar_dados(dados):
    """Salva todos os dados no arquivo JSON"""
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")
        return False

def carregar_disciplinas():
    """Carrega disciplinas do banco de dados"""
    dados = carregar_dados()
    disciplinas = []
    
    for disc_data in dados.get("disciplinas", []):
        try:
            # ✅ CORREÇÃO: Garantir compatibilidade com turmas como lista
            turmas = disc_data.get("turmas", [])
            if isinstance(turmas, str):
                # Se for string, converter para lista (backward compatibility)
                turmas = [turmas] if turmas else []
            
            disciplina = Disciplina(
                nome=disc_data["nome"],
                carga_semanal=disc_data["carga_semanal"],
                tipo=disc_data["tipo"],
                turmas=turmas,  # ✅ AGORA sempre lista
                grupo=disc_data.get("grupo", "A"),
                cor_fundo=disc_data.get("cor_fundo", "#4A90E2"),
                cor_fonte=disc_data.get("cor_fonte", "#FFFFFF"),
                id=disc_data.get("id", str(disc_data.get("_id", "")))
            )
            disciplinas.append(disciplina)
        except Exception as e:
            print(f"Erro ao carregar disciplina {disc_data}: {e}")
    
    return disciplinas

def salvar_disciplinas(disciplinas):
    """Salva disciplinas no banco de dados"""
    dados = carregar_dados()
    
    dados["disciplinas"] = []
    for disc in disciplinas:
        disc_data = {
            "id": disc.id,
            "nome": disc.nome,
            "carga_semanal": disc.carga_semanal,
            "tipo": disc.tipo,
            "turmas": disc.turmas,  # ✅ AGORA salva como lista
            "grupo": disc.grupo,
            "cor_fundo": disc.cor_fundo,
            "cor_fonte": disc.cor_fonte
        }
        dados["disciplinas"].append(disc_data)
    
    return salvar_dados(dados)

def carregar_professores():
    """Carrega professores do banco de dados"""
    dados = carregar_dados()
    professores = []
    
    for prof_data in dados.get("professores", []):
        try:
            professor = Professor(
                nome=prof_data["nome"],
                disciplinas=prof_data["disciplinas"],
                disponibilidade=set(prof_data.get("disponibilidade", [])),
                grupo=prof_data.get("grupo", "A"),
                horarios_indisponiveis=set(prof_data.get("horarios_indisponiveis", [])),
                id=prof_data.get("id", str(prof_data.get("_id", "")))
            )
            professores.append(professor)
        except Exception as e:
            print(f"Erro ao carregar professor {prof_data}: {e}")
    
    return professores

def salvar_professores(professores):
    """Salva professores no banco de dados"""
    dados = carregar_dados()
    
    dados["professores"] = []
    for prof in professores:
        prof_data = {
            "id": prof.id,
            "nome": prof.nome,
            "disciplinas": prof.disciplinas,
            "disponibilidade": list(prof.disponibilidade),
            "grupo": prof.grupo,
            "horarios_indisponiveis": list(prof.horarios_indisponiveis)
        }
        dados["professores"].append(prof_data)
    
    return salvar_dados(dados)

def carregar_turmas():
    """Carrega turmas do banco de dados"""
    dados = carregar_dados()
    turmas = []
    
    for turma_data in dados.get("turmas", []):
        try:
            turma = Turma(
                nome=turma_data["nome"],
                serie=turma_data["serie"],
                turno=turma_data["turno"],
                grupo=turma_data.get("grupo", "A"),
                segmento=turma_data.get("segmento", "EF_II"),
                id=turma_data.get("id", str(turma_data.get("_id", "")))
            )
            turmas.append(turma)
        except Exception as e:
            print(f"Erro ao carregar turma {turma_data}: {e}")
    
    return turmas

def salvar_turmas(turmas):
    """Salva turmas no banco de dados"""
    dados = carregar_dados()
    
    dados["turmas"] = []
    for turma in turmas:
        turma_data = {
            "id": turma.id,
            "nome": turma.nome,
            "serie": turma.serie,
            "turno": turma.turno,
            "grupo": turma.grupo,
            "segmento": turma.segmento
        }
        dados["turmas"].append(turma_data)
    
    return salvar_dados(dados)

def carregar_salas():
    """Carrega salas do banco de dados"""
    dados = carregar_dados()
    salas = []
    
    for sala_data in dados.get("salas", []):
        try:
            sala = Sala(
                nome=sala_data["nome"],
                capacidade=sala_data["capacidade"],
                tipo=sala_data.get("tipo", "normal"),
                id=sala_data.get("id", str(sala_data.get("_id", "")))
            )
            salas.append(sala)
        except Exception as e:
            print(f"Erro ao carregar sala {sala_data}: {e}")
    
    return salas

def salvar_salas(salas):
    """Salva salas no banco de dados"""
    dados = carregar_dados()
    
    dados["salas"] = []
    for sala in salas:
        sala_data = {
            "id": sala.id,
            "nome": sala.nome,
            "capacidade": sala.capacidade,
            "tipo": sala.tipo
        }
        dados["salas"].append(sala_data)
    
    return salvar_dados(dados)

def resetar_banco():
    """Reseta o banco de dados (para desenvolvimento)"""
    try:
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        return True
    except Exception as e:
        print(f"Erro ao resetar banco: {e}")
        return False