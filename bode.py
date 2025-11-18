import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Les CSV-fil
df = pd.read_csv("bodeFilter.csv")

# Hent frekvens og magnitude, sorter etter frekvens
freq = df["Frequency (Hz)"].to_numpy(dtype=float)
mag_db = df["Channel 1 Magnitude (dB)"].to_numpy(dtype=float)
sort_idx = np.argsort(freq)
freq = freq[sort_idx]
mag_db = mag_db[sort_idx]

# ønsket resonansfrekvens
f0 = 1160.0

# interpoler magnitude i f0 (hvis f0 ikke finnes nøyaktig i data)
mag_f0 = float(np.interp(f0, freq, mag_db))
level_3db = mag_f0 - 3.0

def find_crossing_around(f, mag, level, center_freq, direction):
    """
    Finn frekvens hvor mag krysser under 'level' ved å søke bort fra center_freq.
    direction = -1 (venstre), +1 (høyre).
    Returnerer interpolert frekvens eller None.
    """
    # start fra nærmeste indeks til center_freq
    idx = int(np.argmin(np.abs(f - center_freq)))
    n = len(mag)

    if direction == -1:
        i = idx
        # hvis startpunkt allerede under nivå, søk mot venstre etter et punkt over nivå
        if mag[i] < level:
            while i > 0 and mag[i] < level:
                i -= 1
            if i == 0 and mag[i] < level:
                return None
        # gå venstre mens mag >= level
        while i > 0 and mag[i] >= level:
            i -= 1
        # nå er mag[i] < level og mag[i+1] >= level (forutsatt at kryss finnes)
        if i >= 0 and i < n - 1:
            f0_l, f1_l = f[i], f[i + 1]
            m0, m1 = mag[i], mag[i + 1]
            if m1 == m0:
                return 0.5 * (f0_l + f1_l)
            return f0_l + (level - m0) * (f1_l - f0_l) / (m1 - m0)
        return None

    else:
        i = idx
        # hvis startpunkt allerede under nivå, søk mot høyre etter et punkt over nivå
        if mag[i] < level:
            while i < n - 1 and mag[i] < level:
                i += 1
            if i == n - 1 and mag[i] < level:
                return None
        # gå høyre mens mag >= level
        while i < n - 1 and mag[i] >= level:
            i += 1
        # nå er mag[i] < level og mag[i-1] >= level
        if i > 0 and i < n:
            f0_l, f1_l = f[i - 1], f[i]
            m0, m1 = mag[i - 1], mag[i]
            if m1 == m0:
                return 0.5 * (f0_l + f1_l)
            return f0_l + (level - m0) * (f1_l - f0_l) / (m1 - m0)
        return None

# finn venstre og høyre -3 dB kryss rundt f0
f_left = find_crossing_around(freq, mag_db, level_3db, f0, -1)
f_right = find_crossing_around(freq, mag_db, level_3db, f0, +1)

bandwidth = None
Q = None
if f_left is not None and f_right is not None and f_right > f_left:
    bandwidth = f_right - f_left
    Q = f0 / bandwidth

# Plot
plt.figure(figsize=(8, 5))
plt.plot(freq, mag_db, label="Channel 1")
plt.axvline(x=f0, color="red", linestyle="--", linewidth=1.2, label=f"f0 = {f0:.1f} Hz")
plt.hlines(level_3db, xmin=freq.min(), xmax=freq.max(), colors='gray', linestyles=':', linewidth=0.8, label='-3 dB fra f0')
if f_left is not None:
    plt.axvline(f_left, color='orange', linestyle='--', linewidth=1, label=f'f_left = {f_left:.1f} Hz')
if f_right is not None:
    plt.axvline(f_right, color='orange', linestyle='--', linewidth=1, label=f'f_right = {f_right:.1f} Hz')

plt.title("Amplituderespons (beregnet BW/Q rundt f0)")
plt.xlabel("Frekvens (Hz)")
plt.ylabel("Demping (dB)")
plt.xlim(max(freq.min(), f0*0.2), min(freq.max(), f0*5))
plt.grid(True, which="both", linewidth=0.7)
plt.legend()
plt.tight_layout()

# Skriv ut resultater
print(f"Brukt f0 = {f0:.2f} Hz, mag(f0) = {mag_f0:.2f} dB")
if bandwidth is not None:
    print(f"Båndbredde (‑3 dB): {bandwidth:.2f} Hz")
    print(f"Q-faktor: {Q:.3f}")
    txt = f"f0 = {f0:.1f} Hz\nBW = {bandwidth:.1f} Hz\nQ = {Q:.2f}"
    plt.gca().text(0.02, 0.02, txt, transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.8), fontsize=9)
else:
    print("Kunne ikke finne begge -3 dB-kryss for beregning av BW/Q rundt f0.")

plt.show()