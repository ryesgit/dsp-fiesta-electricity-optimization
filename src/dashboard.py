import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
import argparse
import os
import sys

# Add src to path to import analyze_thd and detect_anomaly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyze_thd import calculate_thd
from detect_anomaly import extract_features, detect_anomaly

class DSPDashboard:
    def __init__(self, filepath, window_size=0.1, refresh_rate=50):
        self.filepath = filepath
        self.window_size = window_size  # seconds
        self.refresh_rate = refresh_rate  # ms
        
        # Load data
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        self.df = pd.read_csv(filepath)
        
        # Calculate sampling frequency
        if 'time' in self.df.columns and len(self.df) > 1:
            time_diff = self.df['time'].iloc[1] - self.df['time'].iloc[0]
            self.fs = 1 / time_diff if time_diff > 0 else 1000
        else:
            self.fs = 1000
            
        self.window_samples = int(self.window_size * self.fs)
        self.current_idx = 0
        self.total_samples = len(self.df)
        
        # Setup plot
        self.setup_plot()
        
    def setup_plot(self):
        self.fig = plt.figure(figsize=(14, 9))
        self.fig.suptitle("DSP Fiesta - Real-Time Power Monitoring Dashboard", fontsize=16, fontweight='bold')
        
        gs = GridSpec(2, 2, height_ratios=[1, 1])
        
        # Top: Time Domain Waveforms (spanning full width)
        self.ax_time = self.fig.add_subplot(gs[0, :])
        self.line_v, = self.ax_time.plot([], [], 'b-', linewidth=1, label='Voltage (V)')
        self.line_i, = self.ax_time.plot([], [], 'r-', linewidth=1, label='Current (A)')
        self.ax_time.set_title('Live Time-Domain Waveforms')
        self.ax_time.set_xlabel('Time (s)')
        self.ax_time.set_ylabel('Amplitude')
        self.ax_time.grid(True, alpha=0.3)
        self.ax_time.legend(loc='upper right')
        
        # Set fixed y-limits based on data range
        v_max = self.df['voltage'].abs().max() * 1.1
        i_max = self.df['current'].abs().max() * 1.1
        # Use twinx for current to scale it properly if needed, but for simplicity plotting on same axis with different scales is tricky.
        # Let's use a secondary y-axis for current.
        self.ax_time_i = self.ax_time.twinx()
        self.line_i, = self.ax_time_i.plot([], [], 'r-', linewidth=1, label='Current (A)')
        self.ax_time.set_ylim(-v_max, v_max)
        self.ax_time_i.set_ylim(-i_max, i_max)
        self.ax_time_i.set_ylabel('Current (A)', color='r')
        self.ax_time_i.tick_params(axis='y', labelcolor='r')
        
        # Bottom Left: Frequency Spectrum (FFT)
        self.ax_fft = self.fig.add_subplot(gs[1, 0])
        self.line_fft, = self.ax_fft.plot([], [], 'b-', linewidth=0.8)
        self.line_harmonics, = self.ax_fft.plot([], [], 'ro', markersize=5, label='Harmonics')
        self.ax_fft.set_title('Live Frequency Spectrum (Current)')
        self.ax_fft.set_xlabel('Frequency (Hz)')
        self.ax_fft.set_ylabel('Amplitude')
        self.ax_fft.set_xlim(0, 500)  # Show up to 10th harmonic
        self.ax_fft.set_ylim(0, i_max * 0.5) # Initial guess
        self.ax_fft.grid(True, alpha=0.3)
        self.ax_fft.legend()
        
        # Bottom Right: Metrics & Status
        self.ax_metrics = self.fig.add_subplot(gs[1, 1])
        self.ax_metrics.axis('off')
        
        # Text elements
        self.text_v_rms = self.ax_metrics.text(0.1, 0.8, '', fontsize=14)
        self.text_i_rms = self.ax_metrics.text(0.1, 0.7, '', fontsize=14)
        self.text_power = self.ax_metrics.text(0.1, 0.6, '', fontsize=14)
        self.text_thd = self.ax_metrics.text(0.1, 0.5, '', fontsize=14)
        
        # Status Box
        self.status_rect = plt.Rectangle((0.1, 0.1), 0.8, 0.3, color='gray', alpha=0.3)
        self.ax_metrics.add_patch(self.status_rect)
        self.text_status = self.ax_metrics.text(0.5, 0.25, 'INITIALIZING', 
                                              fontsize=20, fontweight='bold', 
                                              ha='center', va='center', color='white')
        
    def update(self, frame):
        # Update index (looping)
        start_idx = self.current_idx
        end_idx = start_idx + self.window_samples
        
        if end_idx >= self.total_samples:
            # Loop back or stop
            self.current_idx = 0
            start_idx = 0
            end_idx = self.window_samples
            
        # Get data chunk
        chunk = self.df.iloc[start_idx:end_idx]
        t = chunk['time'].values
        v = chunk['voltage'].values
        i = chunk['current'].values
        
        # Update Time Plot
        self.line_v.set_data(t, v)
        self.line_i.set_data(t, i)
        self.ax_time.set_xlim(t[0], t[-1])
        
        # Extract Features & Detect Anomaly
        # Create a mini-dataframe for the feature extraction function
        chunk_df = pd.DataFrame({'voltage': v, 'current': i})
        features = extract_features(chunk_df, self.fs)
        
        # Detect Anomaly
        is_anomaly, reason = detect_anomaly(features, thd_threshold=5.0)
        
        # Update Metrics Text
        self.text_v_rms.set_text(f"Voltage RMS: {features['v_rms']:.2f} V")
        self.text_i_rms.set_text(f"Current RMS: {features['i_rms']:.2f} A")
        self.text_power.set_text(f"Apparent Power: {features['apparent_power']:.2f} VA")
        self.text_thd.set_text(f"Current THD: {features['thd_current']:.2f}%")
        
        # Update Status Alert
        if is_anomaly:
            self.status_rect.set_color('red')
            self.status_rect.set_alpha(0.8)
            self.text_status.set_text(f"ANOMALY!\n{reason}")
        else:
            self.status_rect.set_color('green')
            self.status_rect.set_alpha(0.8)
            self.text_status.set_text("NORMAL")
            
        # Update FFT Plot
        # Recalculate THD to get spectrum data (re-using logic from analyze_thd would be efficient but let's just call it)
        # Actually extract_features calls calculate_thd but discards spectrum. 
        # Let's call calculate_thd directly here to get spectrum for plotting.
        thd, harmonics, (xf, yf) = calculate_thd(i, self.fs, fundamental_freq=50)
        
        self.line_fft.set_data(xf, yf)
        
        harm_freqs = [h[0] for h in harmonics]
        harm_amps = [h[1] for h in harmonics]
        self.line_harmonics.set_data(harm_freqs, harm_amps)
        
        # Advance index
        step = int(self.refresh_rate / 1000 * self.fs)  # Advance by refresh rate duration
        self.current_idx += step
        
        return self.line_v, self.line_i, self.line_fft, self.line_harmonics, self.text_v_rms, self.text_i_rms, self.text_power, self.text_thd, self.status_rect, self.text_status

    def run(self):
        ani = animation.FuncAnimation(self.fig, self.update, interval=self.refresh_rate, blit=False)
        plt.show()

def main():
    parser = argparse.ArgumentParser(description='Real-Time DSP Visualization Dashboard')
    parser.add_argument('filepath', type=str, help='Path to CSV file (e.g., data/illegal_tap.csv)')
    parser.add_argument('--window', type=float, default=0.1, help='Window size in seconds (default: 0.1)')
    parser.add_argument('--refresh', type=int, default=50, help='Refresh rate in ms (default: 50)')
    
    args = parser.parse_args()
    
    dashboard = DSPDashboard(args.filepath, window_size=args.window, refresh_rate=args.refresh)
    dashboard.run()

if __name__ == "__main__":
    main()
