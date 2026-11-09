# README de perfil — Lucas de Oliveira

Este é um pacote independente. Não substitui o README do portfólio e não altera o site.

## Colocar no perfil

1. Use o repositório público **lucazolvr/lucazolvr**, com o mesmo nome do seu usuário.
2. Copie **o conteúdo desta pasta** para a raiz dele, incluindo `assets`, `data`, `scripts`, `tests` e `.github`. O arquivo `README.md` precisa ficar na raiz, e não dentro de `github-profile`.
3. O README já funciona com as imagens incluídas. Só colar o Markdown, sem enviar as imagens, deixa os links locais quebrados.
4. Em **Actions**, execute **Atualizar Circuito de Commits** uma vez. Depois, o workflow tenta atualizar diariamente às 06:23 de Fortaleza (09:23 UTC); o GitHub pode atrasar execuções agendadas.

O workflow usa somente o `GITHUB_TOKEN` automático para salvar os arquivos neste repositório. **Não precisa cadastrar PAT nem dar acesso aos repositórios privados.** O script lê as contagens anonimizadas já visíveis em https://github.com/users/lucazolvr/contributions. Se esse formato mudar ou vier incompleto, ele falha e mantém a pista anterior, em vez de inventar atividade.

**Estado em 08/11/2026:** o README foi publicado, mas a primeira execução do workflow foi bloqueada pelo GitHub antes de iniciar, com a mensagem “The job was not started because your account is locked due to a billing issue.” A atualização automática depende da resolução dessa pendência da conta. As imagens publicadas continuam funcionando com o snapshot atual; nenhuma configuração de cobrança foi alterada.

Se as contribuições privadas forem ocultadas no perfil, as contagens da imagem também deixarão de incluí-las na próxima atualização. Esse desenho representa **contribuições**, não apenas commits: é a mesma métrica do calendário do GitHub.

## Como a pista representa os dados

- Todos os dias retornados pelo calendário são usados uma única vez, inclusive dias sem atividade.
- Os dias avançam do mais antigo ao mais recente a partir da largada. Cada trecho tem três blocos, da esquerda para a direita em relação ao sentido do percurso.
- Roxo escuro representa zero; roxo, lilás e dourado representam os quatro níveis de atividade retornados pelo GitHub.
- As curvas, os blocos e a posição do kart usam a mesma linha de percurso. O kart viaja a velocidade constante e seleciona entre 16 vistas conforme a direção.
- O README usa um SVG autocontido com movimento interpolado e sprites direcionais, sem JavaScript ou imagens externas. Ele respeita movimento reduzido. O GIF alternativo tem 480 frames a 20 fps, formando uma volta de 24 segundos sem teleporte na emenda. `commit-circuit.png` é a alternativa estática.
- `assets/circuit-map.json` relaciona cada bloco à data, contagem e nível originais; `data/contributions.json` guarda a fonte e a data da atualização.

## Atualizar localmente

Requer Python 3.11 ou superior. No Linux/macOS:

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python -m unittest discover -s tests
.venv/bin/python scripts/render_circuit.py --refresh
```

No Windows, use `.venv\Scripts\python.exe` e `.venv\Scripts\pip.exe`.

Sem `--refresh`, o renderizador usa o snapshot incluído. A mesma execução atualiza os SVGs da apresentação, dos contatos e do circuito. Eles compartilham as mesmas coordenadas de fundo para formar um painel contínuo com links individuais. Ícones, badges e sprites são locais. A direção e as referências do redesenho estão em DESIGN.md.

## Referências

- [Requisitos do README de perfil](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme)
- [Contribuições privadas anonimizadas](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/manage-visibility-settings-for-private-contributions-and-achievements)
- [Sintaxe dos workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
