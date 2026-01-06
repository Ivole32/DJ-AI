# AI for DJs

This project builds an intelligent DJ tracklist generator by learning track transitions from real DJ sets and combining them with audio features like BPM, energy, and danceability.

## ⚠️ Disclaimer

**Please note:** Some features described in this documentation will be released gradually over time. This approach helps maintain project organization and ensures quality with each release. Stay tuned for updates!

## 🎯 Features

- **🎵 Audio Analysis**: Extracts BPM, musical key (including Camelot notation), and energy levels from YouTube videos
- **🤖 ML-Powered Predictions**: Machine learning model trained on real DJ transitions to suggest compatible next tracks
- **🎚️ Harmonic Mixing**: Uses Camelot Wheel notation for perfect key-compatible transitions
- **🌐 REST API**: FastAPI backend with Redis caching and PostgreSQL database
- **💻 Web Interface**: User-friendly frontend for searching tracks and building playlists
- **📊 Dataset**: Trained on real DJ mixes from the mir-aidj/djmix-dataset

## 📁 Project Structure

```
DJ-AI/
├── analyzer/          # Audio feature extraction from YouTube videos
│   ├── main.py        # Entry point for batch processing
│   ├── analyzer.py    # BPM, key, and energy detection
│   └── pipeline.py    # Multi-threaded download & analysis
│
├── ml_model/          # Machine learning model for transition prediction
│   ├── training/      # Model training pipeline
│   ├── inference/     # Prediction API
│   └── models/        # Trained model files
│
├── api/               # FastAPI REST backend
│   ├── routers/       # API endpoints (prediction, search)
│   ├── services/      # Business logic
│   ├── database/      # PostgreSQL integration
│   └── cache/         # Redis caching layer
│
├── frontend/          # Web interface
│   ├── public/        # HTML, CSS, JavaScript
│   └── server.js      # Static file server
│
└── dataset/           # Training data and output files
    ├── dataset.json   # DJ mix metadata
    ├── transitions.csv # Extracted track transitions
    ├── tracks.csv     # Analyzed tracks with BPM, key, energy
    └── failed_videos.json # Failed video downloads
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11.9** (recommended - see Python Version section below)
- **FFmpeg** (for audio processing)
- **Redis** (optional, for API caching)
- **PostgreSQL** (for user data)

### 1. Setup Analyzer

Extract audio features from YouTube videos:

```bash
cd analyzer
pip install -r requirements.txt
python main.py
```

This downloads videos from `dataset/dataset.json` and creates `dataset/tracks.csv` with BPM, key, and energy data.

### 2. Train ML Model

Train the transition prediction model:

```bash
cd ml_model

# Extract transitions from DJ mixes
python data_preparation/export_transitions.py

# Train the model
python training/train.py
```

The trained model is saved to `ml_model/models/transition_model.joblib`.

### 3. Run API Server

Start the FastAPI backend:

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`

### 4. Launch Frontend

Start the web interface:

```bash
cd frontend
npm install
npm start
```

Frontend will be available at `http://localhost:3000`

## 🔧 Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **scikit-learn**: Machine learning (HistGradientBoostingClassifier)
- **pandas & numpy**: Data processing
- **Redis**: Caching layer
- **PostgreSQL**: User database

### Audio Processing
- **librosa**: Audio analysis and feature extraction
- **yt-dlp**: YouTube video downloading
- **essentia**: Advanced audio analysis
- **FFmpeg**: Audio format conversion

### Frontend
- **Vanilla JavaScript**: No framework overhead
- **HTML5/CSS3**: Modern responsive design

## 📖 How It Works

1. **Data Collection**: The analyzer downloads audio from YouTube videos listed in the dataset
2. **Feature Extraction**: Each track is analyzed for BPM, musical key (Camelot notation), and energy
3. **Transition Learning**: Real DJ transitions are extracted from mix metadata
4. **Model Training**: A gradient boosting model learns what makes good transitions based on:
   - BPM differences
   - Key compatibility (Camelot distance)
   - Energy progression
5. **Prediction**: Given a track, the model suggests the most compatible next tracks
6. **API Serving**: REST endpoints provide predictions with caching for performance

## 🧠 Training Data
The treaning data is downloaded from here [mir-aidj/djmix-dataset](https://github.com/mir-aidj/djmix-dataset).
Huge thanks to the person who made this, I love you.

## ⚠️ Python Version

**Recommended Python Version: 3.11.9**

Some dependencies in this project require Python 3.11.9 for optimal compatibility. This version has been tested and is recommended for use with all libraries.

## � Documentation

- **[Analyzer README](analyzer/README.md)**: Detailed audio analysis documentation
- **[ML Model README](ml_model/README.md)**: Model training and inference guide
- **[Devlogs](devlogs/)**: Development progress and updates

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs via GitHub Issues
- Suggest new features
- Submit pull requests

## �💬 Support

- **Issues:** [GitHub Issues](https://github.com/Ivole32/Linux-API/issues)
- **Support the project:** [☕ Buy me a coffee on Ko-fi](https://ko-fi.com/ivole32)
## ⚖️ Legal Disclaimer

This project is provided for educational and research purposes only. The author is not responsible for any legal issues that may arise from the use of this software, including but not limited to:

- Downloading or analyzing content from YouTube or other platforms
- Copyright infringement or violations of terms of service
- Any misuse of the software or its outputs

Users are solely responsible for ensuring their use of this software complies with all applicable laws, regulations, and terms of service of third-party platforms. Use at your own risk.
---

Made with ❤️ by [Ivole32](https://github.com/Ivole32)