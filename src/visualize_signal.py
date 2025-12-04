import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

# Constants
FS = 1000  # Sampling frequency (Hz) - same as in generate_data.py

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
    
    # Validate minimum data size
    if len(df) < 2:
        raise ValueError(f"CSV must contain at least 2 samples, found {len(df)}")
    
    return df

def calculate_sampling_frequency(df):
    """Calculate sampling frequency from time data.
    
    Args:
        df: DataFrame with time column
        
    Returns:
        Calculated sampling frequency in Hz
    """
    if len(df) < 2:
        return FS
    
    time_diff = df['time'].iloc[1] - df['time'].iloc[0]
    return 1 / time_diff if time_diff > 0 else FS

def plot_signal(df, title="Electrical Signal Waveform", show_fs=True):
    """Plot voltage and current signals in time domain.
    
    Args:
        df: DataFrame containing time, voltage, and current data
        title: Plot title
        show_fs: Whether to display sampling frequency in the plot
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Plot voltage
    ax1.plot(df['time'], df['voltage'], 'b-', linewidth=0.5, label='Voltage')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Voltage (V)')
    ax1.set_title(f'{title} - Voltage')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot current
    ax2.plot(df['time'], df['current'], 'r-', linewidth=0.5, label='Current')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Current (A)')
    ax2.set_title(f'{title} - Current')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Display sampling frequency if requested
    if show_fs:
        # Calculate actual sampling frequency from data
        calculated_fs = calculate_sampling_frequency(df)
        
        fig.suptitle(f'{title}\nSampling Frequency (fs) = {calculated_fs:.0f} Hz', 
                     fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig

def main():
    parser = argparse.ArgumentParser(
        description='Load and visualize electrical signal waveforms in time domain'
    )
    parser.add_argument(
        'filepath',
        type=str,
        help='Path to CSV file containing signal data (time, voltage, current)'
    )
    parser.add_argument(
        '--title',
        type=str,
        default='Electrical Signal Waveform',
        help='Title for the plot (default: "Electrical Signal Waveform")'
    )
    parser.add_argument(
        '--save',
        type=str,
        default=None,
        help='Save plot to file instead of displaying (e.g., output.png)'
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
    df = load_signal(args.filepath)
    print(f"Loaded {len(df)} samples")
    
    # Filter time range if specified
    if args.time_range:
        start, end = args.time_range
        df = df[(df['time'] >= start) & (df['time'] <= end)]
        print(f"Filtered to time range [{start}, {end}] s: {len(df)} samples")
        
        # Validate filtered data is not empty
        if len(df) == 0:
            raise ValueError(f"No data found in time range [{start}, {end}] s")
        if len(df) < 2:
            raise ValueError(f"Insufficient data in time range [{start}, {end}] s (need at least 2 samples)")
    
    # Display sampling frequency
    calculated_fs = calculate_sampling_frequency(df)
    print(f"Sampling Frequency (fs) = {calculated_fs:.0f} Hz")
    
    # Plot signal
    fig = plot_signal(df, title=args.title, show_fs=True)
    
    # Save or display
    if args.save:
        fig.savefig(args.save, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {args.save}")
    else:
        plt.show()

if __name__ == "__main__":
    main()
