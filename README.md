# Máquina de reels — @henrique.agentes

Gera reels verticais (1080x1920, ~30s) a partir de um roteiro em JSON, com cards animados, legenda palavra por palavra e narração por IA. Operada pelo Claude.

## Uso
```bash
pip install edge-tts
python3 narrar.py roteiros/01-claude-posta-por-mim.json build   # narração + tempos das cenas
node render.js build/01-claude-posta-por-mim.timed.json out.mp4 build/01-claude-posta-por-mim.mp3
```
Precisa de Node com Playwright (Chromium) e ffmpeg.

## Estrutura
- `roteiros/` — um JSON por reel, no molde Gancho / Problema / Virada / Prova / CTA.
- `templates/reel.html` — a animação (cada cena tem um `visual.tipo`: editor, checklist, tabela, agenda, comentario).
- `render.js` — renderiza quadro a quadro e junta com ffmpeg.
- `narrar.py` — gera a voz de cada cena e ajusta a duração das cenas à fala.
- `diretrizes.md` — regras que todo vídeo precisa cumprir antes de ser publicado.
- `videos/` — vídeos prontos, servidos por link público para a publicação no Instagram.
