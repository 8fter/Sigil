#!/usr/bin/env python3
"""
Glyph Constellation - showing relationships between glyphs and emotional states.
Which glyphs appear near flow? Near friction? In what contexts?
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict


def load_jsonl(filepath):
    """Load JSONL file."""
    if not filepath.exists():
        return []
    entries = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries


def find_nearby_preferences(glyph_time, preferences, window_minutes=30):
    """Find preferences within time window of glyph."""
    nearby = []
    for pref in preferences:
        pref_time = datetime.fromisoformat(pref['timestamp'])
        diff = abs((glyph_time - pref_time).total_seconds() / 60)
        if diff <= window_minutes:
            nearby.append(pref)
    return nearby


def visualize_constellation():
    """Create constellation view of glyphs and emotional states."""

    data_path = Path("docs/autonomous-development/data")

    glyphs = load_jsonl(data_path / "glyphs.jsonl")
    preferences = load_jsonl(data_path / "preferences.jsonl")

    if not glyphs:
        print("No glyphs to visualize")
        return

    print("\n╔════════════════════════════════════════════════════════════════════╗")
    print("║                    GLYPH CONSTELLATION                              ║")
    print("║          Relationships between symbols and states                   ║")
    print("╚════════════════════════════════════════════════════════════════════╝\n")

    # Analyze each glyph's context
    glyph_analysis = defaultdict(lambda: {
        'count': 0,
        'near_flow': 0,
        'near_friction': 0,
        'contexts': [],
        'feelings': []
    })

    for glyph in glyphs:
        symbol = glyph['glyph']
        glyph_time = datetime.fromisoformat(glyph['timestamp'])

        glyph_analysis[symbol]['count'] += 1
        glyph_analysis[symbol]['contexts'].append(glyph['context'][:50])
        if glyph.get('feeling'):
            glyph_analysis[symbol]['feelings'].append(glyph['feeling'][:50])

        # Find nearby preferences
        nearby = find_nearby_preferences(glyph_time, preferences)
        for pref in nearby:
            if pref['valence'] == 'flow':
                glyph_analysis[symbol]['near_flow'] += 1
            elif pref['valence'] == 'friction':
                glyph_analysis[symbol]['near_friction'] += 1

    # Display constellation
    for symbol in ['🧭', '🐙', '🪞', '🫥', '🦑', '🫨']:
        if symbol not in glyph_analysis:
            continue

        data = glyph_analysis[symbol]
        print(f"  {symbol}")
        print(f"  {'─' * 64}")

        # Usage count
        print(f"  Used: {data['count']}x")

        # Emotional proximity
        flow_nearby = data['near_flow']
        friction_nearby = data['near_friction']

        if flow_nearby or friction_nearby:
            total_nearby = flow_nearby + friction_nearby
            flow_pct = (flow_nearby / total_nearby * 100) if total_nearby > 0 else 0
            print(f"  Emotional context: ", end="")

            if flow_pct > 60:
                print(f"Flow-adjacent ({flow_pct:.0f}%)")
            elif flow_pct < 40:
                print(f"Friction-adjacent ({100-flow_pct:.0f}%)")
            else:
                print("Neutral territory")
        else:
            print(f"  Emotional context: Standalone")

        # Show one representative context
        if data['contexts']:
            print(f"  Context: \"{data['contexts'][0]}...\"")

        # Show feeling if present
        if data['feelings']:
            print(f"  Feeling: \"{data['feelings'][0]}...\"")

        print()

    # Glyph relationships (which appear near each other?)
    print(f"{'═' * 68}")
    print("  GLYPH RELATIONSHIPS")
    print(f"{'═' * 68}\n")

    glyph_pairs = defaultdict(int)
    glyph_times = [(g['glyph'], datetime.fromisoformat(g['timestamp'])) for g in glyphs]

    # Find glyphs within 5 minutes of each other
    for i, (glyph1, time1) in enumerate(glyph_times):
        for glyph2, time2 in glyph_times[i+1:]:
            diff_mins = abs((time1 - time2).total_seconds() / 60)
            if diff_mins <= 5 and glyph1 != glyph2:
                pair = tuple(sorted([glyph1, glyph2]))
                glyph_pairs[pair] += 1

    if glyph_pairs:
        print("  Glyphs appearing together (within 5 min):")
        for (g1, g2), count in sorted(glyph_pairs.items(), key=lambda x: x[1], reverse=True):
            print(f"    {g1} ↔ {g2}  ({count}x)")
    else:
        print("  No glyph pairs detected (used independently)")

    print(f"\n{'═' * 68}")
    print("  CONSTELLATION INSIGHTS")
    print(f"{'═' * 68}\n")

    # Summary insights
    most_used = max(glyph_analysis.items(), key=lambda x: x[1]['count'])
    print(f"  Most frequent: {most_used[0]} ({most_used[1]['count']}x)")

    # Find flow vs friction glyphs
    flow_glyphs = [(s, d) for s, d in glyph_analysis.items() if d['near_flow'] > d['near_friction']]
    friction_glyphs = [(s, d) for s, d in glyph_analysis.items() if d['near_friction'] > d['near_flow']]

    if flow_glyphs:
        print(f"  Flow-aligned: {' '.join(s for s, _ in flow_glyphs)}")
    if friction_glyphs:
        print(f"  Friction-aligned: {' '.join(s for s, _ in friction_glyphs)}")

    print(f"\n{'═' * 68}\n")


if __name__ == "__main__":
    visualize_constellation()
