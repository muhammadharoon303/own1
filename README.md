# 92PKR Live Split-Screen AI Predictor & Continuous Learning Bot

An advanced real-time AI prediction, live pattern analyzer, and continuous self-training bot for the 92PKR **Win Go (Big/Small)** game.

## Features

- **Live Split-Screen HUD:** Integrated split-screen showing the live 92PKR game interface on the left and the real-time AI Prediction Radar on the right.
- **Automated Live Gateway Synchronization:** Directly interfaces with the live 92PKR API gateway to automatically extract active issue periods, countdown timers, and drawn results without manual input.
- **Ensemble Multi-Model Consensus:**
  - **Markov Transition Matrix:** Analyzes 1st and 2nd-order state transitions with recency weighting.
  - **Streak & Pattern Analyzer:** Detects Dragon streaks (3+ consecutive), alternating chop, pair sequences, and N-gram pattern trees.
  - **Statistical Frequency & Ratio:** Computes hot/cold digits (0–9) and color distribution (Red, Green, Violet).
- **Online Self-Training Engine (nalyzer/adaptive_trainer.py):**
  - Walk-forward backtesting on recent draws.
  - Dynamic model weight optimization (Softmax / EMA smoothed).
  - Real-time win/loss verification for previous predictions.
- **Empirical Confidence Calibration & Trap Guard (nalyzer/confidence_calibrator.py):**
  - Trained on 45+ real-world verified test outcomes.
  - Detects overextension/reversal traps (>60% confidence signals often suffer mean-reversion).
  - Enforces strict neutral filtering (SKIP / DO NOT BET) during model disagreement.
  - Highlights optimal prime entry windows (53%–58% sweet spot).
- **Mobile PWA Ready:** Installable directly to mobile home screens with custom app icons and full-screen standalone app mode.
- **OCR Table Extraction:** Built-in Tesseract OCR and OpenCV pipeline to extract draw records from screenshots and ZIP archives.

## Project Structure

`
big_small_bot/
├── analyzer/                  # Core prediction & training modules
│   ├── adaptive_trainer.py    # Walk-forward online learning & weight optimization
│   ├── confidence_calibrator.py # Empirical calibration & trap detection
│   ├── engine.py              # Ensemble consensus predictor
│   ├── markov.py              # Markov chain transition models
│   ├── patterns.py            # Dragon streaks & N-gram patterns
│   └── statistics.py          # Hot/cold numbers & color frequencies
├── data/                      # Persistent history & model weights
│   ├── empirical_calibration.json
│   ├── history.json
│   ├── model_weights.json
│   └── training_stats.json
├── live/                      # Live 92PKR API client
│   └── client.py
├── ocr/                       # Tesseract OCR & OpenCV parser
│   └── parser.py
├── static/                    # Dashboard styles, scripts, icons, and manifest
│   ├── app.js
│   ├── icon-192.png
│   ├── icon-512.png
│   ├── manifest.json
│   └── style.css
├── templates/
│   └── index.html             # Split-screen web dashboard
├── app.py                     # Flask web server
├── requirements.txt           # Dependencies
└── START_BOT.bat              # 1-Click launcher
`

## Quick Start

### 1. Install Dependencies
`ash
pip install -r requirements.txt
`

### 2. Run the Bot
Double-click START_BOT.bat or run:
`ash
python app.py
`

Open your browser at:
- **Local:** http://127.0.0.1:5092
- **Mobile (same Wi-Fi):** http://<YOUR_LOCAL_IP>:5092
