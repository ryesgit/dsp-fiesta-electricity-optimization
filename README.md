# DSP Fiesta Power Monitoring System

A Digital Signal Processing (DSP)-based power monitoring and anomaly detection system.

## Overview
This project analyzes voltage and current waveforms using core DSP techniques to identify abnormal power usage and illegal electricity tapping.

### System Architecture
```mermaid
graph LR
    subgraph "Data Acquisition"
        A[Power Source] --> B[Sensors (V/I)]
        B --> C[ADC / Data Gen]
    end
    
    subgraph "DSP Core"
        C --> D[Preprocessing (Filter)]
        D --> E[Feature Extraction]
        E --> F[Anomaly Detection]
    end
    
    subgraph "Visualization"
        F --> G[Real-Time Dashboard]
        G --> H[Alerts & Logs]
    end
```

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

## Analysis & Visualization

### 1. Signal Visualization
Visualize the time-domain waveforms:
```bash
python src/visualize_signal.py data/normal_load.csv --time-range 0 0.1
```

### 2. Signal Filtering
Apply a low-pass filter to remove high-frequency noise:
```bash
python src/apply_filter.py data/normal_load.csv --output data/normal_load_filtered.csv --plot both
```

### 3. Harmonic Distortion (THD) Analysis
Analyze the Total Harmonic Distortion (THD) to detect non-linear loads (often associated with illegal tapping):
```bash
python src/analyze_thd.py data/illegal_tap.csv --save-plot docs/illegal_thd.png
```
- **Normal Load**: Typically low THD (< 5%).
- **Illegal Tap**: High THD due to harmonic distortion (e.g., 3rd and 5th harmonics).

### 4. Anomaly Detection
Run the automated anomaly detection script to classify signals:
```bash
python src/detect_anomaly.py data/illegal_tap.csv
```
**Features Extracted:**
- **RMS Voltage/Current**: Root Mean Square values.
- **Apparent Power**: $V_{rms} \times I_{rms}$.
- **THD**: Total Harmonic Distortion.

**Detection Logic:**
- If **THD > 5%**, the signal is flagged as an **ANOMALY** (High Harmonic Distortion).

## Real-Time Dashboard
Launch the real-time visualization dashboard to simulate live monitoring:
```bash
python src/dashboard.py data/illegal_tap.csv
```
**Features:**
- **Live Waveforms**: Scrolling plot of voltage and current.
- **Real-Time FFT**: Dynamic frequency spectrum of the current signal.
- **Metrics**: Live display of RMS, Power, and THD.
- **Anomaly Alert**: Visual alert (Green/Red) indicating system status.
