"""Gera a narração de um roteiro e ajusta os tempos das cenas ao áudio.

Uso: python3 narrar.py roteiros/X.json saida_dir
Gera saida_dir/X.mp3 e saida_dir/X.timed.json (roteiro com inicio/fim recalculados).
"""
import json, os, subprocess, sys

VOZ = os.environ.get("VOZ", "pt-BR-AntonioNeural")
RATE = os.environ.get("RATE", "+12%")
MIN_DUR = {"editor": 2.5, "checklist": 5.5, "tabela": 4.5, "agenda": 6.0, "comentario": 3.5}
GAP = 0.3


def dur(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(out)


def main(roteiro_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    r = json.load(open(roteiro_path))
    env = dict(os.environ, SSL_CERT_FILE="/root/.ccr/ca-bundle.crt")
    proxy = os.environ.get("HTTPS_PROXY")
    t, parts = 0.0, []
    for i, c in enumerate(r["cenas"]):
        mp3 = os.path.join(out_dir, f"{r['id']}-{i}.mp3")
        cmd = ["edge-tts", "--voice", VOZ, f"--rate={RATE}", "--text", c["fala"], "--write-media", mp3]
        if proxy:
            cmd += ["--proxy", proxy]
        subprocess.run(cmd, check=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
    print(audio, timed, f"{total:.1f}s")


if __name__ == "__main__":
    main(*sys.argv[1:3])
