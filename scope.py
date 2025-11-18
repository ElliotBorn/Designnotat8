import csv

import matplotlib.pyplot as plt
import numpy as np


def smooth(data, window_size=11):
    if window_size < 3:
        return data
    window = np.ones(window_size) / window_size
    return np.convolve(data, window, mode='same')


def plot_oscilloscope_csv(filename):
    times = []
    ch1 = []
    ch2 = []
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Skip header
        for _ in range(24):    # Skip next 24 lines
            next(reader, None)
        for row in reader:
            if len(row) < 3:
                continue
            times.append(float(row[0]))
            ch1.append(float(row[1]))
            ch2.append(float(row[2]))


    plt.figure(figsize=(10, 6))
    plt.plot(times, ch2, label='Channel 2 (V)')
    plt.plot(times, ch1, label='Channel 1 (V)')
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.title('Oscilloscope Data (4 Perioder, Mean Removed & Smoothed)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

plot_oscilloscope_csv('scopeNoiseogFiltrert2.csv')