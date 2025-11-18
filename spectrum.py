import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator

filnavn = "spectrumNoiseOgFiltrert.csv"
df = pd.read_csv(filnavn, skiprows=0)
df.columns = [col.strip() for col in df.columns]

# finn frekvens-kolonne
freq_col = next((c for c in df.columns if 'freq' in c.lower()), df.columns[0])
frekvens = pd.to_numeric(df[freq_col], errors='coerce')

# finn alle trace-kolonner (fall back hvis ingen)
trace_cols = [c for c in df.columns if 'trace 2' in c.lower()]

if not trace_cols:
    # prøv kolonner som kan være signal hvis ingen 'trace'
    possible = [c for c in df.columns if c != freq_col]
    trace_cols = possible[:2] if possible else [df.columns[0]]

# klipp bort ikke-positive eller NaN frekvenser (bruk samme mask for alle traces)
mask = frekvens > 0
frekvens = frekvens[mask]

plt.figure(figsize=(12, 6))

for col in trace_cols:
    raw = pd.to_numeric(df[col], errors='coerce')[mask]
    # hvis kolonnenavnet inneholder 'db' antar vi den allerede er i dB
    already_db = 'db' in col.lower()
    if already_db:
        y_db = raw
        ylabel_extra = ' (dB)'
    else:
        # konverter lineær RMS (V) til dB (dBV) med referanse 1 V
        y_lin = raw.clip(lower=1e-12)
        y_db = 20 * np.log10(y_lin / 1.0)
        ylabel_extra = ' (dBV)'

    plt.plot(frekvens, y_db, linewidth=1, label=f"{col}{ylabel_extra}")

#plt.axvline(x=1160, color='red', linestyle='--', label='f_0 = 1160 Hz')
plt.xscale('log')
plt.xlabel('Frekvens [Hz]')
plt.ylabel('Amplitude [dB]')
plt.title('Spektrumanalyse – Frekvens vs Amplitude (dB)')
plt.grid(True, which='both', ls=':')
ax = plt.gca()
ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=15))
ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs='auto', numticks=100))
ax.xaxis.set_minor_formatter(plt.NullFormatter())
plt.legend()
plt.tight_layout()
plt.show()