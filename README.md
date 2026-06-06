# pi-gps-logger

A GPS data logger for the Raspberry Pi with a Kalman filter for smoothing raw GPS tracks. Designed to run as a systemd service and optionally interface with an Adafruit 2.8" TFT display and GPIO buttons for standalone operation in the field.

## Hardware

- Raspberry Pi (any model with a UART interface)
- GPS module connected via UART (GPIO14 TX / GPIO15 RX), e.g. a SparkFun or similar NMEA-output module
- Optional: Adafruit 2.8" resistive TFT+ display with GPIO buttons (pins 17, 22, 23, 27)

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Install and enable the systemd service:

```bash
cd service
bash install_service.bash
```

Edit `service/gps_launcher.service` and replace `<your-username>` with your Raspberry Pi username before installing.

## Usage

**Standalone (TFT display):** Use `mobility_launcher.py`. Button presets let you select a motion profile (stationary, walking, driving), start logging, and save to CSV.

**Headless:** Run `gps_with_kalman.py` directly. Press Ctrl+C to stop; data is saved automatically to `output/`.

**Plot a recorded CSV:** Edit the `input_path` in `render_gps_data.py` and run it to generate an interactive HTML map comparing the raw and filtered GPS tracks.

---

## Kalman Filter

The filter (`gps_kalman_filter.py`) uses a constant-velocity motion model with a 4-element state vector `[x, y, ẋ, ẏ]` in metres.

- **Predict step** propagates the state forward using the motion model and adds process noise **Q** (models uncertainty from unknown acceleration)
- **Update step** corrects the prediction using the GPS measurement and adds measurement noise **R** (models GPS sensor accuracy)

### Tuning knobs

Three parameters control the filter behaviour, exposed as presets in `mobility_launcher.py`:

| Parameter | Description | Effect |
|---|---|---|
| `sigma_gps` | GPS measurement noise (metres) | Lower → trust GPS more, less smoothing. Higher → trust GPS less, smoother but laggier track. |
| `sigma_accel` | Acceleration noise (m/s²) | Lower → assume smooth/constant motion. Higher → allow rapid changes in speed/direction. |
| `initial_velocity_std` | Initial velocity uncertainty (m/s) | Controls how quickly the filter converges from a standing start. |

### Preset reference

| Preset | `sigma_gps` | `sigma_accel` | `initial_velocity_std` | Use case |
|---|---|---|---|---|
| Stationary | 5.0 | 0.05 | 0.5 | Fixed location, minimal motion expected |
| Walking 1 | 5.0 | 0.5 | 1.0 | Pedestrian speed |
| Walking 2 | 6.0 | 0.4 | 1.0 | Pedestrian speed, slightly noisier GPS environment |
| Driving 1 | 5.0 | 2.0 | 10.0 | Vehicle speed with rapid acceleration changes |
