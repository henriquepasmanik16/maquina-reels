# Rotina diária da máquina de reels

Executada por duas tarefas agendadas do Claude, seg a sáb: manhã (09:13) e tarde (15:47), horário de Brasília. Conta: @henrique.agentes (Windsor, conector `instagram`, conta 17841467096525385). O Henrique autorizou publicar sem aprovação **desde que o vídeo passe em `diretrizes.md`**.

## Passos
1. Preparar: `pip install -q edge-tts`. Playwright (Chromium) e ffmpeg já existem no container.
2. Ler `diretrizes.md`, `publicados.json` e os roteiros em `roteiros/`. São dois reels por dia (manhã e tarde). Se `publicados.json` já tem 2 posts com a data de hoje (America/Sao_Paulo), ou um post há menos de 5 horas, pular para o passo 9. Registre também a hora (`hora`, HH:MM) em cada entrada nova.
   Se as ferramentas do Windsor (instagram) não estiverem disponíveis, gerar e subir o vídeo mesmo assim, registrar em `pendentes.md` que faltou o conector e parar.
3a. Pesquisar a novidade do dia (as mesmas fontes que os criadores do nicho usam):
   - GitHub: repositórios novos que estão explodindo. `gh api -X GET search/repositories -f q='claude created:>AAAA-MM-DD' -f sort=stars -f per_page=15` (data de 10 dias atrás); repetir com `skill`, `mcp`, `agent`, `claude code`. Bons temas: skills/ferramentas grátis do Claude com muitas estrelas.
   - WebSearch (se disponível): lançamentos da semana da Anthropic/Claude (Claude Code, skills, novos modelos) e de outras IAs, preferindo a fonte oficial.
   - Antes de usar, abrir o README/página oficial e confirmar o que a ferramenta faz. Só afirmar o que estiver lá. Anotar a fonte em `fonte` no roteiro e citar o nome do repositório na legenda.
   - Se nada novo e confiável aparecer, usar um tema de `referencias/igao-ia.md` com ângulo próprio.
3. Escrever um roteiro novo `roteiros/NN-slug.json` no mesmo formato do `01-claude-posta-por-mim.json`:
   - 5 cenas: Gancho, Problema, Virada, Prova, CTA. Tema do nicho agentes de IA / automação com o Claude, diferente dos últimos 10 em `publicados.json`.
   - Tema: inspirar-se nos temas de `referencias/igao-ia.md` (uma ferramenta, arquivo, skill ou truque concreto de IA, com promessa clara), priorizando os de mais views. Mudar o ângulo e escrever com palavras próprias: nunca repetir título, frase, exemplo ou arte de outro criador. Só falar de ferramenta/fato que você consiga explicar corretamente; na dúvida, escolha outro tema.
   - Campo `capa` obrigatório: `{"texto": "frase curta de 3 a 7 palavras", "destaque": "2 a 4 palavras que fecham a promessa"}`. Aparece no topo do vídeo inteiro (vira a capa do reel).
   - Opcional por cena: `visual.icone` com um emoji que represente a cena (aparece no bloco 3D).
   - `visual.tipo` só entre: editor, checklist, tabela (linhas de 1 item, sem números), agenda, comentario.
   - Nenhum número inventado. CTA: "Comenta AGENTE que eu te respondo com ..." (algo que caiba numa resposta de comentário).
4. `python3 narrar.py roteiros/NN-slug.json build` e `node render.js build/NN-slug.timed.json videos/NN-slug.mp4 build/NN-slug.mp3`.
5. Conferir: duração 20-35s (ffprobe), um frame do meio sem erro visual, checklist de `diretrizes.md`. Se algo falhar, não publicar: registrar o motivo em `pendentes.md` e parar.
6. Commit e push de roteiro + vídeo na `main`.
7. Publicar com `create_video_post`: `video_url` = `https://raw.githubusercontent.com/henriquepasmanik16/maquina-reels/main/videos/NN-slug.mp4`, legenda de 1 a 3 frases + CTA + "Vídeo e narração gerados com IA." + 3 a 5 hashtags.
8. Acrescentar a entrada em `publicados.json` (data, id, tema, media_id), commit e push.
9. Comentários: ler os comentários dos posts dos últimos 7 dias. Para cada comentário com "AGENTE" ainda sem resposta da conta, responder com `reply_to_comment` com o passo a passo prometido no CTA daquele post (curto, até ~600 caracteres, sem link). Não responder duas vezes ao mesmo comentário.
