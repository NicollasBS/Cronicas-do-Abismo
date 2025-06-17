# db_manager.py

import sqlite3
import json
from rpg_model import Jogador, Arma, Armadura, Magia, NPC

DB_FILE = "rpg_database.db"

def get_class_template(class_name: str) -> dict | None:
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        sql = "SELECT * FROM Personagem WHERE lower(classe_personagem) = ? AND tipo_personagem = 'Jogador' LIMIT 1"
        cur.execute(sql, (class_name.lower(),))
        template = cur.fetchone()
        return dict(template) if template else None
    except: return None
    finally:
        if conn: conn.close()

# Em db_manager.py, substitua a função antiga por esta versão final

def get_all_armors() -> list[Armadura]:
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        sql = "SELECT * FROM Item i JOIN Armadura a ON i.id = a.item_id WHERE i.tipo_item = 'Armadura'"
        cur.execute(sql)
        rows = cur.fetchall()
        
        armaduras = []
        for r in rows:
            armadura_obj = Armadura(
                id_entidade=r["id"], nome=r["nome"], descricao=r["descricao"], peso=r["peso"],
                valor_moedas=r["valor_moedas"], tipo_armadura=r["tipo_armadura"],
                bonus_ca_base=r["bonus_ca_base"], requer_destreza_bonus=r["requer_destreza_bonus"],
                max_bonus_destreza=r["max_bonus_destreza"], penalidade_furtividade=r["penalidade_furtividade"],
                requisito_forca=r["requisito_forca"], 
                # --- LINHA CORRIGIDA ---
                bonus_pv=r["bonus_pv"] # Acessando diretamente, sem o .get()
            )
            armaduras.append(armadura_obj)
        return armaduras
        
    except Exception as e:
        # Mantemos o bloco de exceção para capturar outros possíveis erros futuros
        print("\n" + "="*50)
        print(f"!!! ERRO CRÍTICO ao carregar armaduras do banco de dados: {e}")
        import traceback
        traceback.print_exc()
        print("="*50 + "\n")
        return []
    finally:
        if conn: conn.close()

def get_all_spells() -> list[Magia]:
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        sql = "SELECT * FROM Magia"
        cur.execute(sql)
        rows = cur.fetchall()
        return [Magia(
            id_entidade=r["id"], nome=r["nome"], nivel_magia=r["nivel_magia"],
            escola_magia=r["escola_magia"], tempo_conjuracao=r["tempo_conjuracao"],
            alcance_magia=r["alcance_magia"], componentes=json.loads(r["componentes"]),
            duracao_magia=r["duracao_magia"], descricao_efeito=r["descricao_efeito"],
            requer_concentracao=r["requer_concentracao"], custo_mana=r["custo_mana"]
        ) for r in rows]
    except: return []
    finally:
        if conn: conn.close()

def get_all_weapons() -> list[Arma]:
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        sql = "SELECT * FROM Item i JOIN Arma a ON i.id = a.item_id WHERE i.tipo_item = 'Arma'"
        cur.execute(sql)
        rows = cur.fetchall()
        return [Arma(
            id_entidade=r["id"], nome=r["nome"], descricao=r["descricao"], peso=r["peso"],
            valor_moedas=r["valor_moedas"], tipo_dano=r["tipo_dano"],
            dado_dano=r["dado_dano"], propriedades=json.loads(r["propriedades"]),
            alcance=r["alcance"]
        ) for r in rows]
    except: return []
    finally:
        if conn: conn.close()

def get_random_enemy() -> NPC | None:
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        sql = "SELECT * FROM Personagem p JOIN NPC n ON p.id = n.personagem_id WHERE n.tipo_npc = 'Monstro' ORDER BY RANDOM() LIMIT 1"
        cur.execute(sql)
        row = cur.fetchone()
        if row:
            enemy = NPC(
                id_entidade=row["id"], nome=row["nome"], raca=row["raca"],
                classe_personagem=row["classe_personagem"], nivel=row["nivel"],
                pontos_vida_maximos=row["pontos_vida_maximos"],
                pontos_mana_maximos=row["pontos_mana_maximos"],
                atributos=json.loads(row["atributos"]),
                proficiencias=json.loads(row["proficiencias"]),
                tipo=row["tipo_npc"], comportamento=row["comportamento"], dialogo=row["dialogo"]
            )
            enemy.pontos_vida_atuais = row["pontos_vida_atuais"]
            enemy.pontos_mana_atuais = row["pontos_mana_atuais"]
            return enemy
        return None
    except: return None
    finally:
        if conn: conn.close()