"""Gera a narração de um roteiro e ajusta os tempos das cenas ao áudio.

Uso: python3 narrar.py roteiros/X.json saida_dir
Gera saida_dir/X.mp3 e saida_dir/X.timed.json (roteiro com inicio/fim recalculados).
"""
import json, os, subprocess, sys, time

VOZ = os.environ.get("VOZ", "en-US-AndrewMultilingualNeural")
# Clone da voz do Henrique na ElevenLabs. A chave entra pelo segredo de rede do ambiente
# (cabeçalho xi-api-key para api.elevenlabs.io) ou pela variável ELEVENLABS_API_KEY.
ELEVEN_VOZ = os.environ.get("ELEVEN_VOZ", "DGkNwHBY2YolYgRaaWM0")
ELEVEN_MODELO = os.environ.get("ELEVEN_MODELO", "eleven_multilingual_v2")
RATE = os.environ.get("RATE", "+0%")
MIN_DUR = {"editor": 2.5, "checklist": 5.5, "tabela": 4.5, "agenda": 6.0, "comentario": 3.5}
GAP = 0.3


def dur(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(out)


os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")


def eleven(texto, destino):
    """Narra com o clone de voz na ElevenLabs. Devolve False se não der (sem chave, sem rede)."""
    import urllib.request
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOZ}?output_format=mp3_44100_128"
    corpo = json.dumps({"text": texto, "model_id": ELEVEN_MODELO,
                        "voice_settings": {"stability": 0.45, "similarity_boost": 0.85, "style": 0.2}}).encode()
    headers = {"Content-Type": "application/json", "Accept": "audio/mpeg"}
    if os.environ.get("ELEVENLABS_API_KEY"):
        headers["xi-api-key"] = os.environ["ELEVENLABS_API_KEY"]
    try:
        with urllib.request.urlopen(urllib.request.Request(url, corpo, headers), timeout=60) as resp:
            dados = resp.read()
        if len(dados) < 1000:
            return False
        open(destino, "wb").write(dados)
        return True
    except Exception as e:
        print("ElevenLabs indisponível, usando voz gratuita:", e, file=sys.stderr)
        return False


def main(roteiro_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    r = json.load(open(roteiro_path))
    env = dict(os.environ, SSL_CERT_FILE="/root/.ccr/ca-bundle.crt")
    proxy = os.environ.get("HTTPS_PROXY")
    t, parts = 0.0, []
    eleven_ok = None if os.environ.get("SO_EDGE") != "1" else False
    for i, c in enumerate(r["cenas"]):
        mp3 = os.path.join(out_dir, f"{r['id']}-{i}.mp3")
        cmd = ["edge-tts", "--voice", VOZ, f"--rate={RATE}", "--text", c["fala"], "--write-media", mp3]
        if proxy:
            cmd += ["--proxy", proxy]
        if eleven_ok is not False and eleven(c["fala"], mp3):
            eleven_ok = True
        elif eleven_ok:
            raise RuntimeError(f"ElevenLabs falhou na cena {i}; não misturo vozes")
        else:
          eleven_ok = False
          for tentativa in range(5):  # o serviço de voz falha de vez em quando
            if subprocess.run(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                break
            time.sleep(2 + tentativa * 2)
          else:
            raise RuntimeError(f"narração falhou na cena {i}")
        d = dur(mp3)
        cena_dur = max(d + GAP, MIN_DUR.get(c["visual"]["tipo"], 3.0))
        c["inicio"], c["fim"] = round(t, 3), round(t + cena_dur, 3)
        c["fala_dur"] = round(d, 3)
        parts.append((mp3, t))
        t += cena_dur
    total = t + 0.6
    r["cenas"][-1]["fim"] = round(total, 3)

    # junta os áudios, cada um no início da sua cena
    args = ["ffmpeg", "-y", "-loglevel", "error"]
    for mp3, _ in parts:
        args += ["-i", mp3]
    filt = "".join(f"[{i}]adelay={int(st*1000)}|{int(st*1000)}[a{i}];" for i, (_, st) in enumerate(parts))
    filt += "".join(f"[a{i}]" for i in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0,apad,atrim=0:{total}[out]"
    audio = os.path.join(out_dir, f"{r['id']}.mp3")
    subprocess.run(args + ["-filter_complex", filt, "-map", "[out]", audio], check=True)
    for mp3, _ in parts:
        os.remove(mp3)
    timed = os.path.join(out_dir, f"{r['id']}.timed.json")
    json.dump(r, open(timed, "w"), ensure_ascii=False, indent=2)
    print(audio, timed, f"{total:.1f}s", "voz:", "clone ElevenLabs" if eleven_ok else VOZ)


if __name__ == "__main__":
    main(*sys.argv[1:3])
