# -*- coding: utf-8 -*-
"""Script para criar a estrutura inicial do banco de dados SQLite para o RPG D&D."""

import sqlite3
import json

# Nome do arquivo do banco de dados
DB_FILE = "rpg_database.db"

def create_connection(db_file):
    """Cria uma conexão com o banco de dados SQLite especificado por db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Conexão com SQLite DB versão {sqlite3.sqlite_version} estabelecida.")
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """Cria uma tabela usando a instrução SQL fornecida."""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def main():

    conn = create_connection(DB_FILE)

    if conn is not None:
        # --- Criação das Tabelas --- #

        # Tabela Item (Tabela base para todos os itens)
        sql_create_item_table = """ CREATE TABLE IF NOT EXISTS Item (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        nome TEXT NOT NULL,
                                        descricao TEXT,
                                        peso REAL,
                                        valor_moedas INTEGER,
                                        tipo_item TEXT NOT NULL CHECK(tipo_item IN ('Arma', 'Armadura', 'Pocao', 'Outro'))
                                    ); """
        create_table(conn, sql_create_item_table)

        # Tabela Arma (Detalhes específicos de armas, herda de Item)
        sql_create_arma_table = """ CREATE TABLE IF NOT EXISTS Arma (
                                        item_id INTEGER PRIMARY KEY,
                                        tipo_dano TEXT,
                                        dado_dano TEXT,
                                        propriedades TEXT, -- Armazenado como JSON string
                                        alcance TEXT,
                                        FOREIGN KEY (item_id) REFERENCES Item (id) ON DELETE CASCADE
                                    ); """
        create_table(conn, sql_create_arma_table)

        # Tabela Armadura (Detalhes específicos de armaduras, herda de Item)
        sql_create_armadura_table = """ CREATE TABLE IF NOT EXISTS Armadura (
                                            item_id INTEGER PRIMARY KEY,
                                            tipo_armadura TEXT,
                                            bonus_ca_base INTEGER,
                                            requer_destreza_bonus BOOLEAN,
                                            max_bonus_destreza INTEGER,
                                            penalidade_furtividade BOOLEAN,
                                            requisito_forca INTEGER,
                                            bonus_pv INTEGER DEFAULT 0, -- NOVA COLUNA
                                            FOREIGN KEY (item_id) REFERENCES Item (id) ON DELETE CASCADE
                                        ); """
        create_table(conn, sql_create_armadura_table)

        # Tabela Pocao (Detalhes específicos de poções, herda de Item)
        sql_create_pocao_table = """ CREATE TABLE IF NOT EXISTS Pocao (
                                        item_id INTEGER PRIMARY KEY,
                                        efeito TEXT,
                                        duracao_efeito TEXT,
                                        quantidade_cura INTEGER,
                                        FOREIGN KEY (item_id) REFERENCES Item (id) ON DELETE CASCADE
                                    ); """
        create_table(conn, sql_create_pocao_table)

        # Tabela Magia
        sql_create_magia_table = """ CREATE TABLE IF NOT EXISTS Magia (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        nome TEXT NOT NULL UNIQUE,
                                        nivel_magia INTEGER,
                                        escola_magia TEXT,
                                        tempo_conjuracao TEXT,
                                        alcance_magia TEXT,
                                        componentes TEXT, -- Armazenado como JSON string
                                        duracao_magia TEXT,
                                        descricao_efeito TEXT,
                                        requer_concentracao BOOLEAN
                                    ); """
        create_table(conn, sql_create_magia_table)

        # Tabela Personagem (Base para Jogador e NPC)
        sql_create_personagem_table = """ CREATE TABLE IF NOT EXISTS Personagem (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            nome TEXT NOT NULL,
                                            raca TEXT,
                                            classe_personagem TEXT,
                                            nivel INTEGER DEFAULT 1,
                                            pontos_vida_maximos INTEGER,
                                            pontos_vida_atuais INTEGER,
                                            atributos TEXT, -- Armazenado como JSON string (ex: '{"Força": 10, ...}')
                                            proficiencias TEXT, -- Armazenado como JSON string
                                            tipo_personagem TEXT NOT NULL CHECK(tipo_personagem IN ('Jogador', 'NPC'))
                                        ); """
        create_table(conn, sql_create_personagem_table)

        # Tabela Jogador (Detalhes específicos de jogadores)
        sql_create_jogador_table = """ CREATE TABLE IF NOT EXISTS Jogador (
                                            personagem_id INTEGER PRIMARY KEY,
                                            experiencia INTEGER DEFAULT 0,
                                            alinhamento TEXT,
                                            nome_jogador TEXT, -- Nome real do jogador
                                            FOREIGN KEY (personagem_id) REFERENCES Personagem (id) ON DELETE CASCADE
                                        ); """
        create_table(conn, sql_create_jogador_table)

        # Tabela NPC (Detalhes específicos de NPCs)
        sql_create_npc_table = """ CREATE TABLE IF NOT EXISTS NPC (
                                        personagem_id INTEGER PRIMARY KEY,
                                        tipo_npc TEXT, -- Ex: Monstro, Aliado, Comerciante
                                        comportamento TEXT, -- Ex: Agressivo, Neutro
                                        dialogo TEXT,
                                        FOREIGN KEY (personagem_id) REFERENCES Personagem (id) ON DELETE CASCADE
                                    ); """
        create_table(conn, sql_create_npc_table)

        # Tabela Inventario (Relaciona Personagem e Item)
        # Um personagem pode ter várias cópias do mesmo item, por isso uma tabela de junção
        sql_create_inventario_table = """ CREATE TABLE IF NOT EXISTS Inventario (
                                            personagem_id INTEGER NOT NULL,
                                            item_id INTEGER NOT NULL,
                                            quantidade INTEGER DEFAULT 1,
                                            FOREIGN KEY (personagem_id) REFERENCES Personagem (id) ON DELETE CASCADE,
                                            FOREIGN KEY (item_id) REFERENCES Item (id) ON DELETE CASCADE,
                                            PRIMARY KEY (personagem_id, item_id)
                                        ); """
        create_table(conn, sql_create_inventario_table)

        # Tabela Equipamento (Relaciona Personagem e Item equipado)
        # Assumindo um slot por tipo (Arma, Armadura, Escudo etc.)
        sql_create_equipamento_table = """ CREATE TABLE IF NOT EXISTS Equipamento (
                                            personagem_id INTEGER NOT NULL,
                                            slot TEXT NOT NULL CHECK(slot IN ('Arma', 'Armadura', 'Escudo', 'Amuleto', 'Anel1', 'Anel2')), -- Exemplo de slots
                                            item_id INTEGER, -- Pode ser NULL se o slot estiver vazio
                                            FOREIGN KEY (personagem_id) REFERENCES Personagem (id) ON DELETE CASCADE,
                                            FOREIGN KEY (item_id) REFERENCES Item (id) ON DELETE SET NULL,
                                            PRIMARY KEY (personagem_id, slot)
                                        ); """
        create_table(conn, sql_create_equipamento_table)

        # Tabela Magias Conhecidas/Preparadas (Relaciona Personagem e Magia)
        sql_create_magias_personagem_table = """ CREATE TABLE IF NOT EXISTS MagiasPersonagem (
                                                    personagem_id INTEGER NOT NULL,
                                                    magia_id INTEGER NOT NULL,
                                                    status TEXT CHECK(status IN ('Conhecida', 'Preparada')), -- Opcional, dependendo das regras
                                                    FOREIGN KEY (personagem_id) REFERENCES Personagem (id) ON DELETE CASCADE,
                                                    FOREIGN KEY (magia_id) REFERENCES Magia (id) ON DELETE CASCADE,
                                                    PRIMARY KEY (personagem_id, magia_id)
                                                ); """
        create_table(conn, sql_create_magias_personagem_table)

        print("Tabelas criadas com sucesso (se não existiam).")
        conn.close()
        print("Conexão com SQLite fechada.")
    else:
        print("Erro! Não foi possível criar a conexão com o banco de dados.")

if __name__ == '__main__':
    main()

