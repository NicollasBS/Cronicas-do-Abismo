# save_manager.py

import json
import os
import time
from rpg_model import Jogador, Arma, Magia
from db_manager import get_weapon_by_id # Usado para carregar a arma

SAVES_DIR = "saves"

def ensure_saves_dir_exists():
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR)

def save_game(player: Jogador):
    """
    Salva o estado do jogador, incluindo a arma equipada e magias.
    """
    ensure_saves_dir_exists()
    
    if not hasattr(player, 'save_id') or not player.save_id:
        player.save_id = int(time.time())

    save_filename = f"save_{player.save_id}.json"
    filepath = os.path.join(SAVES_DIR, save_filename)

    equipped_weapon = player.equipamento.get("Arma")
    equipped_weapon_id = equipped_weapon.id if equipped_weapon else None

    # Salva os IDs das magias conhecidas
    known_spell_ids = [spell.id for spell in player.magias]

    player_state = {
        "save_id": player.save_id,
        "nome": player.nome,
        "raca": player.raca,
        "classe_personagem": player.classe_personagem,
        "nivel": player.nivel,
        "pontos_vida_maximos": player.pontos_vida_maximos,
        "pontos_vida_atuais": player.pontos_vida_atuais,
        "atributos": player.atributos,
        "proficiencias": player.proficiencias,
        "equipped_weapon_id": equipped_weapon_id,
        "known_spell_ids": known_spell_ids
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
            except Exception:
                continue
    return saved_games

def load_game(filepath: str) -> Jogador | None:
    # (Esta função precisaria ser expandida para carregar todos os detalhes,
    # mas por agora vamos focar no fluxo principal)
    # A lógica de carregar itens/magias do save precisaria ser implementada aqui.
    # Por simplicidade, vamos manter o foco na re-inclusão dos menus.
    pass