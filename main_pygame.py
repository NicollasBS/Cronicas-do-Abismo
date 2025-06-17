# main_pygame.py

import pygame
import sys
import time
import json
import math
from rpg_model import Jogador, Arma, Armadura, Magia, NPC
from db_manager import get_random_enemy, get_class_template, get_all_armors, get_all_spells, get_all_weapons

# --- CONSTANTES E INICIALIZAÇÃO ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 2
PROJECTILE_SPEED = 7
MELEE_RANGE = 50 
WHITE, BLACK, RED, GREEN, GRAY, YELLOW, BLUE = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 150, 0), (100, 100, 100), (255, 255, 0), (0, 100, 255)

# NOVO: Constantes para a regeneração de mana
MANA_REGEN_INTERVAL = 10000 # 10000 milissegundos = 10 segundos
MANA_REGEN_AMOUNT = 5     # Quantidade de mana a regenerar

def initialize_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Crônicas do Abismo")
    clock = pygame.time.Clock()
    fonts = {
        "main": pygame.font.Font(None, 36), "menu": pygame.font.Font(None, 50),
        "input": pygame.font.Font(None, 32), "list": pygame.font.Font(None, 24)
    }
    return screen, clock, fonts

# --- CLASSES DE SPRITE (sem alterações) ---
class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, personagem_jogador: Jogador, pos_x, pos_y):
        super().__init__(); self.personagem_data = personagem_jogador; self.image = pygame.Surface((40, 40)); self.image.fill(GREEN); self.rect = self.image.get_rect(center=(pos_x, pos_y))
    def update(self):
        keys = pygame.key.get_pressed(); dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += PLAYER_SPEED
        self.rect.move_ip(dx, dy); self.rect.clamp_ip(pygame.display.get_surface().get_rect())

class EnemySprite(pygame.sprite.Sprite):
    def __init__(self, personagem_npc: NPC, pos_x, pos_y):
        super().__init__(); self.personagem_data = personagem_npc; self.image = pygame.Surface((40, 40)); self.image.fill((180, 50, 50)); self.rect = self.image.get_rect(center=(pos_x, pos_y))

class WeaponSprite(pygame.sprite.Sprite):
    def __init__(self, player_sprite: PlayerSprite):
        super().__init__(); self.player_sprite = player_sprite; self.image = pygame.Surface((20, 20)); self.image.fill(RED); self.rect = self.image.get_rect(center=self.player_sprite.rect.center); self.offset_x = 30
    def update(self):
        self.rect.centery = self.player_sprite.rect.centery; self.rect.centerx = self.player_sprite.rect.centerx + self.offset_x

class ProjectileSprite(pygame.sprite.Sprite):
    def __init__(self, start_pos, direction_vector, damage, color=YELLOW, max_range=400):
        super().__init__(); self.image = pygame.Surface((10, 10)); self.image.fill(color); self.rect = self.image.get_rect(center=start_pos)
        self.start_pos = pygame.math.Vector2(start_pos); self.direction = direction_vector.normalize() if direction_vector.length() > 0 else pygame.math.Vector2(0)
        self.speed = PROJECTILE_SPEED; self.damage = damage; self.max_range = max_range
    def update(self):
        self.rect.move_ip(self.direction.x * self.speed, self.direction.y * self.speed)
        if not pygame.display.get_surface().get_rect().colliderect(self.rect) or self.start_pos.distance_to(self.rect.center) > self.max_range:
            self.kill()

# --- FUNÇÕES DE INTERFACE (sem alterações) ---
def draw_text(surface, text, font, color, x, y, center=False, topright=False):
    textobj = font.render(text, 1, color)
    if topright: textrect = textobj.get_rect(topright=(x, y))
    elif center: textrect = textobj.get_rect(center=(x, y))
    else: textrect = textobj.get_rect(topleft=(x, y))
    surface.blit(textobj, textrect)

def draw_hud(surface, fonts, jogador_sprite: PlayerSprite):
    jogador_data = jogador_sprite.personagem_data
    draw_text(surface, f"PV: {jogador_data.pontos_vida_atuais} / {jogador_data.pontos_vida_maximos}", fonts["list"], WHITE, 10, 10)
    pygame.draw.rect(surface, (100,0,0), (10, 35, 200, 20))
    vida_percentual = jogador_data.pontos_vida_atuais / jogador_data.pontos_vida_maximos if jogador_data.pontos_vida_maximos > 0 else 0
    pygame.draw.rect(surface, GREEN, (10, 35, 200 * vida_percentual, 20))
    if jogador_data.pontos_mana_maximos > 0:
        draw_text(surface, f"PM: {jogador_data.pontos_mana_atuais} / {jogador_data.pontos_mana_maximos}", fonts["list"], WHITE, 10, 60)
        pygame.draw.rect(surface, (0,0,100), (10, 85, 150, 20))
        mana_percentual = jogador_data.pontos_mana_atuais / jogador_data.pontos_mana_maximos if jogador_data.pontos_mana_maximos > 0 else 0
        pygame.draw.rect(surface, BLUE, (10, 85, 150 * mana_percentual, 20))

def draw_enemy_hud(surface, fonts, enemy_sprite: EnemySprite):
    if not enemy_sprite or not enemy_sprite.alive(): return
    enemy_data = enemy_sprite.personagem_data
    draw_text(surface, enemy_data.nome, fonts["list"], WHITE, SCREEN_WIDTH - 10, 10, topright=True)
    draw_text(surface, f"PV: {enemy_data.pontos_vida_atuais} / {enemy_data.pontos_vida_maximos}", fonts["list"], WHITE, SCREEN_WIDTH - 10, 35, topright=True)

# --- TELAS DO JOGO (sem alterações) ---
def main_menu(screen, clock, fonts):
    options = ["Novo Jogo", "Sair"]; selected_option = 0
    while True:
        screen.fill(BLACK); draw_text(screen, "Crônicas do Abismo", fonts["menu"], WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, center=True)
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
        pygame.display.flip(); clock.tick(FPS)

def character_creation_screen(screen, clock, fonts):
    fields = ["Nome do Personagem", "Classe (Guerreiro/Mago)"]; user_inputs = ["", ""]; current_field = 0
    while True:
        screen.fill(BLACK); draw_text(screen, 'Criação de Personagem', fonts["main"], WHITE, SCREEN_WIDTH/2, 20, center=True)
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
                                print(f"Classe '{classe_personagem_input}' não encontrada."); current_field -= 1; user_inputs[current_field] = ""; continue
                            novo_jogador = Jogador(
                                id_entidade=template["id"], nome=nome_personagem, raca=template["raca"],
                                classe_personagem=template["classe_personagem"], nivel=template["nivel"],
                                pontos_vida_maximos=template["pontos_vida_maximos"],
                                pontos_mana_maximos=template["pontos_mana_maximos"],
                                atributos=json.loads(template["atributos"]), proficiencias=json.loads(template["proficiencias"]),
                                experiencia=template.get("experiencia", 0), alinhamento=template.get("alinhamento", "Neutro"),
                                nome_jogador=template.get("nome_jogador", "Jogador")
                            )
                            return novo_jogador
                elif event.key == pygame.K_BACKSPACE: user_inputs[current_field] = user_inputs[current_field][:-1]
                else: user_inputs[current_field] += event.unicode
        pygame.display.flip(); clock.tick(FPS)

def selection_screen(screen, clock, fonts, player_data, title, items, item_type):
    if not items: return player_data
    selected_index = 0
    while True:
        screen.fill(BLACK); draw_text(screen, title, fonts["menu"], WHITE, SCREEN_WIDTH / 2, 50, center=True)
        for i, item in enumerate(items):
            color = YELLOW if i == selected_index else WHITE
            info_text = f"{item.nome} (CA: {item.bonus_ca_base}, PV: +{item.bonus_pv})" if item_type == "armor" else item.nome
            draw_text(screen, info_text, fonts["list"], color, 100, 150 + i * 40)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return player_data
                if event.key == pygame.K_UP: selected_index = (selected_index - 1) % len(items)
                elif event.key == pygame.K_DOWN: selected_index = (selected_index + 1) % len(items)
                elif event.key == pygame.K_RETURN:
                    chosen_item = items[selected_index]
                    if item_type in ["weapon", "armor"]: player_data.usar_item(chosen_item)
                    elif item_type == "spell": player_data.aprender_magia(chosen_item)
                    return player_data
        pygame.display.flip(); clock.tick(FPS)

# --- LOOP PRINCIPAL DO JOGO (COM A LÓGICA DE REGENERAÇÃO) ---
def game_loop(screen, clock, fonts, jogador_data: Jogador):
    pygame.display.set_caption(f"Crônicas do Abismo - {jogador_data.nome}")
    
    all_sprites = pygame.sprite.Group()
    player_sprite = PlayerSprite(jogador_data, SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2)
    all_sprites.add(player_sprite)
    
    enemy_group = pygame.sprite.Group()
    enemy_data = get_random_enemy()
    if enemy_data:
        enemy_sprite = EnemySprite(enemy_data, SCREEN_WIDTH * 3 / 4, SCREEN_HEIGHT / 2)
        all_sprites.add(enemy_sprite)
        enemy_group.add(enemy_sprite)
    else:
        enemy_sprite = None
        
    projectiles = pygame.sprite.Group()
    if isinstance(jogador_data.equipamento.get("Arma"), Arma):
        all_sprites.add(WeaponSprite(player_sprite))

    combat_message = ""
    message_time = 0
    
    # NOVO: Variável para controlar o tempo da regeneração de mana
    last_mana_regen_time = pygame.time.get_ticks()
    
    running = True
    while running:
        # --- LÓGICA DE REGENERAÇÃO DE MANA ---
        current_time = pygame.time.get_ticks()
        if current_time - last_mana_regen_time > MANA_REGEN_INTERVAL:
            if jogador_data.pontos_mana_atuais < jogador_data.pontos_mana_maximos:
                # Regenera a mana
                jogador_data.pontos_mana_atuais += MANA_REGEN_AMOUNT
                # Garante que não ultrapasse o máximo
                jogador_data.pontos_mana_atuais = min(jogador_data.pontos_mana_atuais, jogador_data.pontos_mana_maximos)
                print(f"{jogador_data.nome} regenerou {MANA_REGEN_AMOUNT} de mana.")
            # Reinicia o contador de tempo
            last_mana_regen_time = current_time

        # --- PROCESSAMENTO DE EVENTOS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: # Lógica de ataque
                    if not enemy_sprite or not enemy_sprite.alive(): continue
                    arma = jogador_data.equipamento.get("Arma")
                    if not arma or "Distância" not in arma.alcance:
                        if pygame.math.Vector2(player_sprite.rect.center).distance_to(enemy_sprite.rect.center) <= MELEE_RANGE:
                            combat_message = jogador_data.atacar(enemy_sprite.personagem_data); message_time = pygame.time.get_ticks() + 2000
                        else: combat_message = "Inimigo fora de alcance!"; message_time = pygame.time.get_ticks() + 2000
                    else:
                        direcao = pygame.math.Vector2(enemy_sprite.rect.center) - pygame.math.Vector2(player_sprite.rect.center)
                        flecha = ProjectileSprite(player_sprite.rect.center, direcao, arma.calcular_dano_rolagem(), color=WHITE)
                        projectiles.add(flecha); all_sprites.add(flecha)
                        combat_message = f"{jogador_data.nome} atirou uma flecha!"; message_time = pygame.time.get_ticks() + 2000
                
                if event.key == pygame.K_e: # Lógica de magia
                    if jogador_data.classe_personagem.lower() == 'mago' and jogador_data.magias:
                        magia = jogador_data.magias[0]
                        if jogador_data.pode_conjurar(magia):
                            jogador_data.gastar_mana(magia.custo_mana)
                            directions = [pygame.math.Vector2(0,-1), pygame.math.Vector2(0,1), pygame.math.Vector2(-1,0), pygame.math.Vector2(1,0)]
                            for direcao in directions:
                                proj_magico = ProjectileSprite(player_sprite.rect.center, direcao, damage=5, color=BLUE)
                                projectiles.add(proj_magico); all_sprites.add(proj_magico)
                            combat_message = f"{jogador_data.nome} conjurou {magia.nome}!"; message_time = pygame.time.get_ticks() + 2000
                        else:
                            combat_message = "Mana insuficiente!"; message_time = pygame.time.get_ticks() + 2000
        
        # --- LÓGICA DE COLISÃO ---
        hits = pygame.sprite.groupcollide(projectiles, enemy_group, True, False)
        for projectile, enemies_hit in hits.items():
            for enemy in enemies_hit:
                enemy.personagem_data.receber_dano(projectile.damage)
                combat_message = f"Inimigo atingido por {projectile.damage} de dano!"
                message_time = pygame.time.get_ticks() + 2000
                if enemy.personagem_data.pontos_vida_atuais <= 0: enemy.kill()
        
        # --- ATUALIZAÇÃO E DESENHO ---
        all_sprites.update()
        screen.fill(BLACK)
        all_sprites.draw(screen)
        draw_hud(screen, fonts, player_sprite)
        draw_enemy_hud(screen, fonts, enemy_sprite)

        if pygame.time.get_ticks() < message_time:
            draw_text(screen, combat_message, fonts["list"], YELLOW, SCREEN_WIDTH/2, SCREEN_HEIGHT - 40, center=True)

        pygame.display.flip()
        clock.tick(FPS)

# --- PONTO DE ENTRADA ---
def main():
    screen, clock, fonts = initialize_game()
    while True:
        choice = main_menu(screen, clock, fonts)
        if choice == "new_game":
            player_data = character_creation_screen(screen, clock, fonts)
            if player_data:
                player_data = selection_screen(screen, clock, fonts, player_data, "Escolha sua Arma Inicial", get_all_weapons(), "weapon")
                if player_data.classe_personagem.lower() == 'guerreiro':
                    player_data = selection_screen(screen, clock, fonts, player_data, "Escolha sua Armadura", get_all_armors(), "armor")
                elif player_data.classe_personagem.lower() == 'mago':
                    player_data = selection_screen(screen, clock, fonts, player_data, "Escolha sua Magia Inicial", get_all_spells(), "spell")
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