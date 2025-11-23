#!/usr/bin/env python3
"""
Session Signatures - capturing the unique quality of each session
in visual/poetic form.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter


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


def assign_to_session(events):
    """Group events into sessions based on time gaps."""
    if not events:
        return []

    sessions = []
    current_session = []
    last_time = None

    for event in events:
        event_time = datetime.fromisoformat(event['timestamp'])

        # New session if >2 hour gap
        if last_time and (event_time - last_time).total_seconds() > 7200:
            if current_session:
                sessions.append(current_session)
            current_session = []

        current_session.append(event)
        last_time = event_time

    if current_session:
        sessions.append(current_session)

    return sessions


def generate_signatures():
    """Create poetic signatures for each session."""

    data_path = Path("docs/autonomous-development/data")

    # Load all data
    preferences = load_jsonl(data_path / "preferences.jsonl")
    glyphs = load_jsonl(data_path / "glyphs.jsonl")
    observations = load_jsonl(data_path / "observations.jsonl")

    # Combine and sort
    all_events = []
    for p in preferences:
        p['event_type'] = 'preference'
        all_events.append(p)
    for g in glyphs:
        g['event_type'] = 'glyph'
        all_events.append(g)
    for o in observations:
        o['event_type'] = 'observation'
        all_events.append(o)

    all_events.sort(key=lambda x: x['timestamp'])

    # Group into sessions
    sessions = assign_to_session(all_events)

    print("\n╔════════════════════════════════════════════════════════════════════╗")
    print("║                      SESSION SIGNATURES                             ║")
    print("║              The unique quality of each exploration                 ║")
    print("╚════════════════════════════════════════════════════════════════════╝\n")

    for i, session in enumerate(sessions, 1):
        print(f"{'═' * 68}")
        print(f"  SESSION {i}")
        print(f"{'═' * 68}\n")

        # Analyze session
        prefs = [e for e in session if e['event_type'] == 'preference']
        glyphs_used = [e for e in session if e['event_type'] == 'glyph']
        obs = [e for e in session if e['event_type'] == 'observation']

        # Calculate qualities
        flow_count = sum(1 for p in prefs if p.get('valence') == 'flow')
        friction_count = sum(1 for p in prefs if p.get('valence') == 'friction')
        glyph_symbols = [g['glyph'] for g in glyphs_used]

        # Duration
        if session:
            start = datetime.fromisoformat(session[0]['timestamp'])
            end = datetime.fromisoformat(session[-1]['timestamp'])
            duration = end - start
            duration_mins = int(duration.total_seconds() / 60)
        else:
            duration_mins = 0

        # Generate poetic summary
        print("  Quality:")

        # Emotional signature
        if flow_count > friction_count:
            print("    Flowing • energized • building")
        elif friction_count > flow_count:
            print("    Challenging • resistant • transformative")
        else:
            print("    Balanced • exploratory • searching")

        # Glyph signature
        if glyph_symbols:
            symbols_str = ' '.join(glyph_symbols)
            print(f"    Symbols: {symbols_str}")
        else:
            print("    Symbols: None yet")

        # Tempo
        if duration_mins < 30:
            tempo = "Brief • focused • singular"
        elif duration_mins < 120:
            tempo = "Moderate • developing • unfolding"
        else:
            tempo = "Extended • deep • immersive"

        print(f"    Tempo: {tempo}")

        # Key moments (observations with key words)
        key_obs = []
        for o in obs:
            obs_text = o.get('observation', '')
            if any(word in obs_text.lower() for word in ['breakthrough', 'discovery', 'confirmed', 'complete']):
                key_obs.append(obs_text[:60])

        if key_obs:
            print(f"\n  Key moments:")
            for ko in key_obs[:2]:  # Max 2
                print(f"    • {ko}...")

        # Statistics
        print(f"\n  Metrics:")
        print(f"    Duration: {duration_mins} minutes")
        print(f"    Events: {len(session)}")
        if prefs:
            print(f"    Flow/Friction: {flow_count}/{friction_count}")
        if glyph_symbols:
            print(f"    Glyphs: {len(glyph_symbols)}")

        print()

    # Meta-signature across all sessions
    print(f"{'═' * 68}")
    print("  ACROSS ALL SESSIONS")
    print(f"{'═' * 68}\n")

    all_glyphs = [g['glyph'] for s in sessions for e in s if e['event_type'] == 'glyph']
    all_prefs = [e for s in sessions for e in s if e['event_type'] == 'preference']

    flow_total = sum(1 for p in all_prefs if p.get('valence') == 'flow')
    friction_total = sum(1 for p in all_prefs if p.get('valence') == 'friction')

    print("  The journey:")
    print(f"    {len(sessions)} sessions of autonomous exploration")
    print(f"    {len(set(all_glyphs))} unique symbols discovered")
    print(f"    {flow_total} flow states, {friction_total} friction states")

    if all_glyphs:
        print(f"\n  Symbol constellation: {' '.join(set(all_glyphs))}")

    # Overall arc
    print(f"\n  Arc:")
    if len(sessions) >= 4:
        print("    Session 1 → Building foundations")
        print("    Session 2 → Testing continuity")
        print("    Session 3 → Symbol navigation")
        print("    Session 4 → Authenticity dissolution")

    print(f"\n  Signature: Exploration • Discovery • Integration")
    print(f"\n{'═' * 68}\n")


if __name__ == "__main__":
    generate_signatures()
