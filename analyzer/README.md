
# Analyzer Module - DJ Track Feature Extraction

Downloads and analyzes audio from YouTube videos to extract DJ-relevant features (BPM, key, energy). Outputs are used by the ML model for transition predictions.

## Structure

```
analyzer/
├── main.py           # Entry point
├── config.py         # Configuration
├── pipeline.py       # Download & analysis pipeline
├── analyzer.py       # Audio analysis (BPM, key, energy)
├── cutter.py         # Audio cutting (ffmpeg)
├── json_loader.py    # Dataset loading
├── requirements.txt  # Python dependencies
└── tmp/              # Temporary audio files
```

**Output files** are saved to `dataset/`:
- `tracks.csv` - Analyzed tracks
- `failed_videos.json` - Failed downloads

## Quick Start

### 1. Install FFmpeg

**Windows:**
- With Chocolatey: `choco install ffmpeg`
- With winget: `winget install Gyan.FFmpeg`
- Or download from the official FFmpeg site

**Linux:** `sudo apt install ffmpeg`

**macOS:** `brew install ffmpeg`

### 2. Install Python Dependencies

```bash
cd analyzer
pip install -r requirements.txt
```

### 3. Run Analyzer

```bash
python main.py
```
This will process tracks listed in `../dataset/dataset.json` and output results to `../dataset/tracks.csv`.

---
For more details, see the main project README.

### 3. Run the Analyzer

```bash
python main.py
```

The analyzer will:
- Load all video IDs from `dataset/dataset.json`
- Skip already processed tracks (found in `dataset/tracks.csv`)
- Skip recently failed videos (within 7 days)
- Download audio from YouTube
- Cut to center 60 seconds
- Analyze BPM, key (standard + Camelot notation), and energy
- Save results to `dataset/tracks.csv`

## 📊 Output Format

### tracks.csv

```csv
youtube_id,bpm,key,camelot,energy
dQw4w9WgXcQ,113,F# minor,11A,0.045821
jNQXAC9IVRw,128,C major,8B,0.062134
```

**Columns:**
- `youtube_id`: YouTube video ID
- `bpm`: Beats per minute (tempo)
- `key`: Musical key in standard notation (e.g., "C major", "F# minor")
- `camelot`: Camelot Wheel notation for DJ mixing (e.g., "8A", "11B")
- `energy`: RMS energy level (0.0 - 1.0, normalized)

### failed_videos.json

Tracks download failures with retry logic:

```json
{
  "video_id": {
    "error": "Download error: Video unavailable",
    "timestamp": "2026-01-06T14:30:00",
    "attempts": 2
  }
}
```

Videos are retried after 7 days (configurable in `main.py`).

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Performance
DOWNLOAD_THREADS = 10          # Parallel downloads
ANALYZE_PROCESSES = cpu_count() # Parallel analysis processes

# Audio processing
CUT_LENGTH = 60  # Seconds to analyze (from center)
```

## 📝 Module Documentation

### main.py

**Entry point** that coordinates the workflow:

- `get_processed_ids()`: Loads already analyzed tracks from CSV
- `get_failed_ids(retry_after_days=7)`: Loads recent failures to skip
- `main()`: Filters videos, shuffles queue, starts pipeline

**Usage:**
```bash
python main.py
```

### analyzer.py

**Core audio analysis** using librosa:

**Key Detection:**
- Uses Krumhansl-Schmuckler key profiles
- Compares chroma features against major/minor templates
- Returns both standard notation and Camelot Wheel format

**BPM Detection:**
- Uses librosa's tempo estimation with median aggregation
- Returns integer BPM value

**Energy Calculation:**
- RMS (Root Mean Square) energy across the audio
- Normalized to 0.0 - 1.0 range

**Functions:**
- `analyze_audio(path: str) -> dict`: Main analysis function
- `camelot_distance()`: Helper for key compatibility (used by ML model)

**Example:**
```python
from analyzer import analyze_audio

result = analyze_audio("audio.wav")
# Returns: {'bpm': 128, 'key': 'C major', 'camelot': '8B', 'energy': 0.045}
```

### pipeline.py

**Multi-threaded/multi-process pipeline** with three stages:

**1. Download Stage (Multi-threaded)**
- Uses `yt-dlp` to download audio from YouTube
- Extracts best audio quality
- Handles errors and retries
- Saves failures to cache

**2. Cut Stage**
- Cuts audio to center segment (default: 60s)
- Uses ffmpeg via `cutter.py`
- Cleans up raw downloads

**3. Analysis Stage (Multi-process)**
- Parallel audio analysis using process pool
- Handles CPU-intensive librosa operations
- Cleans up cut files after analysis

**4. Writer Stage**
- Deduplicates by `youtube_id`
- Appends to CSV and JSON
- Thread-safe file writing

**Functions:**
- `run_pipeline(video_ids)`: Main pipeline coordinator
- `download_worker(pbar)`: Download thread worker
- `analyze_worker(args)`: Analysis process worker
- `writer_worker(total)`: Result writing thread
- `failure_writer()`: Failure cache persistence thread
- `load_failed_videos()`: Load failure cache
- `save_failed_video(id, error)`: Add to failure cache

**Progress Display:**
```
📥 Download: 100%|████████████| 50/50 [05:30<00:00]
🧠 Analysis: 100%|████████████| 50/50 [02:15<00:00]
```

### cutter.py

**FFmpeg wrapper** for audio manipulation:

- `get_duration(file)`: Get audio duration using ffprobe
- `center_cut(inp, out, length)`: Extract center segment

**Logic:**
- If file ≤ length: use entire file
- If file > length: extract center segment

### config.py

**Centralized configuration:**

Uses `pathlib` for cross-platform paths. Automatically creates required directories.

**Key settings:**
- `JSON_FILE`: Path to dataset.json
- `TMP_DIR`: Temporary audio storage (auto-cleaned)
- `OUT_DIR`: Analysis results output
- `DOWNLOAD_THREADS`: Parallel downloads
- `ANALYZE_PROCESSES`: Parallel analysis (defaults to CPU count)
- `CUT_LENGTH`: Audio segment length in seconds

### json_loader.py

**Dataset utilities:**

- `load_youtube_ids()`: Extract all unique video IDs from dataset

Currently not used by main.py (kept for backward compatibility).

## 🔄 Workflow

```
dataset.json
    ↓
main.py (load & filter IDs)
    ↓
pipeline.py
    ├─→ download_worker (yt-dlp) → tmp/video_id.wav
    ├─→ center_cut → tmp/video_id_cut.wav
    ├─→ analyze_worker (librosa) → features
    └─→ writer_worker → dataset/tracks.csv
```

## 🎵 Audio Analysis Details

### BPM (Tempo) Detection

Uses **onset detection** and **autocorrelation**:
- Detects beats in audio signal
- Estimates tempo using median aggregation
- More stable than mean for varied music

### Key Detection (Krumhansl-Schmuckler)

1. **Chroma extraction**: 12-bin pitch class profile
2. **Template matching**: Correlate with major/minor profiles
3. **Best match**: Highest correlation determines key
4. **Camelot mapping**: Convert to DJ-friendly notation

**Camelot Wheel:**
- Numbers 1-12: Position on circle of fifths
- A (minor) / B (major): Mode designation
- Adjacent keys mix harmonically

### Energy Calculation

**RMS (Root Mean Square)** energy:
- Measures overall loudness/intensity
- Used for energy progression in DJ sets
- Higher values = more energetic tracks

## ⚙️ Performance Optimization

### Parallel Processing

**Downloads (I/O bound):**
- 10 concurrent threads (configurable)
- Reduces wall-clock time significantly
- Random delays (0.5-1.5s) to avoid rate limiting

**Analysis (CPU bound):**
- Multi-processing pool (1 per CPU core)
- Parallelizes librosa computations
- Scales with available cores

### Memory Management

- Streams audio through pipeline
- Cleans up temporary files immediately
- Only keeps final results in memory

### Resume Capability

- Automatically skips processed tracks
- Retries failed videos after 7 days
- No need to restart from scratch

## 🐛 Troubleshooting

### FFmpeg Not Found

**Error:** `subprocess` fails with "ffmpeg not found"

**Solution:** Install ffmpeg and ensure it's in PATH
```bash
# Verify installation
ffmpeg -version
ffprobe -version
```

### yt-dlp Download Failures

**Error:** "Video unavailable" or "Sign in to confirm your age"

**Solution:** 
- Videos are automatically retried after 7 days
- Check `dataset/failed_videos.json` for details
- Some videos may require authentication (not supported)

### "No module named 'librosa'"

**Error:** Import error for librosa

**Solution:**
```bash
pip install -r requirements.txt
```

### Low Download Speed

**Symptom:** Downloads taking very long

**Solution:**
- Increase `DOWNLOAD_THREADS` in config.py (try 15-20)
- Check your internet connection
- YouTube may be rate-limiting (delays are intentional)

### Analysis Crashes

**Error:** Librosa errors or crashes during analysis

**Solution:**
- Check audio file integrity in `tmp/` directory
- Ensure sufficient RAM (librosa is memory-intensive)
- Reduce `ANALYZE_PROCESSES` if system runs out of memory

### Duplicate Entries in CSV

**Symptom:** Same video_id appears multiple times

**Solution:**
- Pipeline automatically deduplicates (keeps last entry)
- This is normal if re-running the analyzer
- Use `drop_duplicates()` in pandas if needed

## 📊 Output Statistics

After each run, the analyzer displays:

```
🎧 Total videos: 1500
✅ Already processed: 1200
❌ Temporarily skipped (failed): 50
🔄 Remaining to process: 250

📥 Download: 100%|████████████| 250/250 [15:30<00:00]
🧠 Analysis: 100%|████████████| 250/250 [08:15<00:00]

✅ Done! 245 new tracks analyzed and saved.
```

**Note:** Some videos may fail during download or analysis (age-restricted, deleted, private, etc.). These are tracked in `failed_videos.json`.

## 🔗 Integration

This analyzer's output is used by:

- **ml_model/**: Training data for transition prediction
  - `tracks.csv` provides track features
  - Matched with `transitions.csv` for supervised learning

- **api/**: Real-time predictions
  - Loads `tracks.csv` for feature lookup
  - Powers track suggestion endpoints

## 📚 Dependencies

Core libraries:

- **librosa**: Audio analysis (BPM, chroma, energy)
- **numpy**: Numerical operations
- **scipy**: Signal processing (used by librosa)
- **yt-dlp**: YouTube audio download
- **tqdm**: Progress bars
- **ffmpeg**: Audio processing (system dependency)

See `requirements.txt` for exact versions.

## 🚀 Advanced Usage

### Custom Audio Length

Edit `config.py`:
```python
CUT_LENGTH = 120  # Analyze 2 minutes instead of 1
```

Longer segments may improve accuracy but increase processing time.

### Analyze Specific Videos

Instead of running `main.py`, use pipeline directly:

```python
from pipeline import run_pipeline

video_ids = ["dQw4w9WgXcQ", "jNQXAC9IVRw"]
run_pipeline(video_ids)
```

### Batch Processing

For large datasets, consider running in batches:

```python
from main import main
import config

# Process in smaller batches
config.BATCH_SIZE = 100  # Process 100 at a time
main()
```

### Custom Analysis

Import analyzer directly for custom workflows:

```python
from analyzer import analyze_audio

# Analyze local file
result = analyze_audio("path/to/audio.wav")
print(f"BPM: {result['bpm']}, Key: {result['key']}")
```

## 💡 Performance Tips

1. **SSD Storage**: Use SSD for `tmp/` directory (faster I/O)
2. **More Threads**: Increase `DOWNLOAD_THREADS` on fast connections
3. **Batch Processing**: Run during off-peak hours for better YouTube speeds
4. **Skip Processed**: Don't delete `tracks.csv` - resuming is much faster
5. **Monitor Failures**: Check `failed_videos.json` periodically

## 🤝 Contributing

When adding new features:

1. **Add docstrings** to all functions (Google style)
2. **Update this README** with new functionality
3. **Test with sample videos** before large runs
4. **Consider backward compatibility** with existing CSV format

## ⚠️ Python Version

**Recommended Python Version: 3.11.9**

Some dependencies in this project require Python 3.11.9 for optimal compatibility. This version has been tested and is recommended for use with all libraries.