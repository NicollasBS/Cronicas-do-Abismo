# Projeto de Estrutura de Classes - RPG D&D

Baseado nos requisitos do trabalho e na análise do funcionamento de Dungeons & Dragons 5ª Edição, a seguinte estrutura de classes é proposta:

1.  **`Entidade` (Classe Base Abstrata - Opcional, mas boa prática):**
    *   Pode conter atributos comuns a todos os elementos do jogo, como `id` e `nome`.
    *   *Atributos:* `id` (int), `nome` (str)

2.  **`Personagem` (Herda de `Entidade` ou classe base):**
    *   Representa a base para qualquer criatura no jogo, seja jogador ou NPC.
    *   *Atributos:* `raca` (str), `classe_personagem` (str - *evitar usar "classe" para não confundir com classe de programação*), `nivel` (int), `pontos_vida_maximos` (int), `pontos_vida_atuais` (int), `atributos` (dict - ex: `{"Força": 10, "Destreza": 12, ...}`), `inventario` (list[Item]), `classe_armadura` (int), `proficiencias` (list[str]), `equipamento` (dict - ex: `{"Arma": Arma, "Armadura": Armadura}`).
    *   *Métodos (Protótipos):* `atacar(alvo: Personagem)`, `receber_dano(quantidade: int)`, `usar_item(item: Item)`, `morrer()`.

3.  **`Jogador` (Herda de `Personagem`):**
    *   Representa os personagens controlados pelos usuários.
    *   *Atributos:* `experiencia` (int), `alinhamento` (str), `nome_jogador` (str - *nome real do jogador, se aplicável*).
    *   *Métodos (Protótipos):* `ganhar_experiencia(quantidade: int)`, `subir_nivel()`, `escolher_acao()`.

4.  **`NPC` (Non-Player Character - Herda de `Personagem`):**
    *   Representa personagens controlados pelo Mestre (ou pelo sistema).
    *   *Atributos:* `tipo` (str - ex: "Monstro", "Aliado", "Comerciante"), `comportamento` (str - ex: "Agressivo", "Neutro", "Amigável"), `dialogo` (str ou dict).
    *   *Métodos (Protótipos):* `interagir(jogador: Jogador)`, `determinar_acao_combate()`.

5.  **`Item` (Herda de `Entidade` ou classe base):**
    *   Classe base para todos os objetos que podem ser coletados ou usados.
    *   *Atributos:* `descricao` (str), `peso` (float), `valor_moedas` (int).
    *   *Métodos (Protótipos):* `ser_usado(usuario: Personagem)`.

6.  **`Arma` (Herda de `Item`):**
    *   Representa itens usados para atacar.
    *   *Atributos:* `tipo_dano` (str - ex: "Cortante", "Perfurante", "Concussão"), `dado_dano` (str - ex: "1d8", "2d6"), `propriedades` (list[str] - ex: "Acuidade", "Pesada", "Duas Mãos"), `alcance` (str).
    *   *Métodos (Protótipos):* `calcular_dano_rolagem()`.

7.  **`Armadura` (Herda de `Item`):**
    *   Representa itens usados para defesa (aumentar CA).
    *   *Atributos:* `tipo_armadura` (str - ex: "Leve", "Média", "Pesada", "Escudo"), `bonus_ca_base` (int), `requer_destreza_bonus` (bool), `max_bonus_destreza` (int or None), `penalidade_furtividade` (bool), `requisito_forca` (int).

8.  **`Pocao` (Herda de `Item`):**
    *   Representa itens consumíveis com efeitos mágicos ou de cura.
    *   *Atributos:* `efeito` (str), `duracao_efeito` (str), `quantidade_cura` (int or None).
    *   *Métodos (Protótipos):* `aplicar_efeito(alvo: Personagem)`.

9.  **`Magia` (Herda de `Entidade` ou classe base):**
    *   Representa os feitiços que personagens conjuradores podem usar.
    *   *Atributos:* `nivel_magia` (int), `escola_magia` (str), `tempo_conjuracao` (str), `alcance_magia` (str), `componentes` (list[str] - V, S, M), `duracao_magia` (str), `descricao_efeito` (str), `requer_concentracao` (bool).
    *   *Métodos (Protótipos):* `conjurar(conjurador: Personagem, alvo: Personagem or None)`.

Esta estrutura inicial contém mais de 5 classes e fornece uma base sólida para o desenvolvimento do sistema de RPG, cobrindo personagens, itens e magias. Os atributos e métodos são iniciais e podem ser refinados durante a implementação.

