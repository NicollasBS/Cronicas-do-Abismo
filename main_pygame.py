# main_pygame.py

import pygame
import sys
from rpg_model import Jogador
from db_manager import get_class_template
from save_manager import save_game, load_game, list_saved_games

# --- CONSTANTES E INICIALIZAÇÃO ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SPEED = 2
WHITE, BLACK, RED, GREEN, GRAY, YELLOW = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 150, 0), (100, 100, 100), (255, 255, 0)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Crônicas do Abismo")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
menu_font = pygame.font.Font(None, 50)
input_font = pygame.font.Font(None, 32)
list_font = pygame.font.Font(None, 28)

# --- CLASSES E FUNÇÕES DE INTERFACE ---

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
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += PLAYER_SPEED
        
        self.rect.x += dx
        self.rect.y += dy
        self.rect.clamp_ip(screen.get_rect())

def draw_text(text, font, color, surface, x, y, center=False):
    """Função corrigida para desenhar texto na tela."""
    textobj = font.render(text, 1, color)
    if center:
        textrect = textobj.get_rect(center=(x, y))
    else:
        textrect = textobj.get_rect(topleft=(x, y))
    surface.blit(textobj, textrect)

def draw_hud(surface, jogador_sprite: PlayerSprite):
    jogador_data = jogador_sprite.personagem_data
    nome_texto = font.render(f"{jogador_data.nome} ({jogador_data.classe_personagem} Nv. {jogador_data.nivel})", True, WHITE)
    surface.blit(nome_texto, (10, 10))
    pv_texto = font.render(f"PV: {jogador_data.pontos_vida_atuais} / {jogador_data.pontos_vida_maximos}", True, WHITE)
    surface.blit(pv_texto, (10, 50))
    pygame.draw.rect(surface, RED, (10, 90, 200, 25))
    vida_percentual = jogador_data.pontos_vida_atuais / jogador_data.pontos_vida_maximos if jogador_data.pontos_vida_maximos > 0 else 0
    pygame.draw.rect(surface, GREEN, (10, 90, 200 * vida_percentual, 25))

def character_creation_screen():
    """Função completa e corrigida para criar o personagem."""
    fields = ["Nome do Personagem", "Classe (Ex: Guerreiro, Mago)"]
    user_inputs = ["", ""]
    current_field = 0
    while True:
        screen.fill(BLACK)
        draw_text('Criação de Personagem', font, WHITE, screen, SCREEN_WIDTH/2, 20, center=True)
        draw_text('Use as classes que estão no banco: Guerreiro, Mago.', input_font, GRAY, screen, SCREEN_WIDTH/2, 70, center=True)
        
        for i, field in enumerate(fields):
            prompt = f"{field}: {user_inputs[i]}" + ("_" if i == current_field else "")
            draw_text(prompt, input_font, WHITE, screen, 150, 150 + i * 50)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if user_inputs[current_field].strip() != "":
                        current_field += 1
                        if current_field >= len(fields):
                            nome_personagem = user_inputs[0]
                            classe_personagem_input = user_inputs[1]
                            class_data = get_class_template(classe_personagem_input)
                            if not class_data:
                                print(f"Classe '{classe_personagem_input}' não encontrada.")
                                current_field -= 1
                                user_inputs[current_field] = ""
                                continue
                            novo_jogador = Jogador(
                                id_entidade=1, nome=nome_personagem, raca=class_data["raca"],
                                classe_personagem=classe_personagem_input.capitalize(), nivel=1,
                                pontos_vida_maximos=class_data["pontos_vida_maximos"],
                                atributos=class_data["atributos"], proficiencias=class_data["proficiencias"],
                                experiencia=0, alinhamento="Neutro", nome_jogador="Jogador"
                            )
                            return novo_jogador
                elif event.key == pygame.K_BACKSPACE:
                    user_inputs[current_field] = user_inputs[current_field][:-1]
                else:
                    user_inputs[current_field] += event.unicode
        
        pygame.display.flip()
        clock.tick(FPS)

def main_menu():
    options = ["Novo Jogo", "Carregar Jogo", "Sair"]
    selected_option = 0
    while True:
        screen.fill(BLACK)
        draw_text("Crônicas do Abismo", menu_font, WHITE, screen, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, center=True)
        for i, option in enumerate(options):
            color = YELLOW if i == selected_option else WHITE
            draw_text(option, font, color, screen, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + i * 50, center=True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0: return "new_game"
                    elif selected_option == 1: return "load_game"
                    elif selected_option == 2: pygame.quit(); sys.exit()
        pygame.display.flip()
        clock.tick(FPS)

def load_game_screen():
    saved_games = list_saved_games()
    if not saved_games:
        screen.fill(BLACK)
        draw_text("Nenhum jogo salvo encontrado.", font, WHITE, screen, SCREEN_WIDTH/2, SCREEN_HEIGHT/2, center=True)
        draw_text("Pressione qualquer tecla para voltar.", input_font, GRAY, screen, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40, center=True)
        pygame.display.flip()
        pygame.time.wait(500)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN: waiting = False
        return None

    selected_index = 0
    while True:
        screen.fill(BLACK)
        draw_text("Selecione um Jogo para Carregar", font, WHITE, screen, SCREEN_WIDTH/2, 50, center=True)
        draw_text("Pressione ESC para voltar", input_font, GRAY, screen, SCREEN_WIDTH/2, 90, center=True)
        for i, game_data in enumerate(saved_games):
            color = YELLOW if i == selected_index else WHITE
            info_text = f"{game_data['char_name']} - Nível {game_data['level']} {game_data['class']}"
            draw_text(info_text, list_font, color, screen, 100, 150 + i * 40)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return None
                if event.key == pygame.K_UP: selected_index = (selected_index - 1) % len(saved_games)
                elif event.key == pygame.K_DOWN: selected_index = (selected_index + 1) % len(saved_games)
                elif event.key == pygame.K_RETURN:
                    selected_filepath = saved_games[selected_index]['filepath']
                    return load_game(selected_filepath)
        pygame.display.flip()
        clock.tick(FPS)

def game_loop(jogador_data: Jogador):
    pygame.display.set_caption("Crônicas do Abismo - Aventura")
    player_sprite = PlayerSprite(jogador_data, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    all_sprites = pygame.sprite.Group(player_sprite)
    show_save_msg_time = pygame.time.get_ticks() + 5000
    last_save_was_good = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    player_sprite.personagem_data.receber_dano(1)
                if event.key == pygame.K_p:
                    last_save_was_good = save_game(player_sprite.personagem_data)
                    show_save_msg_time = pygame.time.get_ticks() + 3000
        
        all_sprites.update()
        screen.fill(BLACK)
        all_sprites.draw(screen)
        draw_hud(screen, player_sprite)

        if pygame.time.get_ticks() < show_save_msg_time:
            if last_save_was_good:
                draw_text("Jogo Salvo!", font, YELLOW, screen, SCREEN_WIDTH/2, SCREEN_HEIGHT - 30, center=True)
            else:
                draw_text("Pressione P para salvar", font, GRAY, screen, SCREEN_WIDTH/2, SCREEN_HEIGHT - 30, center=True)
        else:
            last_save_was_good = False

        pygame.display.flip()
        clock.tick(FPS)

# --- PONTO DE ENTRADA DO PROGRAMA ---
if __name__ == '__main__':
    while True:
        choice = main_menu()
        if choice == "new_game":
            player_data = character_creation_screen()
            if player_data:
                game_loop(player_data)
        elif choice == "load_game":
            player_data = load_game_screen()
            if player_data:
                game_loop(player_data)