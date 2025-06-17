# main_pygame.py

import pygame
import sys
import time
import json
from rpg_model import Jogador, Arma, Armadura, Magia
from db_manager import get_class_template, get_all_armors, get_all_spells, get_all_weapons

# --- CONSTANTES E INICIALIZAÇÃO ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 2
WHITE, BLACK, RED, GREEN, GRAY, YELLOW = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 150, 0), (100, 100, 100), (255, 255, 0)

def initialize_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Crônicas do Abismo")
    clock = pygame.time.Clock()
    fonts = {
        "main": pygame.font.Font(None, 36), "menu": pygame.font.Font(None, 50),
        "input": pygame.font.Font(None, 32), "list": pygame.font.Font(None, 28)
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
    
    if jogador_data.classe_personagem.lower() == 'mago' and jogador_data.magias:
        magia_nome = jogador_data.magias[0].nome
        draw_text(surface, f"Magia: {magia_nome}", fonts["list"], YELLOW, 10, 90)
    
    arma_equipada = jogador_data.equipamento.get("Arma")
    if arma_equipada:
        draw_text(surface, f"Arma: {arma_equipada.nome}", fonts["list"], YELLOW, 10, 120)


# --- TELAS DO JOGO ---

def main_menu(screen, clock, fonts):
    # (Função sem alterações)
    options = ["Novo Jogo", "Sair"]
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
                    elif selected_option == 1: pygame.quit(); sys.exit()
        pygame.display.flip()
        clock.tick(FPS)


def character_creation_screen(screen, clock, fonts):
    # (Função sem alterações)
    fields = ["Nome do Personagem", "Classe (Guerreiro/Mago)"]
    user_inputs = ["", ""]
    current_field = 0
    while True:
        screen.fill(BLACK)
        draw_text(screen, 'Criação de Personagem', fonts["main"], WHITE, SCREEN_WIDTH/2, 20, center=True)
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
                            template = get_class_template(classe_personagem_input)
                            if not template:
                                print(f"Classe '{classe_personagem_input}' não encontrada. Tente 'Guerreiro' ou 'Mago'.")
                                current_field -= 1; user_inputs[current_field] = ""; continue
                            novo_jogador = Jogador(
                                id_entidade=template["id"], nome=nome_personagem, raca=template["raca"],
                                classe_personagem=template["classe_personagem"], nivel=template["nivel"],
                                pontos_vida_maximos=template["pontos_vida_maximos"],
                                atributos=json.loads(template["atributos"]),
                                proficiencias=json.loads(template["proficiencias"]),
                                experiencia=0, alinhamento="Leal e Bom", nome_jogador="Jogador"
                            )
                            return novo_jogador
                elif event.key == pygame.K_BACKSPACE: user_inputs[current_field] = user_inputs[current_field][:-1]
                else: user_inputs[current_field] += event.unicode
        pygame.display.flip()
        clock.tick(FPS)

def weapon_selection_screen(screen, clock, fonts, player_data: Jogador):
    """NOVA TELA: Para escolher a arma inicial."""
    weapons = get_all_weapons()
    if not weapons: return player_data
    selected_index = 0
    while True:
        screen.fill(BLACK)
        draw_text(screen, "Escolha sua Arma Inicial", fonts["menu"], WHITE, SCREEN_WIDTH / 2, 50, center=True)
        for i, weapon in enumerate(weapons):
            color = YELLOW if i == selected_index else WHITE
            draw_text(screen, weapon.nome, fonts["list"], color, 100, 150 + i * 40)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return player_data
                if event.key == pygame.K_UP: selected_index = (selected_index - 1) % len(weapons)
                elif event.key == pygame.K_DOWN: selected_index = (selected_index + 1) % len(weapons)
                elif event.key == pygame.K_RETURN:
                    player_data.usar_item(weapons[selected_index])
                    return player_data
        pygame.display.flip()
        clock.tick(FPS)

def armor_selection_screen(screen, clock, fonts, player_data: Jogador):
    # (Função sem alterações)
    armors = get_all_armors()
    if not armors: return player_data
    selected_index = 0
    while True:
        screen.fill(BLACK)
        draw_text(screen, "Escolha sua Armadura", fonts["menu"], WHITE, SCREEN_WIDTH/2, 50, center=True)
        for i, armor in enumerate(armors):
            color = YELLOW if i == selected_index else WHITE
            info_text = f"{armor.nome} (CA: {armor.bonus_ca_base}, PV: +{armor.bonus_pv})"
            draw_text(screen, info_text, fonts["list"], color, 100, 150 + i * 40)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return player_data
                if event.key == pygame.K_UP: selected_index = (selected_index - 1) % len(armors)
                elif event.key == pygame.K_DOWN: selected_index = (selected_index + 1) % len(armors)
                elif event.key == pygame.K_RETURN:
                    player_data.usar_item(armors[selected_index])
                    return player_data
        pygame.display.flip()
        clock.tick(FPS)

def spell_selection_screen(screen, clock, fonts, player_data: Jogador):
    # (Função sem alterações)
    spells = get_all_spells()
    if not spells: return player_data
    selected_index = 0
    while True:
        screen.fill(BLACK)
        draw_text(screen, "Escolha sua Magia Inicial", fonts["menu"], WHITE, SCREEN_WIDTH/2, 50, center=True)
        for i, spell in enumerate(spells):
            color = YELLOW if i == selected_index else WHITE
            draw_text(screen, spell.nome, fonts["list"], color, 100, 150 + i * 40)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return player_data
                if event.key == pygame.K_UP: selected_index = (selected_index - 1) % len(spells)
                elif event.key == pygame.K_DOWN: selected_index = (selected_index + 1) % len(spells)
                elif event.key == pygame.K_RETURN:
                    player_data.aprender_magia(spells[selected_index])
                    return player_data
        pygame.display.flip()
        clock.tick(FPS)


def game_loop(screen, clock, fonts, jogador_data: Jogador):
    pygame.display.set_caption(f"Crônicas do Abismo - {jogador_data.nome}")
    player_sprite = PlayerSprite(jogador_data, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    all_sprites = pygame.sprite.Group(player_sprite)
    
    # Adiciona o sprite da arma se uma estiver equipada
    if isinstance(jogador_data.equipamento.get("Arma"), Arma):
        all_sprites.add(WeaponSprite(player_sprite))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): running = False
        
        all_sprites.update()
        screen.fill(BLACK)
        all_sprites.draw(screen)
        draw_hud(screen, fonts, player_sprite)
        pygame.display.flip()
        clock.tick(FPS)

# --- PONTO DE ENTRADA (FLUXO ATUALIZADO) ---
def main():
    screen, clock, fonts = initialize_game()
    while True:
        choice = main_menu(screen, clock, fonts)
        if choice == "new_game":
            player_data = character_creation_screen(screen, clock, fonts)
            if player_data:
                # ETAPA 1: Todos escolhem uma arma
                player_data = weapon_selection_screen(screen, clock, fonts, player_data)

                # ETAPA 2: Escolha específica da classe
                if player_data.classe_personagem.lower() == 'guerreiro':
                    player_data = armor_selection_screen(screen, clock, fonts, player_data)
                elif player_data.classe_personagem.lower() == 'mago':
                    player_data = spell_selection_screen(screen, clock, fonts, player_data)
                
                game_loop(screen, clock, fonts, player_data)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n--- OCORREU UM ERRO INESPERADO: {e} ---")
        import traceback
        traceback.print_exc()
        time.sleep(15)
    finally:
        pygame.quit()
        sys.exit()