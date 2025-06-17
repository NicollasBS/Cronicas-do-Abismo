# -*- coding: utf-8 -*-
"""Implementação das classes base para o sistema de RPG D&D."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

# --- Classes Base e Entidades ---

class Entidade(ABC):
    """Classe base abstrata para todas as entidades nomeadas no jogo."""
    def __init__(self, id_entidade: int, nome: str):
        # Nome completo dos integrantes (Exemplo)
        # Diógenes Cogo Furlan - RA XXXXXX
        # [Seu Nome Completo] - RA YYYYYY
        self.id = id_entidade
        self.nome = nome

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.nome} (ID: {self.id})"

class Item(Entidade):
    """Classe base para todos os itens que podem ser coletados ou usados."""
    def __init__(self, id_entidade: int, nome: str, descricao: str, peso: float, valor_moedas: int):
        super().__init__(id_entidade, nome)
        self.descricao = descricao
        self.peso = peso
        self.valor_moedas = valor_moedas

    @abstractmethod
    def ser_usado(self, usuario: 'Personagem'):
        """Método abstrato para definir como o item é usado."""
        pass

class Magia(Entidade):
    """Representa os feitiços que personagens conjuradores podem usar."""
    def __init__(self, id_entidade: int, nome: str, nivel_magia: int, escola_magia: str,
                 tempo_conjuracao: str, alcance_magia: str, componentes: List[str],
                 duracao_magia: str, descricao_efeito: str, requer_concentracao: bool):
        super().__init__(id_entidade, nome)
        self.nivel_magia = nivel_magia
        self.escola_magia = escola_magia
        self.tempo_conjuracao = tempo_conjuracao
        self.alcance_magia = alcance_magia
        self.componentes = componentes
        self.duracao_magia = duracao_magia
        self.descricao_efeito = descricao_efeito
        self.requer_concentracao = requer_concentracao

    def conjurar(self, conjurador: 'Personagem', alvo: Optional['Personagem'] = None):
        """Protótipo para a ação de conjurar a magia."""
        print(f"{conjurador.nome} conjura {self.nome}!")
        # Lógica da magia será implementada no 2º bimestre
        pass

# --- Classes de Itens Específicos ---

class Arma(Item):
    """Representa itens usados para atacar."""
    def __init__(self, id_entidade: int, nome: str, descricao: str, peso: float, valor_moedas: int,
                 tipo_dano: str, dado_dano: str, propriedades: List[str], alcance: str):
        super().__init__(id_entidade, nome, descricao, peso, valor_moedas)
        self.tipo_dano = tipo_dano
        self.dado_dano = dado_dano
        self.propriedades = propriedades
        self.alcance = alcance

    def ser_usado(self, usuario: 'Personagem'):
        """Equipa a arma no personagem."""
        print(f"{usuario.nome} equipa {self.nome}.")
        usuario.equipamento['Arma'] = self

    def calcular_dano_rolagem(self):
        """Protótipo para calcular o dano baseado no dado_dano."""
        print(f"{self.nome} causa dano ({self.dado_dano} {self.tipo_dano}).")
        pass

class Armadura(Item):
    """Representa itens usados para defesa (aumentar CA e, opcionalmente, PV)."""
    def __init__(self, id_entidade: int, nome: str, descricao: str, peso: float, valor_moedas: int,
                 tipo_armadura: str, bonus_ca_base: int, requer_destreza_bonus: bool,
                 max_bonus_destreza: Optional[int], penalidade_furtividade: bool, requisito_forca: int,
                 bonus_pv: int = 0): # NOVO ATRIBUTO
        super().__init__(id_entidade, nome, descricao, peso, valor_moedas)
        self.tipo_armadura = tipo_armadura
        self.bonus_ca_base = bonus_ca_base
        self.requer_destreza_bonus = requer_destreza_bonus
        self.max_bonus_destreza = max_bonus_destreza
        self.penalidade_furtividade = penalidade_furtividade
        self.requisito_forca = requisito_forca
        self.bonus_pv = bonus_pv # NOVO ATRIBUTO

    def ser_usado(self, usuario: 'Personagem'):
        """Equipa a armadura e aplica seus bônus."""
        print(f"{usuario.nome} equipa {self.nome}.")
        
        # Lógica para desequipar a armadura antiga e remover seus bônus
        armadura_antiga = usuario.equipamento.get('Armadura')
        if isinstance(armadura_antiga, Armadura):
            usuario.pontos_vida_maximos -= armadura_antiga.bonus_pv
        
        usuario.equipamento['Armadura'] = self
        
        # Aplica o bônus de vida da nova armadura
        usuario.pontos_vida_maximos += self.bonus_pv
        # Garante que a vida atual não ultrapasse a máxima
        usuario.pontos_vida_atuais = min(usuario.pontos_vida_atuais, usuario.pontos_vida_maximos)
        
        usuario.calcular_classe_armadura()

class Pocao(Item):
    """Representa itens consumíveis com efeitos mágicos ou de cura."""
    def __init__(self, id_entidade: int, nome: str, descricao: str, peso: float, valor_moedas: int,
                 efeito: str, duracao_efeito: str, quantidade_cura: Optional[int] = None):
        super().__init__(id_entidade, nome, descricao, peso, valor_moedas)
        self.efeito = efeito
        self.duracao_efeito = duracao_efeito
        self.quantidade_cura = quantidade_cura

    def ser_usado(self, usuario: 'Personagem'):
        """Aplica o efeito da poção no usuário."""
        print(f"{usuario.nome} usa {self.nome}.")
        self.aplicar_efeito(usuario)
        if self in usuario.inventario:
            usuario.inventario.remove(self)

    def aplicar_efeito(self, alvo: 'Personagem'):
        """Protótipo para aplicar o efeito da poção."""
        print(f"Aplicando efeito: {self.efeito} em {alvo.nome}.")
        if self.quantidade_cura:
            alvo.receber_cura(self.quantidade_cura)
        pass

# --- Classes de Personagens ---

class Personagem(Entidade):
    """Classe base para qualquer criatura no jogo (Jogador ou NPC)."""
    def __init__(self, id_entidade: int, nome: str, raca: str, classe_personagem: str, nivel: int,
                 pontos_vida_maximos: int, atributos: Dict[str, int], proficiencias: List[str]):
        super().__init__(id_entidade, nome)
        self.raca = raca
        self.classe_personagem = classe_personagem
        self.nivel = nivel
        self.pontos_vida_maximos = pontos_vida_maximos
        self.pontos_vida_atuais = pontos_vida_maximos
        self.atributos = atributos
        self.inventario: List[Item] = []
        self.classe_armadura = 10
        self.proficiencias = proficiencias
        self.equipamento: Dict[str, Optional[Item]] = {"Arma": None, "Armadura": None, "Escudo": None}
        self.calcular_classe_armadura()

    def calcular_modificador_atributo(self, atributo: str) -> int:
        """Calcula o modificador de um atributo (ex: Força 12 -> +1)."""
        if atributo in self.atributos:
            return (self.atributos[atributo] - 10) // 2
        return 0

    def calcular_classe_armadura(self):
        """Calcula a Classe de Armadura baseada em equipamento e atributos."""
        ca_base = 10
        bonus_destreza = self.calcular_modificador_atributo("Destreza")
        armadura_equipada = self.equipamento.get('Armadura')
        escudo_equipado = self.equipamento.get('Escudo')

        if isinstance(armadura_equipada, Armadura):
            ca_base = armadura_equipada.bonus_ca_base
            if armadura_equipada.requer_destreza_bonus:
                if armadura_equipada.max_bonus_destreza is not None:
                    bonus_destreza = min(bonus_destreza, armadura_equipada.max_bonus_destreza)
            else:
                bonus_destreza = 0

        self.classe_armadura = ca_base + bonus_destreza

        if isinstance(escudo_equipado, Armadura) and escudo_equipado.tipo_armadura == "Escudo":
             self.classe_armadura += escudo_equipado.bonus_ca_base

        print(f"CA de {self.nome} recalculada para {self.classe_armadura}.")

    def atacar(self, alvo: 'Personagem'):
        """Protótipo para a ação de atacar um alvo."""
        print(f"{self.nome} ataca {alvo.nome}!")
        arma = self.equipamento.get('Arma')
        if isinstance(arma, Arma):
            arma.calcular_dano_rolagem()
        else:
            print(f"{self.nome} ataca desarmado.")
        pass

    def receber_dano(self, quantidade: int):
        """Reduz os pontos de vida atuais ao receber dano."""
        self.pontos_vida_atuais -= quantidade
        print(f"{self.nome} recebe {quantidade} de dano. Vida atual: {self.pontos_vida_atuais}/{self.pontos_vida_maximos}")
        if self.pontos_vida_atuais <= 0:
            self.morrer()

    def receber_cura(self, quantidade: int):
        """Aumenta os pontos de vida atuais ao receber cura, limitado ao máximo."""
        self.pontos_vida_atuais = min(self.pontos_vida_maximos, self.pontos_vida_atuais + quantidade)
        print(f"{self.nome} recupera {quantidade} pontos de vida. Vida atual: {self.pontos_vida_atuais}/{self.pontos_vida_maximos}")

    def usar_item(self, item: Item):
        """Tenta usar um item do inventário."""
        if item in self.inventario:
            item.ser_usado(self)
        else:
            print(f"{self.nome} não possui {item.nome} no inventário.")

    def adicionar_item_inventario(self, item: Item):
        """Adiciona um item ao inventário."""
        self.inventario.append(item)
        print(f"{item.nome} adicionado ao inventário de {self.nome}.")

    def remover_item_inventario(self, item: Item):
        """Remove um item do inventário."""
        if item in self.inventario:
            self.inventario.remove(item)
            print(f"{item.nome} removido do inventário de {self.nome}.")
            return True
        return False

    def morrer(self):
        """Define o que acontece quando os pontos de vida chegam a zero ou menos."""
        print(f"{self.nome} caiu inconsciente ou morreu!")
        self.pontos_vida_atuais = 0
        pass

    def __str__(self) -> str:
        return (f"{super().__str__()} - {self.raca} {self.classe_personagem} Nv {self.nivel} "
                f"PV: {self.pontos_vida_atuais}/{self.pontos_vida_maximos} CA: {self.classe_armadura}")

class Jogador(Personagem):
    """Representa os personagens controlados pelos usuários."""
    def __init__(self, id_entidade: int, nome: str, raca: str, classe_personagem: str, nivel: int,
                 pontos_vida_maximos: int, atributos: Dict[str, int], proficiencias: List[str],
                 experiencia: int, alinhamento: str, nome_jogador: str):
        super().__init__(id_entidade, nome, raca, classe_personagem, nivel, pontos_vida_maximos, atributos, proficiencias)
        self.experiencia = experiencia
        self.alinhamento = alinhamento
        self.nome_jogador = nome_jogador
        self.magias: List[Magia] = [] # NOVA LISTA PARA MAGIAS

    def aprender_magia(self, magia: Magia):
        """Adiciona uma magia à lista de magias conhecidas do jogador."""
        if magia not in self.magias:
            self.magias.append(magia)
            print(f"{self.nome} aprendeu a magia: {magia.nome}!")

    def ganhar_experiencia(self, quantidade: int):
        """Adiciona pontos de experiência ao jogador."""
        self.experiencia += quantidade
        print(f"{self.nome} ganha {quantidade} XP! Total: {self.experiencia}")
        self.verificar_subir_nivel()

    def verificar_subir_nivel(self):
        """Verifica se o jogador tem XP suficiente para subir de nível."""
        xp_necessario = {1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500} # ...etc
        proximo_nivel = self.nivel + 1
        if proximo_nivel in xp_necessario and self.experiencia >= xp_necessario[proximo_nivel]:
            self.subir_nivel()

    def subir_nivel(self):
        """Aumenta o nível do jogador e aplica as melhorias correspondentes."""
        self.nivel += 1
        print(f"{self.nome} subiu para o nível {self.nivel}!")
        pass

    def escolher_acao(self):
        """Protótipo para permitir que o jogador escolha sua ação (em combate ou fora)."""
        print(f"É a vez de {self.nome}. O que você faz? (Implementação futura)")
        pass

class NPC(Personagem):
    """Representa personagens controlados pelo Mestre (ou pelo sistema)."""
    def __init__(self, id_entidade: int, nome: str, raca: str, classe_personagem: str, nivel: int,
                 pontos_vida_maximos: int, atributos: Dict[str, int], proficiencias: List[str],
                 tipo: str, comportamento: str, dialogo: Optional[Any] = None):
        super().__init__(id_entidade, nome, raca, classe_personagem, nivel, pontos_vida_maximos, atributos, proficiencias)
        self.tipo = tipo 
        self.comportamento = comportamento
        self.dialogo = dialogo

    def interagir(self, jogador: Jogador):
        """Protótipo para a interação entre NPC e jogador."""
        print(f"{jogador.nome} interage com {self.nome}.")
        if self.dialogo:
            print(f"{self.nome} diz: {self.dialogo}")
        pass

    def determinar_acao_combate(self):
        """Protótipo para a IA básica do NPC em combate."""
        print(f"{self.nome} está decidindo sua ação... (Implementação futura)")
        pass

if __name__ == '__main__':
    guerreiro = Jogador(
        id_entidade=1, nome="Thorin", raca="Anão da Montanha", classe_personagem="Guerreiro", nivel=1,
        pontos_vida_maximos=12, atributos={"Força": 15, "Destreza": 10, "Constituição": 14, "Inteligência": 8, "Sabedoria": 12, "Carisma": 9},
        proficiencias=["Armaduras Pesadas", "Escudos", "Machados"], experiencia=0, alinhamento="Leal e Bom", nome_jogador="Jogador1"
    )

    goblin = NPC(
        id_entidade=101, nome="Snaga", raca="Goblin", classe_personagem="Ladino", nivel=1,
        pontos_vida_maximos=7, atributos={"Força": 8, "Destreza": 14, "Constituição": 10, "Inteligência": 10, "Sabedoria": 8, "Carisma": 8},
        proficiencias=["Furtividade", "Adagas"], tipo="Monstro", comportamento="Agressivo"
    )

    machado_anao = Arma(
        id_entidade=201, nome="Machado de Guerra Anão", descricao="Um machado robusto.", peso=2.0, valor_moedas=15,
        tipo_dano="Cortante", dado_dano="1d8", propriedades=["Versátil (1d10)"], alcance="Corpo a corpo"
    )

    cota_de_malha = Armadura(
        id_entidade=301, nome="Cota de Malha", descricao="Armadura feita de anéis interligados.", peso=20.0, valor_moedas=50,
        tipo_armadura="Pesada", bonus_ca_base=16, requer_destreza_bonus=False, max_bonus_destreza=None,
        penalidade_furtividade=True, requisito_forca=13
    )

    pocao_cura = Pocao(
        id_entidade=401, nome="Poção de Cura Menor", descricao="Recupera alguns pontos de vida.", peso=0.5, valor_moedas=50,
        efeito="Cura", duracao_efeito="Instantâneo", quantidade_cura=7 # Exemplo 2d4+2, média 7
    )

    guerreiro.adicionar_item_inventario(machado_anao)
    guerreiro.adicionar_item_inventario(cota_de_malha)
    guerreiro.adicionar_item_inventario(pocao_cura)

    guerreiro.usar_item(machado_anao)
    guerreiro.usar_item(cota_de_malha)

    print("--- Informações Iniciais ---")
    print(guerreiro)
    print(goblin)
    print("Inventário do Guerreiro:", [item.nome for item in guerreiro.inventario])
    print("Equipamento do Guerreiro:", {k: v.nome if v else None for k, v in guerreiro.equipamento.items()})

    print("\n--- Simulação Básica ---")
    guerreiro.atacar(goblin)
    goblin.receber_dano(5)
