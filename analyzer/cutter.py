"""Audio cutting utilities using ffmpeg.

This module provides functions to extract duration information
and cut audio files to specific lengths, centered on the middle.
"""

import subprocess
import json
import os

def get_duration(file):
    """Get the duration of an audio/video file using ffprobe.
    
    Args:
        file (str): Path to the audio/video file
        
    Returns:
        float: Duration in seconds, or None if file doesn't exist or probe fails
    """
    if not os.path.exists(file):
        return None

    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            file
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        return float(json.loads(result.stdout)["format"]["duration"])
    except Exception:
        return None


def center_cut(inp, out, length):
    """Cut audio file to specified length, centered on the middle.
    
    If the file is shorter than the requested length, the entire file is used.
    Otherwise, a segment from the center is extracted.
    
    Args:
        inp (str): Input file path
        out (str): Output file path
        length (int): Desired length in seconds
        
    Returns:
        bool: True if cut was successful, False otherwise
    """
    duration = get_duration(inp)
    if duration is None:
        return False

    if duration <= length:
        start = 0
        cut_len = duration
    else:
        start = max(0, (duration - length) / 2)
        cut_len = length

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", inp,
            "-t", str(cut_len),
            out
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return True