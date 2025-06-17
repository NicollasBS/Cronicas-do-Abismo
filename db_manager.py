# db_manager.py

import sqlite3
import json
from rpg_model import Arma

# Nome do arquivo do banco de dados
DB_FILE = "rpg_database.db"

def get_class_template(class_name: str) -> dict | None:
    """
    Busca no banco de dados um personagem 'template' da classe especificada
    para usar como base na criação de um novo personagem.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        sql = """SELECT pontos_vida_maximos, atributos, proficiencias, raca
                 FROM Personagem
                 WHERE lower(classe_personagem) = ? AND tipo_personagem = 'Jogador'
                 LIMIT 1"""
        cur.execute(sql, (class_name.lower(),))
        template = cur.fetchone()
        if template:
            atributos = json.loads(template[1])
            proficiencias = json.loads(template[2])
            return {
                "pontos_vida_maximos": template[0],
                "atributos": atributos,
                "proficiencias": proficiencias,
                "raca": template[3]
            }
        return None
    except sqlite3.Error as e:
        print(f"Erro no banco de dados ao buscar template de classe: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_weapons() -> list[Arma]:
    """
    Busca no banco de dados todas as armas disponíveis e retorna uma lista de objetos Arma.
    """
    conn = None
    weapons = []
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        sql = """SELECT
                    i.id, i.nome, i.descricao, i.peso, i.valor_moedas,
                    a.tipo_dano, a.dado_dano, a.propriedades, a.alcance
                 FROM Item i
                 JOIN Arma a ON i.id = a.item_id
                 WHERE i.tipo_item = 'Arma'"""
        cur.execute(sql)
        all_rows = cur.fetchall()
        for row in all_rows:
            propriedades_list = json.loads(row[7])
            weapon = Arma(
                id_entidade=row[0], nome=row[1], descricao=row[2],
                peso=row[3], valor_moedas=row[4], tipo_dano=row[5],
                dado_dano=row[6], propriedades=propriedades_list, alcance=row[8]
            )
            weapons.append(weapon)
        return weapons
    except sqlite3.Error as e:
        print(f"Erro no banco de dados ao buscar armas: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_weapon_by_id(weapon_id: int) -> Arma | None:
    """
    Busca uma arma específica pelo seu ID no banco de dados.
    """
    if weapon_id is None:
        return None
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        sql = """SELECT
                    i.id, i.nome, i.descricao, i.peso, i.valor_moedas,
                    a.tipo_dano, a.dado_dano, a.propriedades, a.alcance
                 FROM Item i
                 JOIN Arma a ON i.id = a.item_id
                 WHERE i.id = ?"""
        cur.execute(sql, (weapon_id,))
        row = cur.fetchone()
        if row:
            propriedades_list = json.loads(row[7])
            weapon = Arma(
                id_entidade=row[0], nome=row[1], descricao=row[2],
                peso=row[3], valor_moedas=row[4], tipo_dano=row[5],
                dado_dano=row[6], propriedades=propriedades_list, alcance=row[8]
            )
            return weapon
        return None
    except sqlite3.Error as e:
        print(f"Erro no banco de dados ao buscar arma pelo ID: {e}")
        return None
    finally:
        if conn:
            conn.close()