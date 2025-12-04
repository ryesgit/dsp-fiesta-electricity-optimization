import numpy as np
import pandas as pd
import argparse
import os
import sys

# Add src to path to import analyze_thd
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyze_thd import calculate_thd

def calculate_rms(signal):
    """Calculate RMS value of a signal."""
    return np.sqrt(np.mean(signal**2))

def extract_features(df, fs=1000):
    """Extract DSP features from voltage and current signals.
    
    Args:
        df: DataFrame with 'voltage' and 'current' columns
        fs: Sampling frequency
        
    Returns:
        Dictionary of features
    """
    voltage = df['voltage'].values
    current = df['current'].values
    
    # RMS
    v_rms = calculate_rms(voltage)
    i_rms = calculate_rms(current)
    
    # Apparent Power
    apparent_power = v_rms * i_rms
    
    # THD (Current)
    # Use 50Hz as fundamental
    thd_current, _, _ = calculate_thd(current, fs, fundamental_freq=50)
    
    return {
        'v_rms': v_rms,
        'i_rms': i_rms,
        'apparent_power': apparent_power,
        'thd_current': thd_current
    }

def detect_anomaly(features, thd_threshold=5.0):
    """Detect anomaly based on features.
    
    Args:
        features: Dictionary of extracted features
        thd_threshold: Threshold for THD in percent
        
    Returns:
        is_anomaly: Boolean
        reason: String explaining the reason
    """
    reasons = []
    is_anomaly = False
    
    # Check THD
    if features['thd_current'] > thd_threshold:
        is_anomaly = True
        reasons.append(f"High THD ({features['thd_current']:.2f}% > {thd_threshold}%)")
        
    # We could add other checks here (e.g., Overcurrent)
    
    if is_anomaly:
        return True, ", ".join(reasons)
    else:
        return False, "Normal"

def main():
    parser = argparse.ArgumentParser(description='Detect anomalies in power signals')
    parser.add_argument('filepath', type=str, help='Path to CSV file')
    parser.add_argument('--thd-threshold', type=float, default=5.0, help='THD threshold in percent (default: 5.0)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.filepath):
        raise FileNotFoundError(f"File not found: {args.filepath}")
    
    df = pd.read_csv(args.filepath)
    
    # Calculate sampling frequency
    if 'time' in df.columns and len(df) > 1:
        time_diff = df['time'].iloc[1] - df['time'].iloc[0]
        fs = 1 / time_diff if time_diff > 0 else 1000
    else:
        fs = 1000
        
    print(f"Analyzing {args.filepath}...")
    
    # Extract features
    features = extract_features(df, fs)
    
    print("\nExtracted Features:")
    print(f"  Voltage RMS: {features['v_rms']:.2f} V")
    print(f"  Current RMS: {features['i_rms']:.2f} A")
    print(f"  Apparent Power: {features['apparent_power']:.2f} VA")
    print(f"  Current THD: {features['thd_current']:.2f}%")
    
    # Detect anomaly
    is_anomaly, reason = detect_anomaly(features, thd_threshold=args.thd_threshold)
    
    print("\nClassification Result:")
    if is_anomaly:
        print(f"  🔴 ANOMALY DETECTED: {reason}")
    else:
        print(f"  🟢 NORMAL: {reason}")

if __name__ == "__main__":
    main()
