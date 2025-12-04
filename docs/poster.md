# DSP Fiesta: Power Monitoring & Anomaly Detection

## 🎯 Abstract
This project implements a **Digital Signal Processing (DSP)** system to monitor electrical power signals and detect anomalies such as **illegal electricity tapping**. By analyzing voltage and current waveforms in real-time, the system identifies non-linear loads characterized by high **Total Harmonic Distortion (THD)**.

## 🛠️ Key Features
- **Synthetic Data Generation**: Simulates normal loads and illegal tapping scenarios.
- **Signal Preprocessing**: Low-pass filtering to remove noise.
- **Spectral Analysis**: FFT-based harmonic extraction and THD calculation.
- **Anomaly Detection**: Automated classification based on DSP feature vectors.
- **Real-Time Dashboard**: Live visualization of waveforms, spectrum, and alerts.

## 📊 System Architecture
```mermaid
graph LR
    A[Sensors] --> B[DSP Core] --> C[Dashboard]
    style B fill:#f96,stroke:#333,stroke-width:2px
```

## 📈 Results
### Normal Load
- **Waveform**: Clean sine wave.
- **THD**: < 1%
- **Status**: 🟢 Normal

### Illegal Tap (Simulated)
- **Waveform**: Distorted current.
- **THD**: > 10% (High 3rd/5th harmonics)
- **Status**: 🔴 Anomaly Detected

## 🚀 Usage
```bash
# Generate Data
python src/generate_data.py

# Run Dashboard
python src/dashboard.py data/illegal_tap.csv
```
