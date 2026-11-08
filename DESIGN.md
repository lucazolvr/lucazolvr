# Perfil GitHub — direção visual

Redesenho solicitado em 8 de novembro de 2026. Composição compacta, voltada a identidade, contatos e stack. Não listar projetos nem repetir o conteúdo da landing page.

Referências consultadas:
- https://github.com/rzashakeri/beautify-github-profile — badges, ícones e widgets de atividade.
- https://github.com/luizacoelh/luizacoelh — banner, stack por ícones e contatos compactos.
- https://github.com/Adryanrr/Adryanrr — apresentação direta e badges de contato.
- https://github.com/screen-gd/screen-gd — poucos elementos e assets SVG próprios.

Banner baixo com nome e função centralizados, ondas violetas e detalhe dourado; quatro badges locais; uma frase de apresentação; duas fileiras de seis ícones; atividade real integrada ao circuito e legenda recolhida em details. Sem tabela de projetos, texto longo ou contadores inventados.

O dono pediu substituir as ondas lisas do cabeçalho pela retícula do Aute usada no portfólio. `header-pixel.svg` usa o mesmo Bayer 4×4 e camadas em roxo/lilás com luz dourada localizada. A faixa de baixo é mais espessa e irregular, sobe pelas laterais e preserva uma ilha fixa sem textura atrás dos textos. SVG autocontido, sem cursor/JavaScript no README; movimento vertical de apenas 4px em 11 segundos e versão parada em movimento reduzido. Gerador reproduzível em `scripts/render_header.py`.

Superfície #0d1117, tinta #f1edf9, lilás #c6afff e dourado #efd08f. Tipografia sem serifa, compatível com o ambiente do GitHub. Ícones coloridos de tecnologias em suportes discretos da mesma família, com alt e title. Badges de contato com altura de 36px e desenhos vetoriais no mesmo traço.

O circuito preserva os dias e intensidades reais. Dias ativos e maior sequência são calculados a partir desses dados. Nenhuma dependência externa de stats com dados privados incompletos. SVGs autocontidos e movimento reduzido preservados. O bloqueio de billing do Actions continua registrado em INSTALAR.md; não afirmar que a automação já executa.
