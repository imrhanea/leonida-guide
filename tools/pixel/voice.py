"""Traitement d'une voix off enregistrée au téléphone.

- découpe l'enregistrement en phrases grâce aux pauses (ffmpeg silencedetect) ;
- recolle les phrases avec des silences courts (rythme TikTok) ;
- améliore le son (filtre, compresseur, volume normalisé) ;
- renvoie la durée de chaque phrase dans la nouvelle piste.
"""
import re, subprocess, tempfile, pathlib

GAP = 0.12        # silence gardé entre deux phrases (secondes)
PAD = 0.06        # marge gardée avant/après chaque phrase


def _duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def _speech_segments(path, noise_db, min_sil):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af",
                        f"silencedetect=noise={noise_db}dB:d={min_sil}", "-f", "null", "-"],
                       capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    total = _duration(path)
    sil = list(zip(starts, ends + [total] * (len(starts) - len(ends))))
    segs, cur = [], 0.0
    for s, e in sil:
        if s - cur > 0.15:
            segs.append((cur, s))
        cur = e
    if total - cur > 0.15:
        segs.append((cur, total))
    return segs


def split_phrases(path, n_expected):
    """Cherche le réglage de détection qui donne exactement n_expected phrases.
    Sinon, fusionne les phrases séparées par les pauses les plus courtes."""
    best = None
    for noise in (-35, -30, -40, -28, -45):
        for d in (0.45, 0.35, 0.55, 0.3, 0.7, 0.25):
            segs = _speech_segments(path, noise, d)
            if len(segs) == n_expected:
                return segs
            if len(segs) >= n_expected and (best is None or len(segs) < len(best)):
                best = segs
    if best is None:
        raise SystemExit(f"Je ne trouve que des phrases trop peu nombreuses (attendu {n_expected}). "
                         "Il faut marquer une pause d'environ 1 seconde entre chaque ligne.")
    segs = list(best)
    while len(segs) > n_expected:   # fusion des deux morceaux les plus proches
        gaps = [segs[i + 1][0] - segs[i][1] for i in range(len(segs) - 1)]
        i = gaps.index(min(gaps))
        segs[i:i + 2] = [(segs[i][0], segs[i + 1][1])]
    return segs


def build_voice_track(path, n_expected, out_wav):
    """Crée la piste voix finale ; renvoie la liste des (début, fin) de chaque phrase dedans."""
    segs = split_phrases(path, n_expected)
    total = _duration(path)
    with tempfile.TemporaryDirectory() as tmp:
        parts, timeline, t = [], [], 0.0
        for i, (s, e) in enumerate(segs):
            s, e = max(0.0, s - PAD), min(total, e + PAD)
            p = f"{tmp}/p{i:02d}.wav"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{s:.3f}", "-to", f"{e:.3f}",
                            "-i", str(path), "-ac", "1", "-ar", "44100", p], check=True)
            parts.append(p)
            timeline.append((t, t + (e - s)))
            t += (e - s) + GAP
        lst = pathlib.Path(tmp) / "list.txt"
        silence = f"{tmp}/gap.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                        "anullsrc=r=44100:cl=mono", "-t", str(GAP), silence], check=True)
        lst.write_text("".join(f"file '{p}'\nfile '{silence}'\n" for p in parts))
        raw = f"{tmp}/raw.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                        "-i", str(lst), "-c", "copy", raw], check=True)
        # son plus percutant : coupe les graves parasites, compresse, normalise le volume
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                        "highpass=f=90,lowpass=f=13000,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,"
                        "loudnorm=I=-14:TP=-1.5:LRA=7", "-ar", "44100", str(out_wav)], check=True)
    return timeline
