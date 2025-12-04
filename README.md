# DSP Fiesta Power Monitoring System

A Digital Signal Processing (DSP)-based power monitoring and anomaly detection system.

## Overview
This project analyzes voltage and current waveforms using core DSP techniques to identify abnormal power usage and illegal electricity tapping.

## Setup
1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Data Generation
To generate synthetic power signal datasets (normal load and illegal tapping scenarios):
```bash
python src/generate_data.py
```
This will create the following files in the `data/` directory:
- `normal_load.csv`: Simulated normal power usage.
- `illegal_tap.csv`: Simulated illegal tapping with amplitude changes and harmonic distortion.

## Signal Visualization
To visualize electrical signal waveforms in the time domain:

### Basic Usage
```bash
python src/visualize_signal.py data/normal_load.csv
```

### Advanced Options
```bash
# Save plot to file
python src/visualize_signal.py data/normal_load.csv --save output.png

# Visualize specific time range (e.g., 0-2 seconds)
python src/visualize_signal.py data/illegal_tap.csv --time-range 0 2

# Custom title
python src/visualize_signal.py data/illegal_tap.csv --title "Illegal Tap Detection"

# Combined options
python src/visualize_signal.py data/illegal_tap.csv --time-range 2 5 --save tap_analysis.png --title "Tap Event (2-5s)"
```

### Features
- **Time-Domain Visualization**: Plots both voltage and current waveforms against time
- **Sampling Frequency Display**: Shows the sampling frequency (fs = 1000 Hz) in the plot
- **Clear Transitions**: Time-domain transitions are clearly visible (e.g., illegal tap starting at t=3s)
- **Flexible Time Range**: Zoom into specific time intervals for detailed analysis

## FFT & Frequency-Domain Analysis
Transform time-domain signals into frequency domain using Fast Fourier Transform (FFT) to identify harmonic content and spectral distortion.

### Basic Usage
```bash
# Analyze frequency spectrum of a single signal
python src/fft_analysis.py data/normal_load.csv
```

### Advanced Options
```bash
# Analyze voltage signal (default is current)
python src/fft_analysis.py data/normal_load.csv --signal voltage

# Compare normal load vs illegal tap spectra
python src/fft_analysis.py data/normal_load.csv --compare data/illegal_tap.csv

# Display harmonic analysis table using pandas
python src/fft_analysis.py data/illegal_tap.csv --show-harmonics

# Set frequency range limit (e.g., 0-500 Hz)
python src/fft_analysis.py data/illegal_tap.csv --xlim 500

# Save plot to file
python src/fft_analysis.py data/normal_load.csv --compare data/illegal_tap.csv --save spectrum_comparison.png

# Combined: Compare with harmonics table
python src/fft_analysis.py data/normal_load.csv --compare data/illegal_tap.csv --show-harmonics --xlim 300
```

### Features
- **FFT Computation**: Computes Fast Fourier Transform of voltage/current signals
- **Frequency Spectrum Plotting**: Visualizes magnitude spectrum with frequency bins
- **Harmonic Analysis**: Identifies and quantifies fundamental frequency (50 Hz) and harmonics using pandas DataFrames
- **Spectral Comparison**: Side-by-side comparison of normal vs illegal tap signals
- **Automatic Peak Detection**: Annotates significant frequency components
- **Distortion Detection**: Clear visualization of 3rd and 5th harmonics in illegal tap scenarios

### Key Observations
- **Normal Load**: Shows clean fundamental frequency (50 Hz) with minimal harmonics (<0.1%)
- **Illegal Tap**: Exhibits clear spectral distortion with:
  - **3rd Harmonic (150 Hz)**: ~11-12% of fundamental magnitude
  - **5th Harmonic (250 Hz)**: ~5-6% of fundamental magnitude
  - These harmonics indicate non-linear loads typical of illegal tapping with electronic devices
