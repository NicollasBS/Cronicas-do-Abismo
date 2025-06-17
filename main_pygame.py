# main_pygame.py

import pygame
import sys
import time # Importado para o tratamento de erros
from rpg_model import Jogador, Arma
from db_manager import get_class_template, get_all_weapons
from save_manager import save_game, load_game, list_saved_games

# --- CONSTANTES E INICIALIZAÇÃO ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1500, 750
FPS = 60
PLAYER_SPEED = 2
WHITE, BLACK, RED, GREEN, GRAY, YELLOW = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 150, 0), (100, 100, 100), (255, 255, 0)

# --- FUNÇÃO PRINCIPAL DE INICIALIZAÇÃO ---
# É uma boa prática encapsular a inicialização para evitar problemas
def initialize_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Crônicas do Abismo")
    clock = pygame.time.Clock()
    fonts = {
        "main": pygame.font.Font(None, 36),
        "menu": pygame.font.Font(None, 50),
        "input": pygame.font.Font(None, 32),
        "list": pygame.font.Font(None, 28)
    }
    return screen, clock, fonts

# --- CLASSES DE SPRITE ---
class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, personagem_jogador: Jogador, pos_x, pos_y):
        super().__init__()
        self.personagem_data = personagem_jogador
        self.image = pygame.Surface((40, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(pos_x, pos_y))

    def update(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += PLAYER_SPEED
        self.rect.move_ip(dx, dy)
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())

class WeaponSprite(pygame.sprite.Sprite):
    def __init__(self, player_sprite: PlayerSprite):
        super().__init__()
        self.player_sprite = player_sprite
        self.image = pygame.Surface((20, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=self.player_sprite.rect.center)
        self.offset_x = 30

    def update(self):
        self.rect.centery = self.player_sprite.rect.centery
        self.rect.centerx = self.player_sprite.rect.centerx + self.offset_x

# --- FUNÇÕES DE INTERFACE ---
def draw_text(surface, text, font, color, x, y, center=False):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x, y)) if center else textobj.get_rect(topleft=(x, y))
    surface.blit(textobj, textrect)

def draw_hud(surface, fonts, jogador_sprite: PlayerSprite):
    jogador_data = jogador_sprite.personagem_data
    draw_text(surface, f"{jogador_data.nome} ({jogador_data.classe_personagem} Nv. {jogador_data.nivel})", fonts["main"], WHITE, 10, 10)
    draw_text(surface, f"PV: {jogador_data.pontos_vida_atuais} / {jogador_data.pontos_vida_maximos}", fonts["main"], WHITE, 10, 50)
    pygame.draw.rect(surface, RED, (10, 90, 200, 25))
    vida_percentual = jogador_data.pontos_vida_atuais / jogador_data.pontos_vida_maximos if jogador_data.pontos_vida_maximos > 0 else 0
    pygame.draw.rect(surface, GREEN, (10, 90, 200 * vida_percentual, 25))

# --- TELAS DO JOGO (MENU, CRIAÇÃO, ETC.) ---

def main_menu(screen, clock, fonts):
    # (Código da função como antes, mas recebendo os parâmetros)
    options = ["Novo Jogo", "Carregar Jogo", "Sair"]
    selected_option = 0
    while True:
        screen.fill(BLACK)
        draw_text(screen, "Crônicas do Abismo", fonts["menu"], WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, center=True)
        for i, option in enumerate(options):
            color = YELLOW if i == selected_option else WHITE
            draw_text(screen, option, fonts["main"], color, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + i * 50, center=True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN: selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0: return "new_game"
                    elif selected_option == 1: return "load_game"
                    elif selected_option == 2: pygame.quit(); sys.exit()
        
        pygame.display.flip()
        clock.tick(FPS)

def character_creation_screen(screen, clock, fonts):
    # (Código da função como antes, mas recebendo os parâmetros)
    fields = ["Nome do Personagem", "Classe (Ex: Guerreiro, Mago)"]
    user_inputs = ["", ""]
    current_field = 0
    while True:
        screen.fill(BLACK)
        draw_text(screen, 'Criação de Personagem', fonts["main"], WHITE, SCREEN_WIDTH/2, 20, center=True)
        draw_text(screen, 'Use as classes do banco: Guerreiro, Mago.', fonts["input"], GRAY, SCREEN_WIDTH/2, 70, center=True)
        for i, field in enumerate(fields):
            prompt = f"{field}: {user_inputs[i]}" + ("_" if i == current_field else "")
            draw_text(screen, prompt, fonts["input"], WHITE, 150, 150 + i * 50)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if user_inputs[current_field].strip() != "":
                        current_field += 1
                        if current_field >= len(fields):
                            nome_personagem, classe_personagem_input = user_inputs[0], user_inputs[1]
                            class_data = get_class_template(classe_personagem_input)
                            if not class_data:
                                print(f"Classe '{classe_personagem_input}' não encontrada."); current_field -= 1; user_inputs[current_field] = ""; continue
                            novo_jogador = Jogador(id_entidade=1, nome=nome_personagem, raca=class_data["raca"], classe_personagem=classe_personagem_input.capitalize(), nivel=1, pontos_vida_maximos=class_data["pontos_vida_maximos"], atributos=class_data["atributos"], proficiencias=class_data["proficiencias"], experiencia=0, alinhamento="Neutro", nome_jogador="Jogador")
                            return novo_jogador
                elif event.key == pygame.K_BACKSPACE: user_inputs[current_field] = user_inputs[current_field][:-1]
                else: user_inputs[current_field] += event.unicode
        
        pygame.display.flip()
        clock.tick(FPS)

def weapon_selection_screen(screen, clock, fonts, player_data: Jogador):
    # (Código da função como antes, mas recebendo os parâmetros)
    available_weapons = get_all_weapons()
    if not available_weapons: print("Nenhuma arma encontrada no banco de dados."); return player_data
    selected_index = 0
    while True:
        screen.fill(BLACK)
        draw_text(screen, "Escolha sua Arma Inicial", fonts["main"], WHITE, SCREEN_WIDTH/2, 50, center=True)
        for i, weapon in enumerate(available_weapons):
            color = YELLOW if i == selected_index else WHITE
            draw_text(screen, weapon.nome, fonts["list"], color, 100, 150 + i * 40)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return player_data
                if event.key == pygame.K_UP: selected_index = (selected_index - 1) % len(available_weapons)
                elif event.key == pygame.K_DOWN: selected_index = (selected_index + 1) % len(available_weapons)
                elif event.key == pygame.K_RETURN:
                    chosen_weapon = available_weapons[selected_index]
                    player_data.adicionar_item_inventario(chosen_weapon)
                    player_data.usar_item(chosen_weapon)
                    return player_data
        
        pygame.display.flip()
        clock.tick(FPS)

def load_game_screen(screen, clock, fonts):
    # (Código da função como antes, mas recebendo os parâmetros)
    saved_games = list_saved_games()
    if not saved_games:
        screen.fill(BLACK)
        draw_text(screen, "Nenhum jogo salvo encontrado.", fonts["main"], WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT/2, center=True)
        draw_text(screen, "Pressione qualquer tecla para voltar.", fonts["input"], GRAY, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40, center=True)
        pygame.display.flip(); pygame.time.wait(500)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN: waiting = False
        return None
    
    selected_index = 0
    while True:
        screen.fill(BLACK)
        draw_text(screen, "Selecione um Jogo para Carregar", fonts["main"], WHITE, SCREEN_WIDTH/2, 50, center=True)
        for i, game_data in enumerate(saved_games):
            color = YELLOW if i == selected_index else WHITE
            info_text = f"{game_data['char_name']} - Nível {game_data['level']} {game_data['class']}"
            draw_text(screen, info_text, fonts["list"], color, 100, 150 + i * 40)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return None
                if event.key == pygame.K_UP: selected_index = (selected_index - 1) % len(saved_games)
                elif event.key == pygame.K_DOWN: selected_index = (selected_index + 1) % len(saved_games)
                elif event.key == pygame.K_RETURN: return load_game(saved_games[selected_index]['filepath'])
        pygame.display.flip()
        clock.tick(FPS)

# --- LOOP PRINCIPAL DO JOGO ---
def game_loop(screen, clock, fonts, jogador_data: Jogador):
    pygame.display.set_caption("Crônicas do Abismo - Aventura")
    player_sprite = PlayerSprite(jogador_data, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    all_sprites = pygame.sprite.Group(player_sprite)
    if isinstance(jogador_data.equipamento.get("Arma"), Arma):
        all_sprites.add(WeaponSprite(player_sprite))
    
    show_save_msg_time = pygame.time.get_ticks() + 5000
    last_save_was_good = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h: player_sprite.personagem_data.receber_dano(1)
                if event.key == pygame.K_p:
                    last_save_was_good = save_game(player_sprite.personagem_data)
                    show_save_msg_time = pygame.time.get_ticks() + 3000
        
        all_sprites.update()
        screen.fill(BLACK)
        all_sprites.draw(screen)
        draw_hud(screen, fonts, player_sprite)

        if pygame.time.get_ticks() < show_save_msg_time:
            if last_save_was_good: draw_text(screen, "Jogo Salvo!", fonts["main"], YELLOW, SCREEN_WIDTH/2, SCREEN_HEIGHT - 30, center=True)
            else: draw_text(screen, "Pressione P para salvar", fonts["main"], GRAY, SCREEN_WIDTH/2, SCREEN_HEIGHT - 30, center=True)
        else:
            last_save_was_good = False

        pygame.display.flip()
        clock.tick(FPS)

# --- PONTO DE ENTRADA DO PROGRAMA COM TRATAMENTO DE ERROS ---
def main():
    screen, clock, fonts = initialize_game()
    while True:
        choice = main_menu(screen, clock, fonts)
        player_data = None
        if choice == "new_game":
            player_data = character_creation_screen(screen, clock, fonts)
            if player_data:
                player_data = weapon_selection_screen(screen, clock, fonts, player_data)
        elif choice == "load_game":
            player_data = load_game_screen(screen, clock, fonts)

        if player_data:
            game_loop(screen, clock, fonts, player_data)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("\n--- OCORREU UM ERRO INESPERADO ---")
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        print("------------------------------------")
        print("O programa será fechado em 15 segundos.")
        time.sleep(15) # Pausa o programa para você conseguir ler o erro.
    finally:
        pygame.quit()
        sys.exit()