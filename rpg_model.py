# rpg_model.py

import random
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

class Entidade(ABC):
    def __init__(self, id_entidade: int, nome: str):
        self.id = id_entidade; self.nome = nome

class Magia(Entidade):
    def __init__(self, id_entidade: int, nome: str, nivel_magia: int, escola_magia: str,
                 tempo_conjuracao: str, alcance_magia: str, componentes: List[str],
                 duracao_magia: str, descricao_efeito: str, requer_concentracao: bool,
                 custo_mana: int = 10):
        super().__init__(id_entidade, nome)
        self.nivel_magia = nivel_magia; self.escola_magia = escola_magia
        self.tempo_conjuracao = tempo_conjuracao; self.alcance_magia = alcance_magia
        self.componentes = componentes; self.duracao_magia = duracao_magia
        self.descricao_efeito = descricao_efeito; self.requer_concentracao = requer_concentracao
        self.custo_mana = custo_mana

class Item(Entidade):
    def __init__(self, id_entidade: int, nome: str, descricao: str, peso: float, valor_moedas: int):
        super().__init__(id_entidade, nome)
        self.descricao = descricao; self.peso = peso; self.valor_moedas = valor_moedas
    @abstractmethod
    def ser_usado(self, usuario: 'Personagem'): pass

class Arma(Item):
    def __init__(self, id_entidade: int, nome: str, descricao: str, peso: float, valor_moedas: int,
                 tipo_dano: str, dado_dano: str, propriedades: List[str], alcance: str):
        super().__init__(id_entidade, nome, descricao, peso, valor_moedas)
        self.tipo_dano = tipo_dano; self.dado_dano = dado_dano
        self.propriedades = propriedades; self.alcance = alcance
    def ser_usado(self, usuario: 'Personagem'):
        usuario.equipamento['Arma'] = self
    def calcular_dano_rolagem(self) -> int:
        try:
            num_dados, tipo_dado = map(int, self.dado_dano.lower().split('d'))
            return sum(random.randint(1, tipo_dado) for _ in range(num_dados))
        except: return 1

class Armadura(Item):
    def __init__(self, id_entidade: int, nome: str, descricao: str, peso: float, valor_moedas: int,
                 tipo_armadura: str, bonus_ca_base: int, requer_destreza_bonus: bool,
                 max_bonus_destreza: Optional[int], penalidade_furtividade: bool, requisito_forca: int,
                 bonus_pv: int = 0):
        super().__init__(id_entidade, nome, descricao, peso, valor_moedas)
        self.tipo_armadura = tipo_armadura; self.bonus_ca_base = bonus_ca_base
        self.requer_destreza_bonus = requer_destreza_bonus; self.max_bonus_destreza = max_bonus_destreza
        self.penalidade_furtividade = penalidade_furtividade; self.requisito_forca = requisito_forca
        self.bonus_pv = bonus_pv
    def ser_usado(self, usuario: 'Personagem'):
        armadura_antiga = usuario.equipamento.get('Armadura')
        if isinstance(armadura_antiga, Armadura): usuario.pontos_vida_maximos -= armadura_antiga.bonus_pv
        usuario.equipamento['Armadura'] = self
        usuario.pontos_vida_maximos += self.bonus_pv
        usuario.pontos_vida_atuais = min(usuario.pontos_vida_atuais, usuario.pontos_vida_maximos)
        usuario.calcular_classe_armadura()

class Personagem(Entidade):
    def __init__(self, id_entidade: int, nome: str, raca: str, classe_personagem: str, nivel: int,
                 pontos_vida_maximos: int, atributos: Dict[str, int], proficiencias: List[str],
                 pontos_mana_maximos: int = 0):
        super().__init__(id_entidade, nome)
        self.raca = raca; self.classe_personagem = classe_personagem; self.nivel = nivel
        self.pontos_vida_maximos = pontos_vida_maximos; self.pontos_vida_atuais = pontos_vida_maximos
        self.pontos_mana_maximos = pontos_mana_maximos; self.pontos_mana_atuais = pontos_mana_maximos
        self.atributos = atributos; self.proficiencias = proficiencias
        self.inventario: List[Item] = []; self.magias: List[Magia] = []
        self.equipamento: Dict[str, Optional[Item]] = {"Arma": None, "Armadura": None}
        self.calcular_classe_armadura()

    def calcular_classe_armadura(self): self.classe_armadura = 10 # Simplificado

    def atacar(self, alvo: 'Personagem') -> str:
        rolagem_ataque = random.randint(1, 20)
        if rolagem_ataque >= alvo.classe_armadura:
            arma = self.equipamento.get('Arma')
            dano = arma.calcular_dano_rolagem() if isinstance(arma, Arma) else 1
            alvo.receber_dano(dano)
            return f"{self.nome} acertou e causou {dano} de dano!"
        return f"{self.nome} errou o ataque."

    def receber_dano(self, quantidade: int):
        self.pontos_vida_atuais -= quantidade
        if self.pontos_vida_atuais <= 0: self.morrer()

    def morrer(self): self.pontos_vida_atuais = 0
    def usar_item(self, item: Item):
        if item not in self.inventario: self.inventario.append(item)
        item.ser_usado(self)
    
    def pode_conjurar(self, magia: Magia) -> bool:
        return self.pontos_mana_atuais >= magia.custo_mana

    def gastar_mana(self, custo: int):
        self.pontos_mana_atuais -= custo

class Jogador(Personagem):
    def __init__(self, id_entidade: int, nome: str, raca: str, classe_personagem: str, nivel: int,
                 pontos_vida_maximos: int, atributos: Dict[str, int], proficiencias: List[str],
                 experiencia: int, alinhamento: str, nome_jogador: str, pontos_mana_maximos: int = 0):
        super().__init__(id_entidade, nome, raca, classe_personagem, nivel, pontos_vida_maximos, atributos, proficiencias, pontos_mana_maximos)
        self.experiencia = experiencia; self.alinhamento = alinhamento; self.nome_jogador = nome_jogador
    def aprender_magia(self, magia: Magia):
        if magia not in self.magias: self.magias.append(magia)

class NPC(Personagem):
    def __init__(self, id_entidade: int, nome: str, raca: str, classe_personagem: str, nivel: int,
                 pontos_vida_maximos: int, atributos: Dict[str, int], proficiencias: List[str],
                 tipo: str, comportamento: str, dialogo: Optional[Any] = None, pontos_mana_maximos: int = 0):
        super().__init__(id_entidade, nome, raca, classe_personagem, nivel, pontos_vida_maximos, atributos, proficiencias, pontos_mana_maximos)
        self.tipo = tipo; self.comportamento = comportamento; self.dialogo = dialogo