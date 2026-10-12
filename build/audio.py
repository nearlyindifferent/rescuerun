"""Synthesised sound effects + music for Rescue Runner (plain 16-bit mono WAV files).

Everything is generated from simple waves, so the project has no copyrighted audio.
"""
import io
import wave

import numpy as np

RATE = 22050


def _wav(samples):
    x = np.asarray(samples, dtype=float)
    peak = np.abs(x).max()
    if peak > 0.85:                                   # keep a little headroom (no clipping)
        x = x * (0.85 / peak)
    x = np.clip(x, -1, 1)
    pcm = (x * 32000).astype("<i2").tobytes()
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm)
    return buf.getvalue()


def _t(dur):
    return np.arange(int(RATE * dur)) / RATE


def _env(n, attack=0.005, release=0.08):
    e = np.ones(n)
    a, r = int(RATE * attack), int(RATE * release)
    if a:
        e[:a] = np.linspace(0, 1, a)
    if r:
        e[-r:] = np.minimum(e[-r:], np.linspace(1, 0, r))
    return e


def note(freq, dur, kind="sine", vol=0.5, decay=4.0):
    t = _t(dur)
    ph = 2 * np.pi * freq * t
    if kind == "square":
        w = np.sign(np.sin(ph)) * 0.6 + 0.4 * np.sin(ph)
    elif kind == "tri":
        w = 2 / np.pi * np.arcsin(np.sin(ph))
    elif kind == "bell":
        w = np.sin(ph) + 0.4 * np.sin(2.01 * ph) + 0.2 * np.sin(3.02 * ph)
        w /= 1.6
    else:
        w = np.sin(ph)
    return vol * w * np.exp(-decay * t) * _env(len(t), 0.004, 0.03)


def _place(buf, start, sig):
    i = int(start * RATE)
    n = min(len(sig), len(buf) - i)
    if n > 0:
        buf[i:i + n] += sig[:n]


NOTE = {"C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23, "G4": 392.0, "A4": 440.0, "B4": 493.88,
        "C5": 523.25, "D5": 587.33, "E5": 659.25, "F5": 698.46, "G5": 783.99, "A5": 880.0, "B5": 987.77,
        "C6": 1046.5, "E6": 1318.5, "G6": 1568.0, "A3": 220.0, "G3": 196.0, "F3": 174.61, "E3": 164.81,
        "C3": 130.81, "D3": 146.83, "B3": 246.94}


def jump():
    t = _t(0.26)
    f = 280 + 520 * (t / 0.26) ** 0.7                       # rising "boing"
    ph = 2 * np.pi * np.cumsum(f) / RATE
    return _wav(0.45 * np.sin(ph) * np.exp(-3.5 * t) * _env(len(t), 0.004, 0.05))


def collect():
    buf = np.zeros(int(RATE * 0.55))
    _place(buf, 0.0, note(NOTE["E6"], 0.3, "bell", 0.45, 6))
    _place(buf, 0.09, note(NOTE["A5"] * 2, 0.45, "bell", 0.45, 5))
    return _wav(buf)


def start():
    buf = np.zeros(int(RATE * 0.5))
    for i, n in enumerate(["C5", "E5", "G5"]):
        _place(buf, i * 0.1, note(NOTE[n], 0.25, "tri", 0.5, 5))
    return _wav(buf)


def win():
    buf = np.zeros(int(RATE * 2.4))
    seq = [("C5", 0.0, 0.18), ("E5", 0.16, 0.18), ("G5", 0.32, 0.18), ("C6", 0.48, 0.5),
           ("G5", 1.0, 0.16), ("C6", 1.16, 0.16), ("E6", 1.32, 0.9)]
    for n, st, d in seq:
        _place(buf, st, note(NOTE[n], d + 0.3, "square", 0.22, 2.2))
        _place(buf, st, note(NOTE[n], d + 0.3, "bell", 0.25, 2.5))
    for n in ["C4", "E4", "G4"]:
        _place(buf, 1.32, note(NOTE[n], 1.0, "tri", 0.22, 1.6))
    return _wav(buf)


def lose():
    buf = np.zeros(int(RATE * 1.8))
    for i, (n, d) in enumerate([("G4", 0.28), ("E4", 0.28), ("C4", 0.28), ("A3", 0.9)]):
        st = [0.0, 0.3, 0.6, 0.9][i]
        _place(buf, st, note(NOTE[n], d + 0.2, "tri", 0.5, 2.2))
    # slow downward slide on the last note
    t = _t(0.8)
    f = 220 * (1 - 0.35 * (t / 0.8))
    _place(buf, 0.95, 0.35 * np.sin(2 * np.pi * np.cumsum(f) / RATE) * np.exp(-2.4 * t))
    return _wav(buf)


def alarm():
    buf = np.zeros(int(RATE * 0.7))
    for i in range(3):
        _place(buf, i * 0.22, note(880 if i % 2 == 0 else 660, 0.18, "square", 0.3, 5))
    return _wav(buf)


def splash():
    rng = np.random.default_rng(7)
    t = _t(0.4)
    n = rng.normal(0, 1, len(t))
    # crude low-pass by moving average => watery "shhh"
    k = 14
    n = np.convolve(n, np.ones(k) / k, mode="same")
    return _wav(0.9 * n * np.exp(-6 * t) * _env(len(t), 0.003, 0.1))


def music():
    """~12 second cheerful loop: bass + chord pulse + a simple tune (C major)."""
    bpm = 132
    beat = 60 / bpm
    bars = 6
    total = bars * 4 * beat
    buf = np.zeros(int(RATE * total) + RATE // 2)
    chords = [("C3", ["C4", "E4", "G4"]), ("A3", ["C4", "E4", "A4"]),
              ("F3", ["C4", "F4", "A4"]), ("G3", ["B3", "D4", "G4"])]
    prog = [0, 1, 2, 3, 0, 1, 2, 3][:bars] if bars <= 8 else [0, 1, 2, 3]
    prog = [0, 1, 2, 3, 2, 3][:bars]
    for bar, ci in enumerate(prog):
        root, chord = chords[ci]
        b0 = bar * 4 * beat
        for k in range(4):                                  # bouncy bass on 1 and 3, chords on the off-beats
            if k in (0, 2):
                _place(buf, b0 + k * beat, note(NOTE[root], beat * 0.9, "tri", 0.34, 3))
            else:
                for c in chord:
                    _place(buf, b0 + k * beat, note(NOTE[c] * 1.0, beat * 0.5, "square", 0.045, 6))
    melody = [("E5", 1), ("G5", 1), ("E5", 1), ("C5", 1), ("D5", 1), ("E5", 0.5), ("D5", 0.5), ("C5", 2),
              ("A4", 1), ("C5", 1), ("E5", 1), ("C5", 1), ("D5", 1), ("B4", 1), ("G4", 2),
              ("F5", 1), ("A5", 1), ("F5", 1), ("C5", 1), ("E5", 1), ("D5", 0.5), ("C5", 0.5), ("E5", 2),
              ("D5", 1), ("G5", 1), ("E5", 1), ("D5", 1), ("C5", 4)]
    pos = 0.0
    for n, d in melody:
        if pos >= total - 0.01:
            break
        _place(buf, pos * beat, note(NOTE[n], d * beat * 0.95, "square", 0.075, 3.0))
        _place(buf, pos * beat, note(NOTE[n], d * beat * 0.95, "tri", 0.1, 3.0))
        pos += d
    buf = buf[: int(RATE * total)]
    return _wav(buf * 0.9)


SOUNDS = {"jump": jump, "collect": collect, "start": start, "win": win, "lose": lose,
          "alarm": alarm, "splash": splash, "music": music}


def all_sounds():
    return {k: f() for k, f in SOUNDS.items()}


if __name__ == "__main__":
    import sys
    for k, v in all_sounds().items():
        n = len(v)
        print("%-8s %6.1f KB" % (k, n / 1024))
