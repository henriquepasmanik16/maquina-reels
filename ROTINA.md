# Rotina diária da máquina de reels

Executada por uma tarefa agendada do Claude, seg a sáb. Conta: @henrique.agentes (Windsor, conector `instagram`, conta 17841467096525385). O Henrique autorizou publicar sem aprovação **desde que o vídeo passe em `diretrizes.md`**.

## Passos
1. Preparar: `pip install -q edge-tts`. Playwright (Chromium) e ffmpeg já existem no container.
2. Ler `diretrizes.md`, `publicados.json` e os roteiros em `roteiros/`. Se `publicados.json` já tem um post com a data de hoje (America/Sao_Paulo), pular para o passo 9.
   Se as ferramentas do Windsor (instagram) não estiverem disponíveis, gerar e subir o vídeo mesmo assim, registrar em `pendentes.md` que faltou o conector e parar.
3. Escrever um roteiro novo `roteiros/NN-slug.json` no mesmo formato do `01-claude-posta-por-mim.json`:
   - 5 cenas: Gancho, Problema, Virada, Prova, CTA. Tema do nicho agentes de IA / automação com o Claude, diferente dos últimos 10 em `publicados.json`.
   - `visual.tipo` só entre: editor, checklist, tabela (linhas de 1 item, sem números), agenda, comentario.
   - Nenhum número inventado. CTA: "Comenta AGENTE que eu te respondo com ..." (algo que caiba numa resposta de comentário).
4. `python3 narrar.py roteiros/NN-slug.json build` e `node render.js build/NN-slug.timed.json videos/NN-slug.mp4 build/NN-slug.mp3`.
5. Conferir: duração 20-35s (ffprobe), um frame do meio sem erro visual, checklist de `diretrizes.md`. Se algo falhar, não publicar: registrar o motivo em `pendentes.md` e parar.
6. Commit e push de roteiro + vídeo na `main`.
7. Publicar com `create_video_post`: `video_url` = `https://raw.githubusercontent.com/henriquepasmanik16/maquina-reels/main/videos/NN-slug.mp4`, legenda de 1 a 3 frases + CTA + "Vídeo e narração gerados com IA." + 3 a 5 hashtags.
8. Acrescentar a entrada em `publicados.json` (data, id, tema, media_id), commit e push.
9. Comentários: ler os comentários dos posts dos últimos 7 dias. Para cada comentário com "AGENTE" ainda sem resposta da conta, responder com `reply_to_comment` com o passo a passo prometido no CTA daquele post (curto, até ~600 caracteres, sem link). Não responder duas vezes ao mesmo comentário.
