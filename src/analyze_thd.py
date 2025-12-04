import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
from scipy.fft import fft, fftfreq

def calculate_thd(signal, fs, fundamental_freq=50):
    """Calculate Total Harmonic Distortion (THD).
    
    Args:
        signal: Input signal array
        fs: Sampling frequency in Hz
        fundamental_freq: Fundamental frequency in Hz (default: 50)
        
    Returns:
        thd: THD value in percent
        harmonics: List of (frequency, amplitude) tuples for harmonics
        spectrum: Tuple of (frequencies, amplitudes) for the full spectrum
    """
    n = len(signal)
    yf = fft(signal)
    xf = fftfreq(n, 1 / fs)[:n//2]
    
    # Normalize amplitude
    amplitudes = 2.0/n * np.abs(yf[0:n//2])
    
    # Find fundamental frequency index
    # Search around the expected fundamental frequency
    search_window = 5  # Hz
    mask_fund = (xf >= fundamental_freq - search_window) & (xf <= fundamental_freq + search_window)
    indices_fund = np.where(mask_fund)[0]
    
    if len(indices_fund) > 0:
        local_idx_fund = np.argmax(amplitudes[indices_fund])
        idx_fund = indices_fund[local_idx_fund]
    else:
        # Fallback if not found (should not happen with valid signal)
        idx_fund = np.argmin(np.abs(xf - fundamental_freq))
    
    fund_freq = xf[idx_fund]
    fund_amp = amplitudes[idx_fund]
    
    # Calculate harmonics (2nd to 10th)
    harmonic_amps = []
    harmonics = []
    
    for h in range(2, 11):
        target_freq = h * fund_freq
        
        # Skip if target frequency is beyond Nyquist
        if target_freq >= fs / 2:
            continue
            
        # Find peak near target frequency
        # Ensure we don't go out of bounds
        mask = (xf >= target_freq - search_window) & (xf <= target_freq + search_window)
        if not np.any(mask):
            continue
            
        idx_harm = np.argmax(mask)
        # argmax returns index relative to the full array if mask is boolean array of same shape
        # But here we need to be careful. Let's use where to get indices.
        indices = np.where(mask)[0]
        if len(indices) == 0:
            continue
            
        # Find the index with max amplitude within the window
        local_idx = np.argmax(amplitudes[indices])
        idx_harm = indices[local_idx]
        
        harm_freq = xf[idx_harm]
        harm_amp = amplitudes[idx_harm]
        
        harmonic_amps.append(harm_amp**2)
        harmonics.append((harm_freq, harm_amp))
        
    # Calculate THD
    thd = np.sqrt(sum(harmonic_amps)) / fund_amp * 100
    
    return thd, harmonics, (xf, amplitudes)

def plot_spectrum(xf, yf, harmonics, thd, title="Frequency Spectrum", save_path=None):
    """Plot frequency spectrum and highlight harmonics."""
    plt.figure(figsize=(10, 6))
    plt.plot(xf, yf, 'b-', linewidth=0.8, label='Spectrum')
    
    # Highlight harmonics
    harm_freqs = [h[0] for h in harmonics]
    harm_amps = [h[1] for h in harmonics]
    plt.plot(harm_freqs, harm_amps, 'ro', markersize=5, label='Harmonics')
    
    plt.xlim(0, 500)  # Show up to 500 Hz (10th harmonic)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.title(f'{title}\nTHD = {thd:.2f}%')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    else:
        plt.show()

def main():
    parser = argparse.ArgumentParser(description='Analyze Total Harmonic Distortion (THD)')
    parser.add_argument('filepath', type=str, help='Path to CSV file')
    parser.add_argument('--col', type=str, default='current', help='Column to analyze (default: current)')
    parser.add_argument('--fs', type=float, default=1000, help='Sampling frequency (default: 1000 Hz)')
    parser.add_argument('--freq', type=float, default=50, help='Fundamental frequency (default: 50 Hz)')
    parser.add_argument('--save-plot', type=str, default=None, help='Save spectrum plot to file')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.filepath):
        raise FileNotFoundError(f"File not found: {args.filepath}")
    
    df = pd.read_csv(args.filepath)
    signal = df[args.col].values
    
    # If sampling frequency is not provided, try to calculate it
    if 'time' in df.columns:
        time_diff = df['time'].iloc[1] - df['time'].iloc[0]
        fs = 1 / time_diff if time_diff > 0 else args.fs
    else:
        fs = args.fs
        
    print(f"Analyzing {args.col} signal from {args.filepath} (fs={fs:.0f} Hz)...")
    
    thd, harmonics, (xf, yf) = calculate_thd(signal, fs, args.freq)
    
    print(f"Fundamental Frequency: {args.freq} Hz")
    print(f"THD: {thd:.2f}%")
    print("Harmonics:")
    for i, (freq, amp) in enumerate(harmonics):
        print(f"  {i+2}nd Harmonic ({freq:.1f} Hz): {amp:.4f}")
        
    if args.save_plot:
        plot_spectrum(xf, yf, harmonics, thd, title=f"Spectrum of {args.col} ({os.path.basename(args.filepath)})", save_path=args.save_plot)

if __name__ == "__main__":
    main()
