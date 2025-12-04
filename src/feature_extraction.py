import numpy as np
import pandas as pd
import argparse
import os

# Constants
ANOMALY_THRESHOLD_PERCENT = 50  # Power increase threshold for anomaly detection
DEFAULT_NORMAL_LOAD_PATH = 'data/normal_load.csv'
DEFAULT_ILLEGAL_TAP_PATH = 'data/illegal_tap.csv'

def calculate_rms(signal):
    """Calculate Root Mean Square (RMS) of a signal.
    
    RMS = sqrt(mean(signal²))
    
    Args:
        signal: Array of signal values
        
    Returns:
        RMS value of the signal
    """
    return np.sqrt(np.mean(signal ** 2))

def calculate_power_metrics(voltage, current):
    """Calculate power metrics from voltage and current signals.
    
    Args:
        voltage: Array of voltage values
        current: Array of current values
        
    Returns:
        Dictionary containing:
        - rms_voltage: RMS voltage
        - rms_current: RMS current
        - avg_power: Average power (mean of instantaneous power)
        - instantaneous_power: Array of instantaneous power values
    """
    # Calculate RMS values
    rms_voltage = calculate_rms(voltage)
    rms_current = calculate_rms(current)
    
    # Calculate instantaneous power: P(t) = V(t) × I(t)
    instantaneous_power = voltage * current
    
    # Calculate average power
    avg_power = np.mean(instantaneous_power)
    
    return {
        'rms_voltage': rms_voltage,
        'rms_current': rms_current,
        'avg_power': avg_power,
        'instantaneous_power': instantaneous_power
    }

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

def analyze_signal(filepath, verbose=True):
    """Analyze signal and compute RMS and power metrics.
    
    Args:
        filepath: Path to CSV file containing signal data
        verbose: Whether to print detailed output
        
    Returns:
        Dictionary containing computed metrics
    """
    # Load data
    df = load_signal(filepath)
    
    # Extract voltage and current
    voltage = df['voltage'].values
    current = df['current'].values
    
    # Calculate metrics
    metrics = calculate_power_metrics(voltage, current)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Signal Analysis: {os.path.basename(filepath)}")
        print(f"{'='*60}")
        print(f"Number of samples: {len(df)}")
        print(f"Duration: {df['time'].iloc[-1] - df['time'].iloc[0]:.2f} seconds")
        print(f"\n{'RMS Values':^60}")
        print(f"{'-'*60}")
        print(f"  RMS Voltage:  {metrics['rms_voltage']:>10.2f} V")
        print(f"  RMS Current:  {metrics['rms_current']:>10.2f} A")
        print(f"\n{'Power Metrics':^60}")
        print(f"{'-'*60}")
        print(f"  Average Power: {metrics['avg_power']:>10.2f} W")
        print(f"  Max Power:     {np.max(metrics['instantaneous_power']):>10.2f} W")
        print(f"  Min Power:     {np.min(metrics['instantaneous_power']):>10.2f} W")
        print(f"{'='*60}\n")
    
    return metrics

def main():
    parser = argparse.ArgumentParser(
        description='Extract RMS and power features from electrical signal data'
    )
    parser.add_argument(
        'filepath',
        type=str,
        nargs='?',
        default=None,
        help='Path to CSV file containing signal data (time, voltage, current)'
    )
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare normal load vs illegal tap (requires data/ folder)'
    )
    
    args = parser.parse_args()
    
    if args.compare:
        # Compare both scenarios
        print("\n" + "="*60)
        print("COMPARATIVE ANALYSIS: Normal Load vs Illegal Tap")
        print("="*60)
        
        normal_path = DEFAULT_NORMAL_LOAD_PATH
        tap_path = DEFAULT_ILLEGAL_TAP_PATH
        
        if not os.path.exists(normal_path) or not os.path.exists(tap_path):
            print("\nError: Data files not found.")
            print("Please run generate_data.py from the project root:")
            print("  python src/generate_data.py")
            return
        
        # Analyze normal load
        normal_metrics = analyze_signal(normal_path, verbose=True)
        
        # Analyze illegal tap
        tap_metrics = analyze_signal(tap_path, verbose=True)
        
        # Show comparison
        print(f"\n{'='*60}")
        print(f"{'COMPARISON SUMMARY':^60}")
        print(f"{'='*60}")
        print(f"\n{'Metric':<25} {'Normal':>12} {'Illegal Tap':>12} {'Change':>8}")
        print(f"{'-'*60}")
        
        voltage_change = ((tap_metrics['rms_voltage'] - normal_metrics['rms_voltage']) 
                         / normal_metrics['rms_voltage'] * 100)
        current_change = ((tap_metrics['rms_current'] - normal_metrics['rms_current']) 
                         / normal_metrics['rms_current'] * 100)
        power_change = ((tap_metrics['avg_power'] - normal_metrics['avg_power']) 
                       / normal_metrics['avg_power'] * 100)
        
        print(f"{'RMS Voltage (V)':<25} {normal_metrics['rms_voltage']:>12.2f} "
              f"{tap_metrics['rms_voltage']:>12.2f} {voltage_change:>7.1f}%")
        print(f"{'RMS Current (A)':<25} {normal_metrics['rms_current']:>12.2f} "
              f"{tap_metrics['rms_current']:>12.2f} {current_change:>7.1f}%")
        print(f"{'Average Power (W)':<25} {normal_metrics['avg_power']:>12.2f} "
              f"{tap_metrics['avg_power']:>12.2f} {power_change:>7.1f}%")
        print(f"{'='*60}")
        
        # Highlight the illegal tap detection
        print(f"\n{'DETECTION RESULT':^60}")
        print(f"{'-'*60}")
        if power_change > ANOMALY_THRESHOLD_PERCENT:
            print(f"  ⚠️  ANOMALY DETECTED: Power increased by {power_change:.1f}%")
            print(f"  This indicates potential illegal electricity tapping!")
        else:
            print(f"  ✓ Normal operation detected")
        print(f"{'='*60}\n")
        
    elif args.filepath:
        # Analyze single file
        analyze_signal(args.filepath, verbose=True)
    else:
        print("Error: Please specify a file path or use --compare")
        print("\nUsage:")
        print("  python src/feature_extraction.py data/normal_load.csv")
        print("  python src/feature_extraction.py --compare")

if __name__ == "__main__":
    main()
