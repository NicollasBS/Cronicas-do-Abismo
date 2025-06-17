# db_manager.py

import sqlite3
import json

# Nome do arquivo do banco de dados, o mesmo dos outros scripts
DB_FILE = "rpg_database.db"

def get_class_template(class_name: str) -> dict | None:
    """
    Busca no banco de dados um personagem 'template' da classe especificada
    para usar como base na criação de um novo personagem.

    Args:
        class_name (str): O nome da classe a ser buscada (ex: "Guerreiro").

    Returns:
        dict | None: Um dicionário com os dados do template ou None se não for encontrado.
    """
    conn = None
    try:
        # Conecta ao banco de dados
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()

        # Busca por um personagem jogador que sirva de modelo para a classe.
        # Usamos lower() para a busca não diferenciar maiúsculas/minúsculas.
        sql = """SELECT pontos_vida_maximos, atributos, proficiencias, raca
                 FROM Personagem
                 WHERE lower(classe_personagem) = ? AND tipo_personagem = 'Jogador'
                 LIMIT 1"""
        
        cur.execute(sql, (class_name.lower(),))
        template = cur.fetchone()

        if template:
            # Se encontrou um resultado, processa os dados
            # Os campos 'atributos' e 'proficiencias' estão como texto JSON no DB
            # e precisam ser convertidos de volta para objetos Python
            atributos = json.loads(template[1])
            proficiencias = json.loads(template[2])
            
            return {
                "pontos_vida_maximos": template[0],
                "atributos": atributos,
                "proficiencias": proficiencias,
                "raca": template[3] # Aproveitamos para pegar a raça do modelo
            }
        # Se a consulta não retornar nada, retorna None
        return None

    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")
        return None
    finally:
        # Garante que a conexão seja sempre fechada
        if conn:
            conn.close()