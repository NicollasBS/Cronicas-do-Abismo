# save_manager.py

import json
import os
import time
from rpg_model import Jogador

SAVES_DIR = "saves"

def ensure_saves_dir_exists():
    """Garante que o diretório de saves exista."""
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR)

def save_game(player: Jogador):
    """
    Salva o estado do jogador. Se for a primeira vez, cria um novo arquivo.
    Se já houver um save, ele o sobrescreve.
    """
    ensure_saves_dir_exists()
    
    # Se o jogador não tem um ID de save, é a primeira vez que está sendo salvo.
    if not player.save_id:
        # Gera um ID único e o atribui ao jogador.
        player.save_id = int(time.time())

    # O nome do arquivo agora é baseado no ID de save permanente do personagem.
    save_filename = f"save_{player.save_id}.json"
    filepath = os.path.join(SAVES_DIR, save_filename)

    player_state = {
        "save_id": player.save_id,  # Salva o ID junto com os outros dados
        "id_entidade": player.id,
        "nome": player.nome,
        "raca": player.raca,
        "classe_personagem": player.classe_personagem,
        "nivel": player.nivel,
        "pontos_vida_maximos": player.pontos_vida_maximos,
        "pontos_vida_atuais": player.pontos_vida_atuais,
        "atributos": player.atributos,
        "proficiencias": player.proficiencias,
        "experiencia": player.experiencia,
        "alinhamento": player.alinhamento,
        "nome_jogador": player.nome_jogador
    }

    try:
        # O modo 'w' (write) já sobrescreve o arquivo se ele existir.
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(player_state, f, indent=4, ensure_ascii=False)
        print(f"Jogo salvo com sucesso em {filepath}")
        return True
    except Exception as e:
        print(f"Erro ao salvar o jogo: {e}")
        return False

def list_saved_games() -> list[dict]:
    """Lê o diretório de saves e retorna uma lista com os dados principais."""
    ensure_saves_dir_exists()
    saved_games = []
    for filename in os.listdir(SAVES_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(SAVES_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    saved_games.append({
                        "char_name": data.get("nome", "Desconhecido"),
                        "level": data.get("nivel", "?"),
                        "class": data.get("classe_personagem", "N/A"),
                        "filepath": filepath
                    })
            except Exception as e:
                print(f"Erro ao ler o arquivo de save {filename}: {e}")
    return saved_games

def load_game(filepath: str) -> Jogador | None:
    """Carrega o estado do jogador de um arquivo de save específico."""
    if not os.path.exists(filepath):
        print(f"Arquivo de save não encontrado: {filepath}")
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            player_state = json.load(f)

        # Agora passamos o save_id ao recriar o objeto Jogador.
        loaded_player = Jogador(
            id_entidade=player_state["id_entidade"],
            nome=player_state["nome"],
            raca=player_state["raca"],
            classe_personagem=player_state["classe_personagem"],
            nivel=player_state["nivel"],
            pontos_vida_maximos=player_state["pontos_vida_maximos"],
            atributos=player_state["atributos"],
            proficiencias=player_state["proficiencias"],
            experiencia=player_state["experiencia"],
            alinhamento=player_state["alinhamento"],
            nome_jogador=player_state["nome_jogador"],
            save_id=player_state.get("save_id")  # Carrega o ID do save
        )
        loaded_player.pontos_vida_atuais = player_state["pontos_vida_atuais"]
        
        print(f"Jogo carregado com sucesso de {filepath}!")
        return loaded_player

    except Exception as e:
        print(f"Erro ao carregar o jogo de {filepath}: {e}")
        return None