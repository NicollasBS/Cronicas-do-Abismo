# populate_database.py

import sqlite3
import json

DB_FILE = "rpg_database.db"

def create_connection(db_file):
    conn = None;
    try: conn = sqlite3.connect(db_file); return conn
    except sqlite3.Error as e: print(e)
    return conn

def insert_item(conn, item_data):
    sql = ''' INSERT OR IGNORE INTO Item(nome, descricao, peso, valor_moedas, tipo_item) VALUES(?,?,?,?,?) '''
    cur = conn.cursor(); cur.execute(sql, item_data); conn.commit(); return cur.lastrowid

def insert_arma(conn, arma_data):
    sql = ''' INSERT OR IGNORE INTO Arma(item_id, tipo_dano, dado_dano, propriedades, alcance) VALUES(?,?,?,?,?) '''
    cur = conn.cursor(); arma_data_processed = list(arma_data); arma_data_processed[3] = json.dumps(arma_data_processed[3]); cur.execute(sql, tuple(arma_data_processed)); conn.commit()

def insert_armadura(conn, armadura_data):
    sql = ''' INSERT OR IGNORE INTO Armadura(item_id, tipo_armadura, bonus_ca_base, requer_destreza_bonus, max_bonus_destreza, penalidade_furtividade, requisito_forca, bonus_pv) VALUES(?,?,?,?,?,?,?,?) '''
    cur = conn.cursor(); cur.execute(sql, armadura_data); conn.commit()

def insert_magia(conn, magia_data):
    sql = ''' INSERT OR IGNORE INTO Magia(nome, nivel_magia, escola_magia, tempo_conjuracao, alcance_magia, componentes, duracao_magia, descricao_efeito, requer_concentracao, custo_mana) VALUES(?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor(); magia_data_processed = list(magia_data); magia_data_processed[5] = json.dumps(magia_data_processed[5]); cur.execute(sql, tuple(magia_data_processed)); conn.commit(); return cur.lastrowid

def insert_personagem(conn, personagem_data):
    sql = ''' INSERT OR IGNORE INTO Personagem(nome, raca, classe_personagem, nivel, pontos_vida_maximos, pontos_vida_atuais, pontos_mana_maximos, pontos_mana_atuais, atributos, proficiencias, tipo_personagem) VALUES(?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor(); personagem_data_processed = list(personagem_data); personagem_data_processed[8] = json.dumps(personagem_data_processed[8]); personagem_data_processed[9] = json.dumps(personagem_data_processed[9]); cur.execute(sql, tuple(personagem_data_processed)); conn.commit(); return cur.lastrowid

def insert_jogador(conn, jogador_data):
    sql = ''' INSERT OR IGNORE INTO Jogador(personagem_id, experiencia, alinhamento, nome_jogador) VALUES(?,?,?,?) '''
    cur = conn.cursor(); cur.execute(sql, jogador_data); conn.commit()

def insert_npc(conn, npc_data):
    sql = ''' INSERT OR IGNORE INTO NPC(personagem_id, tipo_npc, comportamento, dialogo) VALUES(?,?,?,?) '''
    cur = conn.cursor(); cur.execute(sql, npc_data); conn.commit()

def main():
    conn = create_connection(DB_FILE)
    if conn is not None:
        print("Populando banco de dados...")
        
        insert_item(conn, ("Espada Longa", "Uma espada versátil.", 1.4, 15, "Arma"))
        insert_arma(conn, (1, "Cortante", "1d8", ["Versátil (1d10)"], "Corpo a corpo"))
        insert_item(conn, ("Arco Curto", "Um arco leve e rápido.", 1.0, 25, "Arma"))
        insert_arma(conn, (2, "Perfurante", "1d6", ["Duas Mãos", "Munição"], "Distância"))
        
        insert_item(conn, ("Corselete de Couro", "Peitoral de couro endurecido.", 4.5, 10, "Armadura"))
        insert_armadura(conn, (3, "Leve", 11, True, None, False, 0, 2))
        insert_item(conn, ("Cota de Malha", "Armadura de anéis metálicos.", 18.0, 50, "Armadura"))
        insert_armadura(conn, (4, "Pesada", 16, False, None, True, 13, 5))

        insert_magia(conn, ("Mísseis Mágicos", 1, "Evocação", "1 ação", "36 metros", ["V", "S"], "Instantâneo", "Três dardos causam 1d4+1 dano cada.", False, 10))
        insert_magia(conn, ("Bola de Fogo", 3, "Evocação", "1 ação", "45 metros", ["V", "S", "M"], "Instantâneo", "Explosão de fogo em área.", False, 25))
        
        guerreiro_attrs = {"Força": 16, "Destreza": 10, "Constituição": 14, "Inteligência": 8, "Sabedoria": 12, "Carisma": 9}
        guerreiro_profs = ["Armaduras Pesadas", "Escudos", "Machados", "Atletismo"]
        guerreiro_id = insert_personagem(conn, ("Durin", "Anão da Montanha", "Guerreiro", 1, 12, 12, 0, 0, guerreiro_attrs, guerreiro_profs, "Jogador"))
        if guerreiro_id: insert_jogador(conn, (guerreiro_id, 0, "Leal e Bom", "Jogador1"))
        
        mago_attrs = {"Força": 8, "Destreza": 14, "Constituição": 12, "Inteligência": 16, "Sabedoria": 10, "Carisma": 11}
        mago_profs = ["Arcanismo", "História", "Adagas", "Bordões"]
        mago_id = insert_personagem(conn, ("Elara", "Alta Elfa", "Mago", 1, 8, 8, 50, 50, mago_attrs, mago_profs, "Jogador"))
        if mago_id: insert_jogador(conn, (mago_id, 0, "Neutro e Bom", "Jogador2"))
        
        goblin_attrs = {"Força": 8, "Destreza": 14, "Constituição": 10, "Inteligência": 10, "Sabedoria": 8, "Carisma": 8}
        goblin_profs = ["Furtividade"]
        goblin_id = insert_personagem(conn, ("Snaga", "Goblin", "Ladino", 1, 7, 7, 10, 10, goblin_attrs, goblin_profs, "NPC"))
        if goblin_id: insert_npc(conn, (goblin_id, "Monstro", "Agressivo", "Yarr! Morra!"))

        print("Banco de dados populado com sucesso!")
        conn.close()
    else:
        print("Erro! Não foi possível criar a conexão com o banco de dados.")

if __name__ == '__main__':
    main()