"""Script para popular o banco de dados SQLite com dados de exemplo do D&D 5e."""

import sqlite3
import json

# Nome do arquivo do banco de dados
DB_FILE = "rpg_database.db"

def create_connection(db_file):
    """ Cria uma conexão com o banco de dados SQLite. """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def insert_item(conn, item_data):
    """ Insere um item genérico e retorna o ID. """
    sql = ''' INSERT INTO Item(nome, descricao, peso, valor_moedas, tipo_item)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, item_data)
    conn.commit()
    return cur.lastrowid

def insert_arma(conn, arma_data):
    """ Insere dados específicos de uma arma. """
    sql = ''' INSERT INTO Arma(item_id, tipo_dano, dado_dano, propriedades, alcance)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    arma_data_processed = list(arma_data)
    arma_data_processed[3] = json.dumps(arma_data_processed[3])
    cur.execute(sql, tuple(arma_data_processed))
    conn.commit()

def insert_armadura(conn, armadura_data):
    """ Insere dados específicos de uma armadura. """
    sql = ''' INSERT INTO Armadura(item_id, tipo_armadura, bonus_ca_base, requer_destreza_bonus, max_bonus_destreza, penalidade_furtividade, requisito_forca)
              VALUES(?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, armadura_data)
    conn.commit()

def insert_pocao(conn, pocao_data):
    """ Insere dados específicos de uma poção. """
    sql = ''' INSERT INTO Pocao(item_id, efeito, duracao_efeito, quantidade_cura)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, pocao_data)
    conn.commit()

def insert_magia(conn, magia_data):
    """ Insere uma magia. """
    sql = ''' INSERT INTO Magia(nome, nivel_magia, escola_magia, tempo_conjuracao, alcance_magia, componentes, duracao_magia, descricao_efeito, requer_concentracao)
              VALUES(?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    magia_data_processed = list(magia_data)
    magia_data_processed[5] = json.dumps(magia_data_processed[5])
    cur.execute(sql, tuple(magia_data_processed))
    conn.commit()
    return cur.lastrowid

def insert_personagem(conn, personagem_data):
    """ Insere um personagem base e retorna o ID. """
    sql = ''' INSERT INTO Personagem(nome, raca, classe_personagem, nivel, pontos_vida_maximos, pontos_vida_atuais, atributos, proficiencias, tipo_personagem)
              VALUES(?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    personagem_data_processed = list(personagem_data)
    personagem_data_processed[6] = json.dumps(personagem_data_processed[6]) # atributos
    personagem_data_processed[7] = json.dumps(personagem_data_processed[7]) # proficiencias
    cur.execute(sql, tuple(personagem_data_processed))
    conn.commit()
    return cur.lastrowid

def insert_jogador(conn, jogador_data):
    """ Insere dados específicos de um jogador. """
    sql = ''' INSERT INTO Jogador(personagem_id, experiencia, alinhamento, nome_jogador)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, jogador_data)
    conn.commit()

def insert_npc(conn, npc_data):
    """ Insere dados específicos de um NPC. """
    sql = ''' INSERT INTO NPC(personagem_id, tipo_npc, comportamento, dialogo)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, npc_data)
    conn.commit()

def insert_inventario(conn, inventario_data):
    """ Adiciona um item ao inventário de um personagem. """
    sql = ''' INSERT INTO Inventario(personagem_id, item_id, quantidade)
              VALUES(?,?,?) ON CONFLICT(personagem_id, item_id) DO UPDATE SET quantidade = quantidade + excluded.quantidade'''
    cur = conn.cursor()
    cur.execute(sql, inventario_data)
    conn.commit()

def insert_equipamento(conn, equipamento_data):
    """ Equipa um item em um slot de personagem. """
    sql = ''' INSERT INTO Equipamento(personagem_id, slot, item_id)
              VALUES(?,?,?) ON CONFLICT(personagem_id, slot) DO UPDATE SET item_id = excluded.item_id'''
    cur = conn.cursor()
    cur.execute(sql, equipamento_data)
    conn.commit()

def main():

    conn = create_connection(DB_FILE)

    if conn is not None:
        print("Populando banco de dados...")

        # --- Inserir Itens --- #
        # Arma: Espada Longa
        espada_longa_id = insert_item(conn, ("Espada Longa", "Uma espada versátil.", 1.4, 15, "Arma"))
        insert_arma(conn, (espada_longa_id, "Cortante", "1d8", ["Versátil (1d10)"], "Corpo a corpo"))

        # Arma: Arco Curto
        arco_curto_id = insert_item(conn, ("Arco Curto", "Um arco leve e rápido.", 1.0, 25, "Arma"))
        insert_arma(conn, (arco_curto_id, "Perfurante", "1d6", ["Duas Mãos", "Munição (distância 80/320)"], "Distância"))

        # Armadura: Corselete de Couro
        couro_id = insert_item(conn, ("Corselete de Couro", "Peitoral de couro endurecido.", 4.5, 10, "Armadura"))
        insert_armadura(conn, (couro_id, "Leve", 11, True, None, False, 0))

        # Armadura: Cota de Malha
        cota_malha_id = insert_item(conn, ("Cota de Malha", "Armadura de anéis metálicos.", 18.0, 50, "Armadura"))
        insert_armadura(conn, (cota_malha_id, "Pesada", 16, False, None, True, 13))

        # Poção: Poção de Cura
        pocao_cura_id = insert_item(conn, ("Poção de Cura", "Líquido vermelho que restaura vida.", 0.2, 50, "Pocao"))
        insert_pocao(conn, (pocao_cura_id, "Cura 2d4+2 PV", "Instantâneo", 7)) # Usando média de 2d4+2

        # --- Inserir Magias --- #
        # bola_fogo_id = insert_magia(conn, ("Bola de Fogo", 3, "Evocação", "1 ação", "45 metros", ["V", "S", "M"], "Instantâneo", "Explosão de fogo em área.", False))
        # curar_ferimentos_id = insert_magia(conn, ("Curar Ferimentos", 1, "Evocação", "1 ação", "Toque", ["V", "S"], "Instantâneo", "Restaura 1d8+mod PV.", False))
        # misseis_magicos_id = insert_magia(conn, ("Mísseis Mágicos", 1, "Evocação", "1 ação", "36 metros", ["V", "S"], "Instantâneo", "Três dardos causam 1d4+1 dano cada.", False))

        # --- Inserir Personagens --- #
        # Jogador: Guerreiro Anão
        guerreiro_attrs = {"Força": 16, "Destreza": 10, "Constituição": 14, "Inteligência": 8, "Sabedoria": 12, "Carisma": 9}
        guerreiro_profs = ["Armaduras Pesadas", "Escudos", "Machados", "Atletismo"]
        guerreiro_id = insert_personagem(conn, ("Durin", "Anão da Montanha", "Guerreiro", 1, 12, 12, guerreiro_attrs, guerreiro_profs, "Jogador"))
        insert_jogador(conn, (guerreiro_id, 0, "Leal e Bom", "Jogador1"))

        # Jogador: Mago Elfo
        mago_attrs = {"Força": 8, "Destreza": 14, "Constituição": 12, "Inteligência": 16, "Sabedoria": 10, "Carisma": 11}
        mago_profs = ["Arcanismo", "História", "Adagas", "Bordões"]
        mago_id = insert_personagem(conn, ("Elara", "Alta Elfa", "Mago", 1, 8, 8, mago_attrs, mago_profs, "Jogador"))
        insert_jogador(conn, (mago_id, 0, "Neutro e Bom", "Jogador2"))

        # NPC: Goblin
        goblin_attrs = {"Força": 8, "Destreza": 14, "Constituição": 10, "Inteligência": 10, "Sabedoria": 8, "Carisma": 8}
        goblin_profs = ["Furtividade"]
        goblin_id = insert_personagem(conn, ("Snaga", "Goblin", "Nenhuma", 1, 7, 7, goblin_attrs, goblin_profs, "NPC"))
        insert_npc(conn, (goblin_id, "Monstro", "Agressivo", "Yarr! Morra!"))

        # NPC: Comerciante Humano
        comerciante_attrs = {"Força": 10, "Destreza": 11, "Constituição": 12, "Inteligência": 13, "Sabedoria": 14, "Carisma": 15}
        comerciante_profs = ["Persuasão", "Intuição"]
        comerciante_id = insert_personagem(conn, ("Bartholomew", "Humano", "Comum", 2, 10, 10, comerciante_attrs, comerciante_profs, "NPC"))
        insert_npc(conn, (comerciante_id, "Comerciante", "Neutro", "Bem-vindo à minha loja! O que procura?"))

        # --- Relacionamentos --- #
        # Inventário Inicial
        insert_inventario(conn, (guerreiro_id, cota_malha_id, 1))
        insert_inventario(conn, (guerreiro_id, espada_longa_id, 1)) # Machado seria melhor, mas usando espada como exemplo
        insert_inventario(conn, (guerreiro_id, pocao_cura_id, 2))
        insert_inventario(conn, (mago_id, couro_id, 1))
        insert_inventario(conn, (mago_id, pocao_cura_id, 1))
        insert_inventario(conn, (goblin_id, arco_curto_id, 1))

        # Equipamento Inicial
        insert_equipamento(conn, (guerreiro_id, "Armadura", cota_malha_id))
        insert_equipamento(conn, (guerreiro_id, "Arma", espada_longa_id))
        insert_equipamento(conn, (mago_id, "Armadura", couro_id))
        # Mago começa sem arma equipada, talvez um cajado (não adicionado)
        insert_equipamento(conn, (goblin_id, "Arma", arco_curto_id))

        # Magias Iniciais (Exemplo: Mago conhece algumas)
        # Supondo que MagiasPersonagem relaciona magias conhecidas
        # sql_create_magias_personagem_table = """ CREATE TABLE IF NOT EXISTS MagiasPersonagem (
        #                                             personagem_id INTEGER NOT NULL,
        #                                             magia_id INTEGER NOT NULL,
        #                                             status TEXT CHECK(status IN (
        #                                         ); """
        # Não implementado aqui para simplificar, mas a tabela existe.

        print("Banco de dados populado com sucesso!")
        conn.close()
        print("Conexão com SQLite fechada.")
    else:
        print("Erro! Não foi possível criar a conexão com o banco de dados.")

if __name__ == '__main__':
    main()

