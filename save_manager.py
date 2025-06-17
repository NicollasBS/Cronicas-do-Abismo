# save_manager.py

import json
import os
import time
from rpg_model import Jogador, Arma
# Precisamos da nova função do db_manager
from db_manager import get_weapon_by_id

SAVES_DIR = "saves"

def ensure_saves_dir_exists():
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR)

def save_game(player: Jogador):
    """
    Salva o estado do jogador, incluindo a arma equipada.
    """
    ensure_saves_dir_exists()
    
    if not player.save_id:
        player.save_id = int(time.time())

    save_filename = f"save_{player.save_id}.json"
    filepath = os.path.join(SAVES_DIR, save_filename)

    # Verifica qual arma está equipada para salvar seu ID
    equipped_weapon = player.equipamento.get("Arma")
    equipped_weapon_id = equipped_weapon.id if equipped_weapon else None

    player_state = {
        "save_id": player.save_id,
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
        "nome_jogador": player.nome_jogador,
        # NOVO: Salva o ID da arma equipada
        "equipped_weapon_id": equipped_weapon_id
    }

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(player_state, f, indent=4, ensure_ascii=False)
        print(f"Jogo salvo com sucesso em {filepath}")
        return True
    except Exception as e:
        print(f"Erro ao salvar o jogo: {e}")
        return False

def list_saved_games() -> list[dict]:
    # (Esta função não precisa de alterações)
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
    """
    Carrega o estado do jogador de um arquivo, incluindo a arma equipada.
    """
    if not os.path.exists(filepath):
        print(f"Arquivo de save não encontrado: {filepath}")
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            player_state = json.load(f)

        loaded_player = Jogador(
            id_entidade=player_state["id_entidade"],
            nome=player_state["nome"], raca=player_state["raca"],
            classe_personagem=player_state["classe_personagem"], nivel=player_state["nivel"],
            pontos_vida_maximos=player_state["pontos_vida_maximos"], atributos=player_state["atributos"],
            proficiencias=player_state["proficiencias"], experiencia=player_state["experiencia"],
            alinhamento=player_state["alinhamento"], nome_jogador=player_state["nome_jogador"],
            save_id=player_state.get("save_id")
        )
        loaded_player.pontos_vida_atuais = player_state["pontos_vida_atuais"]
        
        # NOVO: Carrega e re-equipa a arma
        equipped_weapon_id = player_state.get("equipped_weapon_id")
        if equipped_weapon_id:
            weapon = get_weapon_by_id(equipped_weapon_id)
            if weapon:
                # Adiciona a arma ao inventário e a equipa
                loaded_player.adicionar_item_inventario(weapon)
                loaded_player.usar_item(weapon)

        print(f"Jogo carregado com sucesso de {filepath}!")
        return loaded_player

    except Exception as e:
        print(f"Erro ao carregar o jogo de {filepath}: {e}")
        import traceback
        traceback.print_exc()
        return None
    
