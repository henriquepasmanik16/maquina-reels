// Uso: node render.js roteiros/X.json saida.mp4 [audio.mp3]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

(async () => {
  const [roteiroPath, out, audio] = process.argv.slice(2);
  const roteiro = JSON.parse(fs.readFileSync(roteiroPath, 'utf8'));
  const FPS = 30;
  const total = roteiro.cenas[roteiro.cenas.length - 1].fim;
  const frames = Math.round(total * FPS);

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.addInitScript(r => { window.ROTEIRO = r; }, roteiro);
  await page.goto('file://' + path.resolve(__dirname, 'templates/reel.html'));
  await page.evaluate(() => document.fonts.ready);

  const args = ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-'];
  if (audio) args.push('-i', audio, '-c:a', 'aac', '-b:a', '192k', '-shortest');
  args.push('-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'medium', '-crf', '20', '-movflags', '+faststart', out);
  const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'ignore', 'inherit'] });

  for (let i = 0; i < frames; i++) {
    await page.evaluate(t => window.render(t), i / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.error(`frame ${i}/${frames}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.error('ok:', out);
})();
