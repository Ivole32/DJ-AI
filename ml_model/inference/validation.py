"""
Simple validation utilities for ML model.

Checks basic requirements: file existence and importability.
"""

from pathlib import Path
from typing import Dict, Any
import sys

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import TRACKS_CSV, MODEL_FILE


def validate_model_files(tracks_path=None, model_path=None) -> Dict[str, Any]:
    """
    Check if model files exist and are accessible.
    
    Args:
        tracks_path (Path, optional): Path to tracks CSV
        model_path (Path, optional): Path to model file
        
    Returns:
        dict: Validation result with 'ok' (bool), 'missing' (list), 'error' (str)
    """
    # Use paths from centralized config
    if tracks_path is None:
        tracks_path = TRACKS_CSV
    if model_path is None:
        model_path = MODEL_FILE
    
    missing = []
    
    if not Path(tracks_path).exists():
        missing.append(f"tracks.csv at {tracks_path}")
    
    if not Path(model_path).exists():
        missing.append(f"model at {model_path}")
    
    if missing:
        return {
            "ok": False,
            "missing": missing,
            "error": f"Missing files: {', '.join(missing)}"
        }
    
    return {
        "ok": True,
        "missing": [],
        "tracks_path": str(tracks_path),
        "model_path": str(model_path)
    }


def validate_imports() -> Dict[str, Any]:
    """
    Check if required modules can be imported.
    
    Returns:
        dict: Import validation result
    """
    missing_imports = []
    
    try:
        import pandas
    except ImportError:
        missing_imports.append("pandas")
    
    try:
        import joblib
    except ImportError:
        missing_imports.append("joblib")
    
    try:
        from pathlib import Path
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / 'utils'))
        from feature_builder import build_pair_features
    except ImportError:
        missing_imports.append("feature_builder (local)")
    
    if missing_imports:
        return {
            "ok": False,
            "missing": missing_imports,
            "error": f"Cannot import: {', '.join(missing_imports)}"
        }
    
    return {
        "ok": True,
        "missing": []
    }


def quick_validate(tracks_path=None, model_path=None) -> bool:
    """
    Quick validation - returns True if everything is OK.
    
    Args:
        tracks_path (Path, optional): Path to tracks CSV
        model_path (Path, optional): Path to model file
        
    Returns:
        bool: True if files exist and imports work
    """
    files_ok = validate_model_files(tracks_path, model_path)
    imports_ok = validate_imports()
    
    return files_ok["ok"] and imports_ok["ok"]


if __name__ == "__main__":
    print("=" * 60)
    print("ML Model Validation")
    print("=" * 60)
    
    print("\n1. Checking files...")
    files = validate_model_files()
    if files["ok"]:
        print("   ✓ All files exist")
        print(f"   Tracks: {files['tracks_path']}")
        print(f"   Model: {files['model_path']}")
    else:
        print(f"   ✗ {files['error']}")
    
    print("\n2. Checking imports...")
    imports = validate_imports()
    if imports["ok"]:
        print("   ✓ All imports available")
    else:
        print(f"   ✗ {imports['error']}")
    
    print("\n" + "=" * 60)
    is_ready = files["ok"] and imports["ok"]
    print(f"Ready: {is_ready}")
    print("=" * 60)