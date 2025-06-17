# db_manager.py

import sqlite3
import json
from rpg_model import Jogador, Arma, Armadura, Magia

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
    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")
        return None
    finally:
        if conn: conn.close()

def get_all_armors() -> list[Armadura]:
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        sql = "SELECT * FROM Item i JOIN Armadura a ON i.id = a.item_id WHERE i.tipo_item = 'Armadura'"
        cur.execute(sql)
        rows = cur.fetchall()
        armors = [Armadura(
            id_entidade=r["id"], nome=r["nome"], descricao=r["descricao"], peso=r["peso"],
            valor_moedas=r["valor_moedas"], tipo_armadura=r["tipo_armadura"],
            bonus_ca_base=r["bonus_ca_base"], requer_destreza_bonus=r["requer_destreza_bonus"],
            max_bonus_destreza=r["max_bonus_destreza"], penalidade_furtividade=r["penalidade_furtividade"],
            requisito_forca=r["requisito_forca"], bonus_pv=r["bonus_pv"]
        ) for r in rows]
        return armors
    except Exception as e:
        print(f"Erro ao buscar armaduras: {e}"); return []
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
        spells = [Magia(
            id_entidade=r["id"], nome=r["nome"], nivel_magia=r["nivel_magia"],
            escola_magia=r["escola_magia"], tempo_conjuracao=r["tempo_conjuracao"],
            alcance_magia=r["alcance_magia"], componentes=json.loads(r["componentes"]),
            duracao_magia=r["duracao_magia"], descricao_efeito=r["descricao_efeito"],
            requer_concentracao=r["requer_concentracao"]
        ) for r in rows]
        return spells
    except Exception as e:
        print(f"Erro ao buscar magias: {e}"); return []
    finally:
        if conn: conn.close()

def get_all_weapons() -> list[Arma]:
    """
    Busca todas as armas disponíveis e retorna uma lista de objetos Arma.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        sql = "SELECT * FROM Item i JOIN Arma a ON i.id = a.item_id WHERE i.tipo_item = 'Arma'"
        cur.execute(sql)
        rows = cur.fetchall()
        weapons = [Arma(
            id_entidade=r["id"], nome=r["nome"], descricao=r["descricao"], peso=r["peso"],
            valor_moedas=r["valor_moedas"], tipo_dano=r["tipo_dano"],
            dado_dano=r["dado_dano"], propriedades=json.loads(r["propriedades"]),
            alcance=r["alcance"]
        ) for r in rows]
        return weapons
    except Exception as e:
        print(f"Erro ao buscar armas: {e}"); return []
    finally:
        if conn: conn.close()