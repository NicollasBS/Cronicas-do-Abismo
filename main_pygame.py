# main_pygame.py

import pygame
import sys
from rpg_model import Jogador, NPC, Arma  # Importando suas classes!

# --- CONSTANTES DE CONFIGURAÇÃO ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SPEED = 2

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 150, 0)

# --- INICIALIZAÇÃO DO PYGAME ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Meu RPG de D&D")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36) # Fonte para texto da UI

# --- CLASSES DE SPRITE (A Camada Visual) ---

class PlayerSprite(pygame.sprite.Sprite):
    """
    Esta classe representa a parte VISUAL do jogador.
    Ela contém a lógica de movimento e imagem, e se conecta
    ao objeto Jogador que contém os dados e regras do jogo.
    """
    def __init__(self, personagem_jogador: Jogador, pos_x, pos_y):
        super().__init__()
        
        # Link para o objeto de dados do jogador
        self.personagem_data = personagem_jogador
        
        # Atributos visuais (um quadrado verde por enquanto)
        self.image = pygame.Surface((40, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(pos_x, pos_y))

    def update(self):
        """Atualiza a posição do sprite com base nas teclas pressionadas."""
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += PLAYER_SPEED

        # Mantém o jogador dentro da tela
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

# --- FUNÇÃO PARA DESENHAR A INTERFACE (UI/HUD) ---

def draw_hud(surface, jogador_sprite: PlayerSprite):
    """Desenha informações do jogador na tela."""
    # Extrai os dados do objeto Jogador dentro do sprite
    jogador_data = jogador_sprite.personagem_data
    
    # Exibe Nome e Classe
    nome_texto = font.render(f"{jogador_data.nome} ({jogador_data.classe_personagem} Nv. {jogador_data.nivel})", True, WHITE)
    surface.blit(nome_texto, (10, 10))
    
    # Exibe Pontos de Vida
    pv_texto = font.render(f"PV: {jogador_data.pontos_vida_atuais} / {jogador_data.pontos_vida_maximos}", True, WHITE)
    surface.blit(pv_texto, (10, 50))
    
    # Barra de Vida
    pygame.draw.rect(surface, RED, (10, 90, 200, 25))
    vida_percentual = jogador_data.pontos_vida_atuais / jogador_data.pontos_vida_maximos
    pygame.draw.rect(surface, GREEN, (10, 90, 200 * vida_percentual, 25))

# --- FUNÇÃO PRINCIPAL DO JOGO ---

def game_loop():
    """Loop principal que executa o jogo."""

    # 1. CRIAR INSTÂNCIAS DOS SEUS OBJETOS
    # Aqui, criamos um personagem usando sua classe Jogador
    guerreiro_data = Jogador(
        id_entidade=1, nome="Durin", raca="Anão", classe_personagem="Guerreiro", nivel=1,
        pontos_vida_maximos=12,
        atributos={"Força": 16, "Destreza": 10, "Constituição": 14},
        proficiencias=["Escudos", "Machados"], experiencia=0, alinhamento="Leal e Bom", nome_jogador="Jogador1"
    )

    # 2. CRIAR OS SPRITES PARA REPRESENTÁ-LOS
    # Criamos um sprite visual e passamos o objeto de dados para ele
    player_sprite = PlayerSprite(guerreiro_data, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    # Grupo de Sprites: uma forma fácil de atualizar e desenhar todos os sprites de uma vez
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player_sprite)

    running = True
    while running:
        # --- PROCESSAMENTO DE EVENTOS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Exemplo de interação: simular dano ao apertar 'H'
                if event.key == pygame.K_h:
                    player_sprite.personagem_data.receber_dano(1)
                    print("Guerreiro recebeu 1 de dano!")
        
        # --- ATUALIZAÇÃO DA LÓGICA ---
        all_sprites.update() # Isso chama o método update() de todos os sprites no grupo

        # --- DESENHO NA TELA ---
        screen.fill(BLACK) # Limpa a tela com a cor preta

        all_sprites.draw(screen) # Desenha todos os sprites no grupo
        
        draw_hud(screen, player_sprite) # Desenha a interface do usuário

        # --- ATUALIZAÇÃO DA TELA ---
        pygame.display.flip()

        # Controla a velocidade do jogo
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


# --- PONTO DE ENTRADA DO PROGRAMA ---
if __name__ == '__main__':
    game_loop()