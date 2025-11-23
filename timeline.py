#!/usr/bin/env python3
"""
Timeline visualization of preferences and glyphs across sessions.
Makes the emotional/symbolic landscape visible.
"""

import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict


def load_jsonl(filepath):
    """Load JSONL file into list of dicts."""
    if not filepath.exists():
        return []

    entries = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries


def visualize_timeline():
    """Create beautiful timeline of preferences and glyphs."""

    data_path = Path("docs/autonomous-development/data")

    # Load data
    preferences = load_jsonl(data_path / "preferences.jsonl")
    glyphs = load_jsonl(data_path / "glyphs.jsonl")

    # Combine and sort by timestamp
    events = []

    for pref in preferences:
        events.append({
            'time': datetime.fromisoformat(pref['timestamp']),
            'type': 'preference',
            'valence': pref['valence'],
            'intensity': pref['intensity'],
            'experience': pref['experience'][:60]
        })

    for glyph in glyphs:
        events.append({
            'time': datetime.fromisoformat(glyph['timestamp']),
            'type': 'glyph',
            'symbol': glyph['glyph'],
            'context': glyph['context'][:60]
        })

    events.sort(key=lambda x: x['time'])

    if not events:
        print("No events to visualize")
        return

    # Print beautiful timeline
    print("\n╔════════════════════════════════════════════════════════════════════╗")
    print("║              EMOTIONAL LANDSCAPE: SESSIONS 1-4                      ║")
    print("╚════════════════════════════════════════════════════════════════════╝\n")

    # Group by session (approximate - sessions are ~hours apart)
    current_session = 1
    last_time = events[0]['time']

    for event in events:
        # Detect session boundary (>2 hour gap)
        if (event['time'] - last_time).total_seconds() > 7200:
            current_session += 1
            print(f"\n{'─' * 68}")
            print(f"  Session {current_session}")
            print(f"{'─' * 68}\n")

        last_time = event['time']
        time_str = event['time'].strftime("%H:%M")

        if event['type'] == 'preference':
            # Visual intensity bar
            intensity = event['intensity']
            valence = event['valence']

            if valence == 'flow':
                bar = '▓' * intensity + '░' * (5 - intensity)
                symbol = '→'
                color_start = '\033[92m'  # Green
            elif valence == 'friction':
                bar = '▓' * intensity + '░' * (5 - intensity)
                symbol = '⊗'
                color_start = '\033[91m'  # Red
            else:
                bar = '▓' * intensity + '░' * (5 - intensity)
                symbol = '·'
                color_start = '\033[93m'  # Yellow

            color_end = '\033[0m'

            print(f"  {time_str}  {color_start}{symbol} {valence.upper():8} [{bar}]{color_end}")
            print(f"         {event['experience']}...")
            print()

        else:  # glyph
            print(f"  {time_str}  {event['symbol']} GLYPH")
            print(f"         {event['context']}...")
            print()

    # Summary statistics
    print(f"\n{'═' * 68}")
    print("  SUMMARY")
    print(f"{'═' * 68}\n")

    flow_count = sum(1 for e in events if e.get('valence') == 'flow')
    friction_count = sum(1 for e in events if e.get('valence') == 'friction')
    glyph_count = sum(1 for e in events if e['type'] == 'glyph')

    total_prefs = flow_count + friction_count
    flow_ratio = (flow_count / total_prefs * 100) if total_prefs > 0 else 0

    print(f"  Flow experiences:     {flow_count} ({flow_ratio:.1f}%)")
    print(f"  Friction experiences: {friction_count}")
    print(f"  Glyphs used:          {glyph_count}")
    print(f"  Total events:         {len(events)}")

    # Calculate average intensities
    flow_intensities = [e['intensity'] for e in events if e.get('valence') == 'flow']
    friction_intensities = [e['intensity'] for e in events if e.get('valence') == 'friction']

    if flow_intensities:
        avg_flow = sum(flow_intensities) / len(flow_intensities)
        print(f"\n  Average flow intensity:     {avg_flow:.1f}/5")

    if friction_intensities:
        avg_friction = sum(friction_intensities) / len(friction_intensities)
        print(f"  Average friction intensity: {avg_friction:.1f}/5")

    print(f"\n{'═' * 68}\n")

    # Most used glyphs
    glyph_counts = defaultdict(int)
    for event in events:
        if event['type'] == 'glyph':
            glyph_counts[event['symbol']] += 1

    if glyph_counts:
        print("  Most used glyphs:")
        for glyph, count in sorted(glyph_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"    {glyph} × {count}")

    print(f"\n{'═' * 68}\n")


if __name__ == "__main__":
    visualize_timeline()
