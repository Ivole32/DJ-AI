"""Audio analysis pipeline.

This module coordinates the full workflow:
1. Download audio from YouTube
2. Cut to configured length (center segment)
3. Analyze BPM, key, energy using librosa
4. Save results to CSV and JSON

Uses multi-threading for downloads and multi-processing for analysis.
"""

import os
import json
import csv
import threading
import subprocess
from queue import Queue
from multiprocessing import Pool
from tqdm import tqdm
import time
import random
from datetime import datetime

import multiprocessing as mp
mp.freeze_support()

import config
from cutter import center_cut
from analyzer import analyze_audio


download_q = Queue()
analyze_q = Queue()
result_q = Queue()
failure_q = Queue()


# =========================
# FAILURE CACHE
# =========================
def get_failure_cache_path():
    return os.path.join(config.OUT_DIR, "failed_videos.json")

def load_failed_videos():
    """Load failed videos from cache.
    
    Returns:
        dict: Dictionary mapping video IDs to failure information
    """
    cache_path = get_failure_cache_path()
    if not os.path.exists(cache_path):
        return {}
    
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_failed_video(video_id, error_msg):
    """Save a failed video to the cache.
    
    Args:
        video_id (str): YouTube video ID
        error_msg (str): Error description
    """
    failure_q.put((video_id, error_msg))

def failure_writer():
    """Background thread that persists failures to disk."""
    cache_path = get_failure_cache_path()
    failed_cache = load_failed_videos()
    
    while True:
        item = failure_q.get()
        if item is None:
            break
        
        video_id, error_msg = item
        failed_cache[video_id] = {
            "error": error_msg,
            "timestamp": datetime.now().isoformat(),
            "attempts": failed_cache.get(video_id, {}).get("attempts", 0) + 1
        }
        
        # Save immediately
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(failed_cache, f, indent=2)
        except Exception as e:
            print(f"\n⚠️  Could not save failure cache: {e}")
        
        failure_q.task_done()

# =========================
# DOWNLOAD WORKER
# =========================
def download_worker(pbar):
    error_count = 3
    while True:
        vid = download_q.get()
        if vid is None:
            break

        raw = os.path.join(config.TMP_DIR, f"{vid}.wav")
        cut = os.path.join(config.TMP_DIR, f"{vid}_cut.wav")

        try:
            # Download (use python -m to ensure correct version)
            result = subprocess.run(
                [
                    "python", "-m", "yt_dlp",
                    #"-U",
                    "--ignore-errors",
                    "-f", "bestaudio",
                    "--extract-audio",
                    "--js-runtime", "node",
                    "--audio-format", "wav",
                    "--compat-options", "no-youtube-unavailable-videos",
                    #"--extractor-args", "youtube:player_client=android",
                    "-o", raw,
                    f"https://www.youtube.com/watch?v={vid}"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )

            # Check if file exists
            if not os.path.exists(raw):
                error_msg = "Download failed - file not found"
                print(f"\n⚠️  {error_msg}: {vid}")
                save_failed_video(vid, error_msg)
                pbar.update(1)
                download_q.task_done()
                continue

            # Cut audio
            if center_cut(raw, cut, config.CUT_LENGTH):
                analyze_q.put((vid, cut))
            else:
                error_msg = "Cut failed"
                print(f"\n⚠️  {error_msg}: {vid}")
                save_failed_video(vid, error_msg)

            # Cleanup raw file
            try:
                os.remove(raw)
            except:
                pass

        except subprocess.CalledProcessError as e:
            # Handle encoding errors in stderr
            try:
                error_msg = f"Download error: {e.stderr.decode('utf-8', errors='replace')[:100]}"
            except:
                error_msg = f"Download error: Exit code {e.returncode}"
            
            if error_count > 1:
                print(f"\n❌ {vid}: {error_msg}")
                error_count = 0
            else:
                error_count += 1

            save_failed_video(vid, error_msg)
        except Exception as e:
            if error_count > 1:
                error_msg = f"Error: {str(e)}"
                print(f"\n❌ {vid}: {error_msg}")
                error_count = 0
            else:
                error_count += 1
            save_failed_video(vid, error_msg)

        pbar.update(1)

        time.sleep(random.uniform(0.5, 1.5))

        download_q.task_done()


# =========================
# ANALYZE PROCESS
# =========================
def analyze_worker(args):
    vid, path = args
    try:
        if not os.path.exists(path):
            error_msg = "File missing for analysis"
            print(f"\n⚠️  {error_msg}: {vid}")
            save_failed_video(vid, error_msg)
            return None
        
        data = analyze_audio(path)
        data["youtube_id"] = vid
        
        # Cleanup cut file after analysis
        try:
            os.remove(path)
        except:
            pass
        
        return data
    except Exception as e:
        error_msg = f"Analyze error: {str(e)}"
        print(f"\n❌ {vid}: {error_msg}")
        save_failed_video(vid, error_msg)
        return None


# =========================
# RESULT WRITER
# =========================
def writer_worker(total):
    """Background thread that writes analysis results to CSV.
    
    Receives results from the result queue, deduplicates by ID,
    and appends to the output CSV file.
    
    Args:
        total (int): Total number of tracks expected
    """
    csv_path = os.path.join(config.OUT_DIR, "tracks.csv")

    results = []

    analyze_bar = tqdm(
        total=total,
        desc="🧠 Analysis",
        unit="track",
        position=1
    )

    # Load existing IDs to avoid duplicates
    existing_ids = set()
    file_exists = os.path.exists(csv_path)
    needs_header = not file_exists or os.path.getsize(csv_path) == 0
    
    if file_exists and os.path.getsize(csv_path) > 0:
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                existing_ids = {row["youtube_id"] for row in reader}
        except Exception as e:
            print(f"⚠️  Warning: Could not read existing IDs: {e}")

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["youtube_id", "bpm", "key", "camelot", "energy"]
        )
        if needs_header:
            writer.writeheader()

        while True:
            item = result_q.get()
            if item is None:
                break

            # Check if ID already exists
            if item["youtube_id"] not in existing_ids:
                writer.writerow(item)
                f.flush()
                results.append(item)
                existing_ids.add(item["youtube_id"])
            
            analyze_bar.update(1)
            result_q.task_done()

    analyze_bar.close()
    
    print(f"\n✅ Done! {len(results)} new tracks analyzed and saved.")


# =========================
# PIPELINE START
# =========================
def run_pipeline(video_ids):
    """Run the complete analysis pipeline.
    
    Coordinates download threads, analysis processes, and result writing.
    Progress is displayed using tqdm progress bars.
    
    Args:
        video_ids (list): List of YouTube video IDs to process
    """
    total = len(video_ids)

    download_bar = tqdm(
        total=total,
        desc="📥 Download",
        unit="track",
        position=0
    )

    # Fill queue
    for vid in video_ids:
        download_q.put(vid)

    # Download threads
    for _ in range(config.DOWNLOAD_THREADS):
        threading.Thread(
            target=download_worker,
            args=(download_bar,),
            daemon=True
        ).start()

    # Writer
    writer_thread = threading.Thread(
        target=writer_worker,
        args=(total,),
        daemon=True
    )
    writer_thread.start()

    # Failure writer
    failure_thread = threading.Thread(
        target=failure_writer,
        daemon=True
    )
    failure_thread.start()

    # Start analyzer pool in background
    def analyzer_loop():
        with Pool(config.ANALYZE_PROCESSES) as pool:
            while True:
                try:
                    item = analyze_q.get(timeout=2)
                    if item is None:
                        break
                    pool.apply_async(
                        analyze_worker,
                        (item,),
                        callback=lambda r: result_q.put(r) if r else None
                    )
                except:
                    # Check if downloads are done
                    if download_q.unfinished_tasks == 0 and analyze_q.empty():
                        break
            pool.close()
            pool.join()
        # Signal writer to stop
        result_q.put(None)
    
    analyzer_thread = threading.Thread(target=analyzer_loop, daemon=True)
    analyzer_thread.start()

    # Wait for downloads to complete
    download_q.join()
    
    # Stop download threads
    for _ in range(config.DOWNLOAD_THREADS):
        download_q.put(None)
    
    download_bar.close()
    
    # Signal analyzer to check for completion
    analyze_q.put(None)
    
    # Wait for analyzer and writer to finish
    analyzer_thread.join()
    writer_thread.join(timeout=10)
    
    # Stop failure writer
    failure_q.put(None)
    failure_thread.join(timeout=5)