import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

# Constants
FS = 1000  # Sampling frequency (Hz) - same as in generate_data.py
MAX_PEAK_ANNOTATIONS = 5  # Maximum number of peaks to annotate in frequency plots
FREQ_TOLERANCE_MULTIPLIER = 2  # Multiplier for frequency tolerance in harmonic detection

def load_signal(filepath):
    """Load signal data from CSV file.
    
    Args:
        filepath: Path to CSV file containing time, voltage, and current columns
        
    Returns:
        pandas DataFrame with signal data
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    df = pd.read_csv(filepath)
    
    # Validate required columns
    required_cols = ['time', 'voltage', 'current']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"CSV must contain columns: {required_cols}")
    
    return df

def compute_fft(signal, fs):
    """Compute FFT of a signal.
    
    Args:
        signal: Input signal (numpy array or pandas Series)
        fs: Sampling frequency in Hz
        
    Returns:
        Tuple of (frequencies, magnitude spectrum)
    """
    # Convert to numpy array if pandas Series
    if isinstance(signal, pd.Series):
        signal = signal.values
    
    # Compute FFT
    n = len(signal)
    fft_result = np.fft.fft(signal)
    
    # Compute magnitude spectrum (only positive frequencies)
    magnitude = np.abs(fft_result)
    
    # Compute frequency bins
    frequencies = np.fft.fftfreq(n, 1/fs)
    
    # Return only positive frequencies
    positive_freq_idx = frequencies >= 0
    frequencies = frequencies[positive_freq_idx]
    magnitude = magnitude[positive_freq_idx]
    
    # Normalize magnitude (divide by n for proper scaling)
    magnitude = magnitude / n * 2  # *2 to account for negative frequencies
    magnitude[0] = magnitude[0] / 2  # DC component should not be doubled
    
    return frequencies, magnitude

def plot_frequency_spectrum(df, signal_type='voltage', title="Frequency Spectrum", 
                            xlim=None, save_path=None):
    """Plot frequency spectrum of a signal.
    
    Args:
        df: DataFrame containing signal data
        signal_type: Type of signal to analyze ('voltage' or 'current')
        title: Plot title
        xlim: X-axis limits (max frequency to display)
        save_path: Path to save the plot (if None, displays instead)
    """
    # Calculate sampling frequency from data
    time_diff = df['time'].iloc[1] - df['time'].iloc[0]
    fs = 1 / time_diff if time_diff > 0 else FS
    
    # Compute FFT
    frequencies, magnitude = compute_fft(df[signal_type], fs)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(frequencies, magnitude, 'b-', linewidth=0.8)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Magnitude')
    ax.set_title(f'{title} - {signal_type.capitalize()}')
    ax.grid(True, alpha=0.3)
    
    # Set x-axis limit if specified
    if xlim:
        ax.set_xlim([0, xlim])
    else:
        # Default: show up to 500 Hz for better visualization
        ax.set_xlim([0, 500])
    
    plt.tight_layout()
    
    # Save or display
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    else:
        plt.show()
    
    return fig

def compare_spectra(normal_df, illegal_df, signal_type='current', xlim=300, save_path=None):
    """Compare frequency spectra of normal load vs illegal tap signals.
    
    Args:
        normal_df: DataFrame with normal load signal data
        illegal_df: DataFrame with illegal tap signal data
        signal_type: Type of signal to analyze ('voltage' or 'current')
        xlim: Maximum frequency to display
        save_path: Path to save the plot (if None, displays instead)
    """
    # Calculate sampling frequency
    time_diff = normal_df['time'].iloc[1] - normal_df['time'].iloc[0]
    fs = 1 / time_diff if time_diff > 0 else FS
    
    # Compute FFT for both signals
    freq_normal, mag_normal = compute_fft(normal_df[signal_type], fs)
    freq_illegal, mag_illegal = compute_fft(illegal_df[signal_type], fs)
    
    # Create comparison plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Plot normal load spectrum
    ax1.plot(freq_normal, mag_normal, 'b-', linewidth=0.8, label='Normal Load')
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('Magnitude')
    ax1.set_title(f'Normal Load - {signal_type.capitalize()} Frequency Spectrum')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, xlim])
    ax1.legend()
    
    # Annotate fundamental frequency and harmonics for normal load
    # Find peaks above a threshold
    threshold = 0.1 * np.max(mag_normal)
    peaks_idx = np.where(mag_normal > threshold)[0]
    for idx in peaks_idx[:MAX_PEAK_ANNOTATIONS]:  # Annotate top peaks
        if freq_normal[idx] > 0:
            ax1.annotate(f'{freq_normal[idx]:.0f} Hz', 
                        xy=(freq_normal[idx], mag_normal[idx]),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=8, color='darkblue')
    
    # Plot illegal tap spectrum
    ax2.plot(freq_illegal, mag_illegal, 'r-', linewidth=0.8, label='Illegal Tap')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Magnitude')
    ax2.set_title(f'Illegal Tap - {signal_type.capitalize()} Frequency Spectrum (with Harmonic Distortion)')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, xlim])
    ax2.legend()
    
    # Annotate fundamental frequency and harmonics for illegal tap
    threshold = 0.1 * np.max(mag_illegal)
    peaks_idx = np.where(mag_illegal > threshold)[0]
    for idx in peaks_idx[:MAX_PEAK_ANNOTATIONS]:  # Annotate top peaks
        if freq_illegal[idx] > 0:
            ax2.annotate(f'{freq_illegal[idx]:.0f} Hz', 
                        xy=(freq_illegal[idx], mag_illegal[idx]),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=8, color='darkred')
    
    fig.suptitle(f'Spectral Comparison: Normal Load vs Illegal Tap\nSampling Frequency (fs) = {fs:.0f} Hz',
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    # Save or display
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    else:
        plt.show()
    
    return fig

def _get_ordinal_suffix(n):
    """Get ordinal suffix for a number (st, nd, rd, th).
    
    Args:
        n: Integer number
        
    Returns:
        Ordinal suffix string ('st', 'nd', 'rd', or 'th')
    """
    # Special case for numbers ending in 11, 12, 13 (e.g., 11th, 12th, 13th)
    if 10 <= n % 100 <= 13:
        return 'th'
    
    # Regular cases based on last digit
    last_digit = n % 10
    if last_digit == 1:
        return 'st'
    elif last_digit == 2:
        return 'nd'
    elif last_digit == 3:
        return 'rd'
    else:
        return 'th'

def analyze_harmonics(df, signal_type='current', fundamental_freq=50):
    """Analyze and display harmonic content using pandas DataFrame.
    
    Args:
        df: DataFrame with signal data
        signal_type: Type of signal to analyze ('voltage' or 'current')
        fundamental_freq: Fundamental frequency in Hz (default: 50 Hz)
        
    Returns:
        DataFrame with harmonic analysis results
    """
    # Calculate sampling frequency
    time_diff = df['time'].iloc[1] - df['time'].iloc[0]
    fs = 1 / time_diff if time_diff > 0 else FS
    
    # Compute FFT
    frequencies, magnitude = compute_fft(df[signal_type], fs)
    
    # Get fundamental magnitude for percentage calculation
    fundamental_idx = np.argmin(np.abs(frequencies - fundamental_freq))
    fundamental_magnitude = magnitude[fundamental_idx]
    
    # Find harmonics (fundamental, 2nd, 3rd, 4th, 5th, etc.)
    harmonics_data = []
    n_samples = len(frequencies)
    freq_tolerance = fs / n_samples  # Frequency resolution
    
    for harmonic_num in range(1, 11):  # Analyze up to 10th harmonic
        harmonic_freq = fundamental_freq * harmonic_num
        
        # Find the closest frequency bin
        freq_idx = np.argmin(np.abs(frequencies - harmonic_freq))
        
        if np.abs(frequencies[freq_idx] - harmonic_freq) < freq_tolerance * FREQ_TOLERANCE_MULTIPLIER:
            harmonic_magnitude = magnitude[freq_idx]
            magnitude_percent = (harmonic_magnitude / fundamental_magnitude) * 100 if harmonic_num > 1 else 100
            
            harmonics_data.append({
                'Harmonic': f'{harmonic_num}{_get_ordinal_suffix(harmonic_num)}',
                'Frequency (Hz)': frequencies[freq_idx],
                'Magnitude': harmonic_magnitude,
                'Magnitude (%)': magnitude_percent
            })
    
    # Create DataFrame
    harmonics_df = pd.DataFrame(harmonics_data)
    
    return harmonics_df

def main():
    parser = argparse.ArgumentParser(
        description='Perform FFT and frequency-domain analysis on electrical signals'
    )
    parser.add_argument(
        'filepath',
        type=str,
        help='Path to CSV file containing signal data (time, voltage, current)'
    )
    parser.add_argument(
        '--signal',
        type=str,
        choices=['voltage', 'current'],
        default='current',
        help='Type of signal to analyze (default: current)'
    )
    parser.add_argument(
        '--compare',
        type=str,
        default=None,
        help='Path to second CSV file for comparison (e.g., normal vs illegal tap)'
    )
    parser.add_argument(
        '--xlim',
        type=float,
        default=300,
        help='Maximum frequency to display in Hz (default: 300)'
    )
    parser.add_argument(
        '--save',
        type=str,
        default=None,
        help='Save plot to file instead of displaying (e.g., spectrum.png)'
    )
    parser.add_argument(
        '--show-harmonics',
        action='store_true',
        help='Display harmonic analysis table using pandas'
    )
    
    args = parser.parse_args()
    
    # Load signal data
    print(f"Loading signal data from: {args.filepath}")
    df = load_signal(args.filepath)
    print(f"Loaded {len(df)} samples")
    
    if args.compare:
        # Comparison mode
        print(f"\nLoading comparison data from: {args.compare}")
        df_compare = load_signal(args.compare)
        print(f"Loaded {len(df_compare)} samples for comparison")
        
        print(f"\nComparing {args.signal} frequency spectra...")
        compare_spectra(df, df_compare, signal_type=args.signal, 
                       xlim=args.xlim, save_path=args.save)
        
        # Show harmonics analysis for both signals if requested
        if args.show_harmonics:
            print(f"\n{'='*60}")
            print(f"Harmonic Analysis - File 1: {args.filepath}")
            print(f"{'='*60}")
            harmonics_df1 = analyze_harmonics(df, signal_type=args.signal)
            print(harmonics_df1.to_string(index=False))
            
            print(f"\n{'='*60}")
            print(f"Harmonic Analysis - File 2: {args.compare}")
            print(f"{'='*60}")
            harmonics_df2 = analyze_harmonics(df_compare, signal_type=args.signal)
            print(harmonics_df2.to_string(index=False))
    else:
        # Single file analysis
        print(f"\nComputing FFT for {args.signal}...")
        plot_frequency_spectrum(df, signal_type=args.signal, 
                               title=f"Frequency Spectrum - {args.filepath}",
                               xlim=args.xlim, save_path=args.save)
        
        # Show harmonics analysis if requested
        if args.show_harmonics:
            print(f"\n{'='*60}")
            print(f"Harmonic Analysis - {args.signal.capitalize()}")
            print(f"{'='*60}")
            harmonics_df = analyze_harmonics(df, signal_type=args.signal)
            print(harmonics_df.to_string(index=False))

if __name__ == "__main__":
    main()
