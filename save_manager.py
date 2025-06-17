# save_manager.py

import json
import os
import time
from rpg_model import Jogador, Arma, Magia
# O save_manager pode precisar do db_manager para carregar itens/magias no futuro
# from db_manager import get_weapon_by_id 

SAVES_DIR = "saves"

def ensure_saves_dir_exists():
    """Garante que o diretório de saves exista."""
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR)

def save_game(player: Jogador):
    """
    Salva o estado atual do jogador em um arquivo JSON.
    Se for a primeira vez, cria um novo arquivo; senão, sobrescreve o existente.
    """
    ensure_saves_dir_exists()
    
    # Gera um ID para o save se o personagem ainda não tiver um
    if not hasattr(player, 'save_id') or not player.save_id:
        player.save_id = int(time.time())

    save_filename = f"save_{player.save_id}.json"
    filepath = os.path.join(SAVES_DIR, save_filename)

    # Coleta os dados do personagem para salvar
    player_state = {
        "save_id": player.save_id,
        "nome": player.nome,
        "raca": player.raca,
        "classe_personagem": player.classe_personagem,
        "nivel": player.nivel,
        "pontos_vida_maximos": player.pontos_vida_maximos,
        "pontos_vida_atuais": player.pontos_vida_atuais,
        "atributos": player.atributos,
        "proficiencias": player.proficiencias
        # Adicionar aqui outros dados para salvar, como inventário, etc.
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
    """Lista todos os jogos salvos no diretório 'saves'."""
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
    """Carrega um personagem a partir de um arquivo de save."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Recriando o objeto Jogador com os dados básicos
        loaded_player = Jogador(
            id_entidade=1,
            nome=data["nome"],
            raca=data["raca"],
            classe_personagem=data["classe_personagem"],
            nivel=data["nivel"],
            pontos_vida_maximos=data["pontos_vida_maximos"],
            atributos=data["atributos"],
            proficiencias=data["proficiencias"],
            experiencia=data.get("experiencia", 0),
            alinhamento=data.get("alinhamento", "Neutro"),
            nome_jogador=data.get("nome_jogador", "Jogador")
        )
        loaded_player.pontos_vida_atuais = data["pontos_vida_atuais"]
        if hasattr(loaded_player, 'save_id'):
            loaded_player.save_id = data.get("save_id")

        print(f"Jogo {data['nome']} carregado.")
        return loaded_player
    except Exception as e:
        print(f"Falha ao carregar o save: {e}")
        return None