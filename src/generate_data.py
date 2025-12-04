import numpy as np
import pandas as pd
import os

# Constants
FS = 1000  # Sampling frequency (Hz)
DURATION = 10  # Duration in seconds
FREQ = 50  # Power frequency (Hz)
VOLTAGE_RMS = 230
CURRENT_RMS_NORMAL = 5
NOISE_LEVEL = 0.05

def generate_time_vector(duration, fs):
    return np.linspace(0, duration, int(duration * fs), endpoint=False)

def generate_sine_wave(t, rms, freq, phase=0):
    amplitude = rms * np.sqrt(2)
    return amplitude * np.sin(2 * np.pi * freq * t + phase)

def add_noise(signal, noise_level):
    noise = np.random.normal(0, noise_level, len(signal))
    return signal + noise

def generate_normal_load():
    t = generate_time_vector(DURATION, FS)
    
    # Voltage: Pure sine wave
    voltage = generate_sine_wave(t, VOLTAGE_RMS, FREQ)
    voltage = add_noise(voltage, VOLTAGE_RMS * 0.01)
    
    # Current: Linear load, slightly lagging
    current = generate_sine_wave(t, CURRENT_RMS_NORMAL, FREQ, phase=-0.1)
    current = add_noise(current, CURRENT_RMS_NORMAL * NOISE_LEVEL)
    
    df = pd.DataFrame({'time': t, 'voltage': voltage, 'current': current})
    return df

def generate_illegal_tap():
    t = generate_time_vector(DURATION, FS)
    
    # Voltage: Mostly stable, slight dip during heavy load
    voltage = generate_sine_wave(t, VOLTAGE_RMS, FREQ)
    
    # Current: Normal initially, then tapping starts
    current = generate_sine_wave(t, CURRENT_RMS_NORMAL, FREQ, phase=-0.1)
    
    # Simulate tapping starting at t=3s
    tap_start_idx = int(3 * FS)
    tap_current_rms = 10  # Additional load
    
    # Tapping signal with harmonics (simulating non-linear load like electronics)
    tap_signal = generate_sine_wave(t, tap_current_rms, FREQ, phase=-0.1)
    tap_signal += 0.2 * generate_sine_wave(t, tap_current_rms, 3 * FREQ)  # 3rd harmonic
    tap_signal += 0.1 * generate_sine_wave(t, tap_current_rms, 5 * FREQ)  # 5th harmonic
    
    # Apply tapping
    current[tap_start_idx:] += tap_signal[tap_start_idx:]
    
    # Add noise
    voltage = add_noise(voltage, VOLTAGE_RMS * 0.01)
    current = add_noise(current, CURRENT_RMS_NORMAL * NOISE_LEVEL)
    
    df = pd.DataFrame({'time': t, 'voltage': voltage, 'current': current})
    return df

def main():
    os.makedirs('data', exist_ok=True)
    
    print("Generating normal load data...")
    normal_df = generate_normal_load()
    normal_df.to_csv('data/normal_load.csv', index=False)
    print(f"Saved data/normal_load.csv ({len(normal_df)} rows)")
    
    print("Generating illegal tap data...")
    tap_df = generate_illegal_tap()
    tap_df.to_csv('data/illegal_tap.csv', index=False)
    print(f"Saved data/illegal_tap.csv ({len(tap_df)} rows)")

if __name__ == "__main__":
    main()
