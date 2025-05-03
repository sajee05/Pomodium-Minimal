import numpy as np
from scipy.io import wavfile

# Generate a simple beep sound
sample_rate = 44100
duration = 0.5
t = np.linspace(0, duration, int(sample_rate * duration))
frequency = 440  # A4 note
beep = np.sin(2 * np.pi * frequency * t)

# Add fade in/out
fade_duration = 0.1
fade_length = int(fade_duration * sample_rate)
fade_in = np.linspace(0, 1, fade_length)
fade_out = np.linspace(1, 0, fade_length)
beep[:fade_length] *= fade_in
beep[-fade_length:] *= fade_out

# Normalize and convert to 16-bit integer
beep = np.int16(beep * 32767)

# Save as WAV file
wavfile.write('complete.wav', sample_rate, beep)
