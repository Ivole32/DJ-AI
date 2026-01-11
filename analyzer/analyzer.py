
# Numpy for numerical operations
import numpy as np

# Librosa for audio analysis
import librosa

# =========================
# KEY PROFILES (Krumhansl)
# =========================
MAJOR_PROFILE = np.array([
    6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
    2.52, 5.19, 2.39, 3.66, 2.29, 2.88
])

MINOR_PROFILE = np.array([
    6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
    2.54, 4.75, 3.98, 2.69, 3.34, 3.17
])

NOTES = ["C", "C#", "D", "D#", "E", "F",
         "F#", "G", "G#", "A", "A#", "B"]

CAM_MAJOR = {
    "C": "8B", "G": "9B", "D": "10B", "A": "11B", "E": "12B",
    "B": "1B", "F#": "2B", "C#": "3B", "G#": "4B",
    "D#": "5B", "A#": "6B", "F": "7B"
}

CAM_MINOR = {
    "A": "8A", "E": "9A", "B": "10A", "F#": "11A", "C#": "12A",
    "G#": "1A", "D#": "2A", "A#": "3A",
    "F": "4A", "C": "5A", "G": "6A", "D": "7A"
}


# =========================
# CORE ANALYSIS
# =========================
def analyze_audio(path: str) -> dict:
    y, sr = librosa.load(path, sr=None, mono=True)

    # ---------- BPM ----------
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning)
        tempo = librosa.beat.tempo(y=y, sr=sr, aggregate=np.median)
    bpm = int(round(float(tempo[0])))

    # ---------- ENERGY ----------
    rms = librosa.feature.rms(y=y)
    energy = float(np.mean(rms))

    # ---------- KEY ----------
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)

    major_corr = [
        np.corrcoef(np.roll(MAJOR_PROFILE, i), chroma_mean)[0, 1]
        for i in range(12)
    ]
    minor_corr = [
        np.corrcoef(np.roll(MINOR_PROFILE, i), chroma_mean)[0, 1]
        for i in range(12)
    ]

    maj_i = int(np.argmax(major_corr))
    min_i = int(np.argmax(minor_corr))

    if major_corr[maj_i] >= minor_corr[min_i]:
        key = f"{NOTES[maj_i]} major"
        camelot = CAM_MAJOR.get(NOTES[maj_i])
    else:
        key = f"{NOTES[min_i]} minor"
        camelot = CAM_MINOR.get(NOTES[min_i])

    return {
        "bpm": bpm,
        "key": key,
        "camelot": camelot,
        "energy": round(energy, 6)
    }