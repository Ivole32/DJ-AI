"""
Export transitions from dataset.json to CSV.

This module extracts all track-to-track transitions from DJ mixes and counts their frequency.
Only includes transitions where both tracks have valid (non-null) IDs.
"""

import json
import csv
from pathlib import Path
from collections import defaultdict
import sys

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATASET_JSON, TRANSITIONS_CSV


def load_dataset(json_path):
    """
    Load the dataset from JSON file.
    
    Args:
        json_path (Path): Path to the dataset JSON file
        
    Returns:
        list: List of DJ mix dictionaries
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_transitions(dataset):
    """
    Extract all transitions from the dataset.
    
    A transition is defined as two consecutive tracks in a mix's tracklist.
    Only transitions where both tracks have valid IDs (not null) are included.
    
    Args:
        dataset (list): List of DJ mix dictionaries
        
    Returns:
        dict: Mapping from (from_track_id, to_track_id) tuples to frequency count
    """
    transition_counts = defaultdict(int)
    
    for mix in dataset:
        tracklist = mix.get('tracklist', [])
        
        # Iterate through consecutive pairs of tracks
        for i in range(len(tracklist) - 1):
            from_track = tracklist[i]
            to_track = tracklist[i + 1]
            
            from_id = from_track.get('id')
            to_id = to_track.get('id')
            
            # Only include transitions where both IDs are not null
            if from_id is not None and to_id is not None:
                transition_key = (from_id, to_id)
                transition_counts[transition_key] += 1
    
    return transition_counts


def export_to_csv(transition_counts, output_path):
    """
    Export transitions to CSV file.
    
    Args:
        transition_counts (dict): Dictionary mapping (from_id, to_id) tuples to counts
        output_path (Path): Path where the CSV file should be saved
    
    CSV Format:
        from_track_id, to_track_id, frequency
    """
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow(['from_track_id', 'to_track_id', 'frequency'])
        
        # Write transitions sorted by frequency (descending)
        for (from_id, to_id), count in sorted(
            transition_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        ):
            writer.writerow([from_id, to_id, count])


def main():
    """
    Main execution function.
    
    Loads the dataset, extracts transitions, and exports them to CSV.
    """
    # Use paths from centralized config
    dataset_path = DATASET_JSON
    output_path = TRANSITIONS_CSV
    
    print(f"Loading dataset from: {dataset_path}")
    dataset = load_dataset(dataset_path)
    print(f"Loaded {len(dataset)} mixes")
    
    print("Extracting transitions...")
    transition_counts = extract_transitions(dataset)
    print(f"Found {len(transition_counts)} unique transitions")
    
    total_transitions = sum(transition_counts.values())
    print(f"Total transitions (with frequency): {total_transitions}")
    
    print(f"Exporting to: {output_path}")
    export_to_csv(transition_counts, output_path)
    print("Export complete!")
    
    # Print some statistics
    if transition_counts:
        max_count = max(transition_counts.values())
        most_common = [(k, v) for k, v in transition_counts.items() if v == max_count]
        print(f"\nMost common transition(s) with frequency {max_count}:")
        for (from_id, to_id), count in most_common[:5]:
            print(f"  {from_id} -> {to_id}: {count}")


if __name__ == '__main__':
    main()