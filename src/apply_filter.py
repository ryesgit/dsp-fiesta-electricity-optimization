import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
import argparse
import os

# Constants
FS = 1000  # Sampling frequency (Hz)

def design_lowpass_filter(cutoff_freq, fs, order=4):
    """Design a Butterworth low-pass filter.
    
    Args:
        cutoff_freq: Cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order (default: 4)
        
    Returns:
        Tuple of (b, a) filter coefficients
    """
    nyquist = fs / 2
    normalized_cutoff = cutoff_freq / nyquist
    b, a = signal.butter(order, normalized_cutoff, btype='low', analog=False)
    return b, a

def apply_filter(data, b, a):
    """Apply filter to signal data.
    
    Args:
        data: Input signal array
        b, a: Filter coefficients
        
    Returns:
        Filtered signal array
    """
    # Use filtfilt for zero-phase filtering (no phase distortion)
    filtered = signal.filtfilt(b, a, data)
    return filtered

def filter_signal(df, cutoff_freq=200, order=4):
    """Filter voltage and current signals in a DataFrame.
    
    Args:
        df: DataFrame with 'time', 'voltage', 'current' columns
        cutoff_freq: Cutoff frequency in Hz (default: 200 Hz)
        order: Filter order (default: 4)
        
    Returns:
        DataFrame with original and filtered signals
    """
    # Calculate sampling frequency from data
    if len(df) < 2:
        raise ValueError("DataFrame must contain at least 2 samples")
    
    time_diff = df['time'].iloc[1] - df['time'].iloc[0]
    fs = 1 / time_diff if time_diff > 0 else FS
    
    # Design filter
    b, a = design_lowpass_filter(cutoff_freq, fs, order)
    
    # Apply filter to voltage and current
    df_filtered = df.copy()
    df_filtered['voltage_filtered'] = apply_filter(df['voltage'].values, b, a)
    df_filtered['current_filtered'] = apply_filter(df['current'].values, b, a)
    
    return df_filtered

def plot_comparison(df, title="Signal Filtering Comparison", save_path=None):
    """Plot original vs filtered signals.
    
    Args:
        df: DataFrame with original and filtered signals
        title: Plot title
        save_path: Optional path to save the plot
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Voltage - Before
    axes[0, 0].plot(df['time'], df['voltage'], 'b-', linewidth=0.5, alpha=0.7)
    axes[0, 0].set_xlabel('Time (s)')
    axes[0, 0].set_ylabel('Voltage (V)')
    axes[0, 0].set_title('Voltage - Before Filtering')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Voltage - After
    axes[0, 1].plot(df['time'], df['voltage_filtered'], 'b-', linewidth=0.8)
    axes[0, 1].set_xlabel('Time (s)')
    axes[0, 1].set_ylabel('Voltage (V)')
    axes[0, 1].set_title('Voltage - After Filtering')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Current - Before
    axes[1, 0].plot(df['time'], df['current'], 'r-', linewidth=0.5, alpha=0.7)
    axes[1, 0].set_xlabel('Time (s)')
    axes[1, 0].set_ylabel('Current (A)')
    axes[1, 0].set_title('Current - Before Filtering')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Current - After
    axes[1, 1].plot(df['time'], df['current_filtered'], 'r-', linewidth=0.8)
    axes[1, 1].set_xlabel('Time (s)')
    axes[1, 1].set_ylabel('Current (A)')
    axes[1, 1].set_title('Current - After Filtering')
    axes[1, 1].grid(True, alpha=0.3)
    
    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    
    return fig

def plot_overlay(df, title="Signal Filtering - Overlay Comparison", save_path=None):
    """Plot original and filtered signals overlaid.
    
    Args:
        df: DataFrame with original and filtered signals
        title: Plot title
        save_path: Optional path to save the plot
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Voltage overlay
    ax1.plot(df['time'], df['voltage'], 'b-', linewidth=0.5, alpha=0.5, label='Original (Noisy)')
    ax1.plot(df['time'], df['voltage_filtered'], 'g-', linewidth=1.2, label='Filtered (Clean)')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Voltage (V)')
    ax1.set_title('Voltage - Before vs After Filtering')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Current overlay
    ax2.plot(df['time'], df['current'], 'r-', linewidth=0.5, alpha=0.5, label='Original (Noisy)')
    ax2.plot(df['time'], df['current_filtered'], 'g-', linewidth=1.2, label='Filtered (Clean)')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Current (A)')
    ax2.set_title('Current - Before vs After Filtering')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    
    return fig

def main():
    parser = argparse.ArgumentParser(
        description='Apply digital low-pass filter to electrical signals'
    )
    parser.add_argument(
        'filepath',
        type=str,
        help='Path to CSV file containing signal data (time, voltage, current)'
    )
    parser.add_argument(
        '--cutoff',
        type=float,
        default=200,
        help='Cutoff frequency in Hz (default: 200 Hz)'
    )
    parser.add_argument(
        '--order',
        type=int,
        default=4,
        help='Filter order (default: 4)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Save filtered data to CSV file (e.g., data/normal_load_filtered.csv)'
    )
    parser.add_argument(
        '--plot',
        type=str,
        choices=['comparison', 'overlay', 'both'],
        default='both',
        help='Type of plot to generate (default: both)'
    )
    parser.add_argument(
        '--save-plot',
        type=str,
        default=None,
        help='Save plot to file (e.g., output.png)'
    )
    parser.add_argument(
        '--time-range',
        type=float,
        nargs=2,
        metavar=('START', 'END'),
        help='Time range to plot in seconds (e.g., --time-range 0 2)'
    )
    
    args = parser.parse_args()
    
    # Load signal data
    print(f"Loading signal data from: {args.filepath}")
    if not os.path.exists(args.filepath):
        raise FileNotFoundError(f"File not found: {args.filepath}")
    
    df = pd.read_csv(args.filepath)
    print(f"Loaded {len(df)} samples")
    
    # Apply filter
    print(f"Applying low-pass filter (cutoff={args.cutoff} Hz, order={args.order})...")
    df_filtered = filter_signal(df, cutoff_freq=args.cutoff, order=args.order)
    print("Filtering complete!")
    
    # Calculate noise reduction
    voltage_noise_before = np.std(df['voltage'] - df_filtered['voltage_filtered'])
    current_noise_before = np.std(df['current'] - df_filtered['current_filtered'])
    print(f"\nNoise Reduction:")
    print(f"  Voltage noise std dev: {voltage_noise_before:.4f} V")
    print(f"  Current noise std dev: {current_noise_before:.4f} A")
    
    # Save filtered data if requested
    if args.output:
        df_filtered.to_csv(args.output, index=False)
        print(f"\nFiltered data saved to: {args.output}")
    
    # Filter time range if specified
    df_plot = df_filtered
    if args.time_range:
        start, end = args.time_range
        df_plot = df_filtered[(df_filtered['time'] >= start) & (df_filtered['time'] <= end)]
        print(f"Plotting time range [{start}, {end}] s: {len(df_plot)} samples")
    
    # Generate plots
    if args.plot in ['comparison', 'both']:
        save_path = args.save_plot if args.plot == 'comparison' else None
        if args.plot == 'both' and args.save_plot:
            # Add suffix for comparison plot
            base, ext = os.path.splitext(args.save_plot)
            save_path = f"{base}_comparison{ext}"
        
        plot_comparison(df_plot, save_path=save_path)
    
    if args.plot in ['overlay', 'both']:
        save_path = args.save_plot if args.plot == 'overlay' else None
        if args.plot == 'both' and args.save_plot:
            # Add suffix for overlay plot
            base, ext = os.path.splitext(args.save_plot)
            save_path = f"{base}_overlay{ext}"
        
        plot_overlay(df_plot, save_path=save_path)
    
    # Show plots if not saving
    if not args.save_plot:
        plt.show()

if __name__ == "__main__":
    main()
