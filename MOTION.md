# Motion — Circuito de Commits do perfil

Preservar o gato, o kart e as 16 vistas aprovadas no portfólio. A pista é a própria visualização dos dados: um dia por bloco, três faixas, percurso cronológico fechado. Não colocar um circuito em volta de um calendário retangular.

Um único relógio controla o percurso e a suspensão de menos de um pixel. Parametrização por distância mantém a velocidade constante, inclusive nas curvas; a volta se fecha sem teleportar. Nenhum clarão, mudança aleatória por frame ou fundo pulsante. Só o kart e um pequeno escape de pixels se movem.

Destino: SVG autocontido dentro de README do GitHub, com interpolação SMIL e sprites embutidos, sem JavaScript, canvas ou recursos externos. O SVG troca para uma imagem estática em `prefers-reduced-motion`. Também gerar GIF e fornecer PNG estático no README. O site não é alterado.
