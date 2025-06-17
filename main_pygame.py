import pygame
import sys
# Linha Corrigida
from rpg_model import Jogador, NPC, Arma
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SPEED = 5

# CORES
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# inicializa o Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RPG Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Classe Sprite do Jogador
class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, personagem_jogador: Jogador, pos_x, pos_y):
        super().__init__()
        self.jogador = personagem_jogador
        self.image = pygame.Surface((50, 50))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(pos_x, pos_y))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.rect.y += PLAYER_SPEED

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        
# Função para desenhar a interface do jogo
def draw_hud(surface, jogador_sprite: PlayerSprite):
   jogador_data = jogador_sprite.jogador_data

   nome_texto = font.render(f"Nome: {jogador_data.nome} ({jogador_data.classe_personagem} Nv. {jogador_data.nivel})", True, WHITE)
   surface.blit(nome_texto, (10, 10))

   pv_texto = font.render(f"PV: {jogador_data.pontos_vida_atuais} / {jogador_data.pontos_vida_maximos}", True, WHITE)
   surface.blit(pv_texto, (10, 50))

   pygame.draw.rect(surface, RED, (10, 90, 200, 25))
   vida_percentual = jogador_data.pontos_vida_atuais / jogador_data.pontos_vida_maximos
   pygame.draw.rect(surface, GREEN, (10, 90, 200 * vida_percentual, 25))

def game_loop():
    """Loop principal que executa o jogo."""

    # 1. CRIAR INSTÂNCIAS DOS SEUS OBJETOS
    # Aqui, criamos um personagem usando sua classe Jogador
    guerreiro_data = Jogador(
        id_entidade=1, nome="Durin", raca="Anão", classe_personagem="Guerreiro", nivel=1,
        pontos_vida_maximos=12, pontos_vida_atuais=12,
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
   

