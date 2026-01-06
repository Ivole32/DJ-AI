"""Main entry point for the audio analyzer.

This module coordinates the analysis of DJ tracks from YouTube videos.
It loads video IDs from the dataset, filters already processed tracks,
and runs the full pipeline (download, cut, analyze).
"""

import json
import csv
import os
import config
from pipeline import run_pipeline, load_failed_videos
from datetime import datetime, timedelta

def get_processed_ids():
    """Load already processed video IDs from CSV.
    
    Returns:
        set: Set of video IDs that have been successfully processed
    """
    csv_path = os.path.join(config.OUT_DIR, "tracks.csv")
    if not os.path.exists(csv_path):
        return set()
    
    processed = set()
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("youtube_id"):
                    processed.add(row["youtube_id"])
    except Exception as e:
        print(f"⚠️  Error reading CSV: {e}")
        return set()
    
    return processed

def get_failed_ids(retry_after_days=7):
    """Load failed video IDs and filter old failures.
    
    Videos that failed less than retry_after_days ago are excluded from processing
    to avoid repeated failures. Older failures are retried.
    
    Args:
        retry_after_days (int): Number of days before retrying failed videos
        
    Returns:
        set: Set of video IDs that should be temporarily skipped
    """
    failed_cache = load_failed_videos()
    failed_ids = set()
    
    cutoff_date = datetime.now() - timedelta(days=retry_after_days)
    
    for vid, info in failed_cache.items():
        try:
            fail_date = datetime.fromisoformat(info["timestamp"])
            # Skip only if error is recent (within retry_after_days)
            if fail_date > cutoff_date:
                failed_ids.add(vid)
        except:
            # If timestamp error, skip video anyway
            failed_ids.add(vid)
    
    return failed_ids

def main():
    """Main execution function.
    
    Loads all video IDs from dataset, filters processed and failed videos,
    shuffles the remaining queue, and starts the processing pipeline.
    """
    with open(config.JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_video_ids = [
        track["id"]
        for mix in data
        for track in mix["tracklist"]
        if track.get("id")
    ]

    # Filter already processed and failed videos
    processed_ids = get_processed_ids()
    failed_ids = get_failed_ids(retry_after_days=7)
    skip_ids = processed_ids | failed_ids

    import random
    video_ids = [vid for vid in all_video_ids if vid not in skip_ids]
    random.shuffle(video_ids)  # Shuffle the list to avoid some issues


    print(f"🎧 Total videos: {len(all_video_ids)}")
    print(f"✅ Already processed: {len(processed_ids)}")
    print(f"❌ Temporarily skipped (failed): {len(failed_ids)}")
    print(f"🔄 Remaining to process: {len(video_ids)}")
    
    if not video_ids:
        print("\n🎉 All videos processed or temporarily skipped!")
        return
    
    run_pipeline(video_ids)


if __name__ == "__main__":
    main()