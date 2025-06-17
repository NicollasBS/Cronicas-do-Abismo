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
    sql = ''' INSERT INTO Item(nome, descricao, peso, valor_moedas, tipo_item) VALUES(?,?,?,?,?) '''
    cur = conn.cursor(); cur.execute(sql, item_data); conn.commit(); return cur.lastrowid

def insert_arma(conn, arma_data):
    sql = ''' INSERT INTO Arma(item_id, tipo_dano, dado_dano, propriedades, alcance) VALUES(?,?,?,?,?) '''
    cur = conn.cursor(); arma_data_processed = list(arma_data); arma_data_processed[3] = json.dumps(arma_data_processed[3]); cur.execute(sql, tuple(arma_data_processed)); conn.commit()

def insert_armadura(conn, armadura_data):
    # MODIFICADO: Adicionada a coluna bonus_pv
    sql = ''' INSERT INTO Armadura(item_id, tipo_armadura, bonus_ca_base, requer_destreza_bonus, max_bonus_destreza, penalidade_furtividade, requisito_forca, bonus_pv) VALUES(?,?,?,?,?,?,?,?) '''
    cur = conn.cursor(); cur.execute(sql, armadura_data); conn.commit()

# ... (outras funções de insert) ...

def main():
    conn = create_connection(DB_FILE)
    if conn is not None:
        print("Populando banco de dados...")
        
        # Arma: Espada Longa
        espada_longa_id = insert_item(conn, ("Espada Longa", "Uma espada versátil.", 1.4, 15, "Arma"))
        insert_arma(conn, (espada_longa_id, "Cortante", "1d8", ["Versátil (1d10)"], "Corpo a corpo"))
        
        # Armadura: Corselete de Couro com bônus de vida
        couro_id = insert_item(conn, ("Corselete de Couro", "Peitoral de couro endurecido.", 4.5, 10, "Armadura"))
        insert_armadura(conn, (couro_id, "Leve", 11, True, None, False, 0, 2)) # +2 PV

        # Armadura: Cota de Malha com bônus de vida
        cota_malha_id = insert_item(conn, ("Cota de Malha", "Armadura de anéis metálicos.", 18.0, 50, "Armadura"))
        insert_armadura(conn, (cota_malha_id, "Pesada", 16, False, None, True, 13, 5)) # +5 PV

        # ... (código para inserir personagens, etc.)
        
        print("Banco de dados populado com sucesso!")
        conn.close()
    else:
        print("Erro! Não foi possível criar a conexão com o banco de dados.")

if __name__ == '__main__':
    main()