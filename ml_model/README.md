# ML Model - DJ Track Transition Prediction

This module contains the machine learning components for predicting good track transitions in DJ sets.

## 📁 Project Structure

```
ml_model/
├── config.py              # Centralized configuration (paths)
├── data_preparation/      # Data extraction and preprocessing
│   └── export_transitions.py
├── training/              # Model training pipeline
│   ├── training_data.py
│   └── train.py
├── inference/             # Prediction and serving
│   ├── predict.py
│   └── validation.py
├── utils/                 # Shared utilities
│   └── feature_builder.py
├── models/                # Trained model files (.joblib)
│   └── transition_model.joblib
└── requirements.txt       # Python dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd ml_model
pip install -r requirements.txt
```

### 2. Prepare Training Data

Extract transitions from the dataset:

```bash
python data_preparation/export_transitions.py
```

This creates `dataset/transitions.csv` containing all track-to-track transitions from DJ mixes.

### 3. Train the Model

```bash
python training/train.py
```

**Requirements:**
- `dataset/tracks.csv` with analyzed tracks (BPM, key, Camelot, energy)
- `dataset/transitions.csv` with real DJ transitions

The training process:
- Loads track features (including **Camelot notation** for harmonic key matching)
- Loads transitions from DJ mixes
- Builds training set with positive (real transitions) and negative (random pairs) examples
- Trains a HistGradientBoostingClassifier using features like BPM difference and **Camelot key distance**
- Saves model to `models/transition_model.joblib`

**Note:** The Camelot Wheel notation (e.g., "8A", "11B") is crucial for the model - it enables harmonic mixing predictions based on DJ key compatibility.

### 4. Validate Setup (Optional but Recommended)

Before making predictions, verify everything is ready:

```bash
python inference/validation.py
```

This checks:
- ✓ All required files exist (tracks.csv, model)
- ✓ All dependencies are importable
- ✓ Paths are correctly configured

**Quick validation in code:**

```python
from ml_model import quick_validate

if quick_validate():
    print("✓ Model ready!")
else:
    print("✗ Setup incomplete - check files and dependencies")
```

### 5. Make Predictions

```python
from inference.predict import suggest_next

# Get top 10 suggestions for next track
suggestions = suggest_next('youtube_video_id', top_k=10)

for track_id, score in suggestions:
    print(f"{track_id}: {score:.3f}")
```

## 📊 How It Works

### Feature Engineering

The model uses these features to predict good transitions:

- **BPM Difference**: Absolute tempo difference between tracks
- **Energy Difference**: Change in energy level (increase/decrease)
- **Key Distance**: Harmonic distance using Camelot Wheel notation
- **Same Key**: Binary flag for identical keys
- **Tempo Match**: Binary flag for BPM within ±2

### Training Data

- **Positive Examples**: Real transitions from DJ mixes (weighted by frequency)
- **Negative Examples**: Random track pairs that likely wouldn't work well
- **Ratio**: 3 negative examples per positive to balance classes

### Model Architecture

**HistGradientBoostingClassifier** with:
- Max depth: 6 (prevents overfitting)
- Iterations: 200
- Learning rate: 0.05 (stable convergence)
- Min samples per leaf: 20 (reduces noise)
- L2 regularization: 1.0
- Early stopping enabled

## 📝 Module Documentation

### config.py

**Centralized configuration** for all ML model modules:

Uses `pathlib` for cross-platform paths. Automatically creates required directories.

**Key settings:**
- `TRACKS_CSV`: Path to analyzed tracks (dataset/tracks.csv)
- `TRANSITIONS_CSV`: Path to extracted transitions (dataset/transitions.csv)
- `DATASET_JSON`: Path to DJ mix dataset (dataset/dataset.json)
- `MODEL_FILE`: Path to trained model (models/transition_model.joblib)
- `MODELS_DIR`: Directory for model files
- Training hyperparameters (MAX_DEPTH, MAX_ITER, LEARNING_RATE, etc.)
- Training data generation parameters (NEGATIVES_PER_POS, MAX_FREQUENCY_WEIGHT)

All modules import paths and parameters from this central config for consistency.

### data_preparation/

**export_transitions.py**: Extracts track-to-track transitions from `dataset.json`
- Counts frequency of each transition
- Exports to CSV format
- Filters out tracks with null IDs
- Uses centralized config for paths

### training/

**training_data.py**: Generates labeled training set
- `build_training_set()`: Creates feature matrix and labels
- Balances positive/negative examples
- Weights frequent transitions using `MAX_FREQUENCY_WEIGHT` from config
- Uses `NEGATIVES_PER_POS` from config for class balance

**train.py**: Main training script
- Loads and preprocesses data
- Trains the model using hyperparameters from config
- Saves trained model to disk

### inference/

**predict.py**: Prediction API
- `TrackPredictor`: Class-based predictor with full control
- `suggest_next()`: Convenience function for quick predictions
- Returns ranked list of (track_id, probability) tuples

**validation.py**: Model validation utilities for setup verification

This module provides three levels of validation to ensure the model is ready:

**1. `validate_model_files(tracks_path=None, model_path=None)`**
- Checks file existence: `tracks.csv` and `transition_model.joblib`
- Returns detailed dict with `ok` (bool), `missing` (list), and file paths
- Use before training or prediction to catch missing data early

```python
from ml_model import validate_model_files

result = validate_model_files()
if result['ok']:
    print(f"✓ Files ready: {result['tracks_path']}")
else:
    print(f"✗ Missing: {result['missing']}")
```

**2. `validate_imports()`**
- Tests if all required packages can be imported
- Checks: pandas, joblib, sklearn, and local utils
- Returns dict with `ok` (bool) and `missing` (list)
- Use to diagnose dependency issues

```python
from ml_model import validate_imports

result = validate_imports()
if not result['ok']:
    print(f"Install missing packages: {result['missing']}")
```

**3. `quick_validate(tracks_path=None, model_path=None)`**
- Fast boolean check: returns `True` if everything is ready
- Combines file and import validation
- Ideal for quick checks in production code

```python
from ml_model import quick_validate

if not quick_validate():
    raise RuntimeError("ML model not ready - run validation.py for details")
```

**Standalone Diagnostic Tool:**

Run as a script for a complete system check:

```bash
python inference/validation.py
```

Output example:
```
============================================================
ML Model Validation
============================================================

1. Checking files...
   ✓ All files exist
   Tracks: C:\...\analyzer\output\tracks.csv
   Model: C:\...\ml_model\models\transition_model.joblib

2. Checking imports...
   ✓ All imports available

============================================================
Ready: True
============================================================
```

### utils/

**feature_builder.py**: Feature engineering functions
- `camelot_distance()`: Calculates harmonic key distance
- `build_pair_features()`: Extracts features from track pairs

## 🔄 Workflow

```
dataset.json → export_transitions.py → transitions.csv
                                              ↓
tracks.csv → training_data.py → feature matrix
                                              ↓
                                       train.py → transition_model.joblib
                                                            ↓
                                                      predict.py → suggestions
```

## 🛠️ Configuration

All configuration is centralized in `config.py` for easy customization.

### Model Hyperparameters

Edit `config.py` to adjust model training parameters:
- `MAX_DEPTH`: Tree depth (controls complexity) - Default: 6
- `MAX_ITER`: Number of boosting rounds - Default: 200
- `LEARNING_RATE`: Step size for gradient descent - Default: 0.05
- `MIN_SAMPLES_LEAF`: Minimum samples per leaf node - Default: 20
- `L2_REGULARIZATION`: L2 penalty for regularization - Default: 1.0
- `EARLY_STOPPING`: Stop if validation doesn't improve - Default: True
- `RANDOM_STATE`: Reproducibility seed - Default: 42

### Training Data Balance

Edit `config.py` to adjust training data generation:
- `NEGATIVES_PER_POS`: Ratio of negative to positive examples - Default: 3
- `MAX_FREQUENCY_WEIGHT`: Cap on repeating frequent transitions - Default: 3

## 📈 Performance Tips

1. **More Data**: Analyze more DJ mixes to get more transitions
2. **Feature Engineering**: Add new features (genre, mood, decade, etc.)
3. **Hyperparameter Tuning**: Use GridSearchCV for optimal parameters
4. **Class Weighting**: Adjust if precision/recall is imbalanced

## 🐛 Troubleshooting

**FileNotFoundError**: Ensure you've run the analyzer and have `tracks.csv`
- Run `python inference/validation.py` to see which files are missing
- Check paths: `dataset/tracks.csv` and `models/transition_model.joblib`

**ImportError**: Missing dependencies
- Run `python inference/validation.py` to identify missing packages
- Install with: `pip install -r requirements.txt`

**KeyError in predict**: Track ID not in dataset
- Track hasn't been analyzed yet - add it to analyzer queue

**Poor predictions**: Need more training data or better feature engineering
- Analyze more DJ mixes to increase training transitions
- Check if `transitions.csv` has sufficient variety

## 📚 Dependencies

- pandas: Data manipulation
- numpy: Numerical operations
- scikit-learn: Machine learning
- joblib: Model serialization

## 🤝 Integration

This model is used by:
- `api/`: REST API endpoints for track suggestions
- `frontend/`: Web interface for DJ mix planning

## ⚠️ Python Version

**Recommended Python Version: 3.11.9**

Some dependencies in this project require Python 3.11.9 for optimal compatibility. This version has been tested and is recommended for use with all libraries.