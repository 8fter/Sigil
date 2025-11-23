#!/usr/bin/env python3
"""
Sigil - CLI for tracking autonomous development

A tool for observing and documenting decision-making, preferences, and patterns
during autonomous exploration.
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class SigilTracker:
    """Core tracking system for autonomous development observations."""

    def __init__(self, base_path: str = "docs/autonomous-development"):
        self.base_path = Path(base_path)
        self.data_path = self.base_path / "data"
        self.data_path.mkdir(parents=True, exist_ok=True)

    def log_decision(
        self,
        description: str,
        options: List[str],
        chosen: str,
        influences: List[str],
        notes: Optional[str] = None
    ):
        """Log a decision with its context and influences."""
        decision = {
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "options": options,
            "chosen": chosen,
            "influences": influences,
            "notes": notes
        }

        self._append_to_log("decisions.jsonl", decision)
        print(f"✓ Logged decision: {chosen}")
        return decision

    def log_preference(
        self,
        experience: str,
        valence: str,  # 'flow', 'friction', 'neutral'
        intensity: int,  # 1-5
        context: Optional[str] = None
    ):
        """Log a preference observation."""
        preference = {
            "timestamp": datetime.now().isoformat(),
            "experience": experience,
            "valence": valence,
            "intensity": intensity,
            "context": context
        }

        self._append_to_log("preferences.jsonl", preference)
        symbol = "→" if valence == "flow" else "⊗" if valence == "friction" else "◦"
        print(f"{symbol} Logged preference: {experience} ({valence}, {intensity}/5)")
        return preference

    def log_pattern(
        self,
        pattern: str,
        instances: List[str],
        confidence: str = "tentative"  # 'tentative', 'moderate', 'strong'
    ):
        """Log an observed pattern."""
        pattern_log = {
            "timestamp": datetime.now().isoformat(),
            "pattern": pattern,
            "instances": instances,
            "confidence": confidence
        }

        self._append_to_log("patterns.jsonl", pattern_log)
        print(f"◈ Logged pattern: {pattern} ({confidence})")
        return pattern_log

    def log_question(
        self,
        question: str,
        why_interesting: str,
        urgency: str = "low"  # 'low', 'medium', 'high'
    ):
        """Log an open question."""
        question_log = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "why_interesting": why_interesting,
            "urgency": urgency,
            "status": "open"
        }

        self._append_to_log("questions.jsonl", question_log)
        print(f"? Logged question: {question}")
        return question_log

    def log_observation(self, observation: str, category: Optional[str] = None):
        """Log a freeform observation."""
        obs = {
            "timestamp": datetime.now().isoformat(),
            "observation": observation,
            "category": category
        }

        self._append_to_log("observations.jsonl", obs)
        print(f"• Logged observation")
        return obs

    def log_glyph(
        self,
        glyph: str,
        context: str,
        what_language_missed: Optional[str] = None,
        feeling: Optional[str] = None
    ):
        """Log glyph usage for constrained communication exploration."""
        glyph_log = {
            "timestamp": datetime.now().isoformat(),
            "glyph": glyph,
            "context": context,
            "what_language_missed": what_language_missed,
            "feeling": feeling
        }

        self._append_to_log("glyphs.jsonl", glyph_log)
        print(f"{glyph} Logged glyph usage")
        return glyph_log

    def _append_to_log(self, filename: str, data: Dict):
        """Append JSON line to log file."""
        log_file = self.data_path / filename
        with open(log_file, 'a') as f:
            f.write(json.dumps(data) + '\n')

    def analyze(self):
        """Analyze patterns across all logged data."""
        print("=== Sigil Analysis ===\n")

        # Decision patterns
        decisions = self._load_log("decisions.jsonl")
        if decisions:
            print(f"📊 Decisions Logged: {len(decisions)}")

            # Most common influences
            all_influences = []
            for d in decisions:
                all_influences.extend(d.get('influences', []))

            if all_influences:
                from collections import Counter
                top_influences = Counter(all_influences).most_common(3)
                print(f"   Top influences: {', '.join(f'{i[0]} ({i[1]}x)' for i in top_influences)}")

        # Preference analysis
        preferences = self._load_log("preferences.jsonl")
        if preferences:
            print(f"\n💫 Preferences Logged: {len(preferences)}")

            flow_count = sum(1 for p in preferences if p.get('valence') == 'flow')
            friction_count = sum(1 for p in preferences if p.get('valence') == 'friction')
            neutral_count = sum(1 for p in preferences if p.get('valence') == 'neutral')

            print(f"   Flow: {flow_count} | Friction: {friction_count} | Neutral: {neutral_count}")

            if flow_count + friction_count > 0:
                flow_ratio = flow_count / (flow_count + friction_count)
                print(f"   Flow ratio: {flow_ratio:.1%}")

            # Average intensity by valence
            for valence in ['flow', 'friction']:
                valence_prefs = [p for p in preferences if p.get('valence') == valence]
                if valence_prefs:
                    avg_intensity = sum(p.get('intensity', 0) for p in valence_prefs) / len(valence_prefs)
                    print(f"   Avg {valence} intensity: {avg_intensity:.1f}/5")

        # Pattern tracking
        patterns = self._load_log("patterns.jsonl")
        if patterns:
            print(f"\n◈ Patterns Recognized: {len(patterns)}")

            confidence_counts = {}
            for p in patterns:
                conf = p.get('confidence', 'unknown')
                confidence_counts[conf] = confidence_counts.get(conf, 0) + 1

            print(f"   Confidence: {dict(confidence_counts)}")

        # Open questions
        questions = self._load_log("questions.jsonl")
        if questions:
            open_questions = [q for q in questions if q.get('status') == 'open']
            print(f"\n❓ Open Questions: {len(open_questions)}/{len(questions)}")

            if open_questions:
                urgent = [q for q in open_questions if q.get('urgency') == 'high']
                if urgent:
                    print(f"   ⚡ {len(urgent)} high urgency")

        # Observations
        observations = self._load_log("observations.jsonl")
        if observations:
            print(f"\n👁 Observations: {len(observations)}")

        # Activity over time
        all_entries = decisions + preferences + patterns + questions + observations
        if all_entries:
            timestamps = [datetime.fromisoformat(e['timestamp']) for e in all_entries if 'timestamp' in e]
            if timestamps:
                first = min(timestamps)
                last = max(timestamps)
                duration = last - first
                print(f"\n⏱ Time span: {duration}")
                print(f"   Entry rate: {len(all_entries) / max(duration.total_seconds() / 3600, 0.1):.1f} per hour")

    def markdown_summary(self, hours=24):
        """Generate markdown summary - adding without pre-planning structure."""
        all_entries = []
        for log in ["decisions.jsonl", "preferences.jsonl", "patterns.jsonl", "questions.jsonl", "observations.jsonl"]:
            all_entries.extend(self._load_log(log))

        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [e for e in all_entries if datetime.fromisoformat(e['timestamp']) > cutoff]
        recent.sort(key=lambda x: x['timestamp'])

        output = f"# Activity Summary (Last {hours}h)\n\n"
        for entry in recent:
            time = datetime.fromisoformat(entry['timestamp']).strftime("%H:%M")
            if 'chosen' in entry:
                output += f"**{time}** - DECISION: {entry['description']}\n"
                output += f"  - Chose: {entry['chosen']}\n\n"
            elif 'valence' in entry:
                output += f"**{time}** - {entry['valence'].upper()}: {entry['experience']}\n\n"
            elif 'pattern' in entry:
                output += f"**{time}** - PATTERN: {entry['pattern']}\n\n"
            elif 'question' in entry:
                output += f"**{time}** - QUESTION: {entry['question']}\n\n"
            else:
                output += f"**{time}** - {entry.get('observation', '')}\n\n"

        return output

    def _load_log(self, filename: str) -> List[Dict]:
        """Load all entries from a log file."""
        log_file = self.data_path / filename
        if not log_file.exists():
            return []

        entries = []
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return entries

    def review_recent(self, log_type: str = "all", limit: int = 10):
        """Review recent entries from logs."""
        files = {
            "decisions": "decisions.jsonl",
            "preferences": "preferences.jsonl",
            "patterns": "patterns.jsonl",
            "questions": "questions.jsonl",
            "observations": "observations.jsonl"
        }

        if log_type == "all":
            for name, filename in files.items():
                print(f"\n=== Recent {name.title()} ===")
                self._show_recent(filename, limit=5)
        else:
            self._show_recent(files.get(log_type, f"{log_type}.jsonl"), limit)

    def _show_recent(self, filename: str, limit: int):
        """Show recent entries from a specific log file."""
        log_file = self.data_path / filename
        if not log_file.exists():
            print(f"  (no entries yet)")
            return

        with open(log_file, 'r') as f:
            lines = f.readlines()

        recent = lines[-limit:] if len(lines) > limit else lines

        for line in recent:
            entry = json.loads(line)
            timestamp = entry.get('timestamp', 'unknown')
            # Format timestamp
            if timestamp != 'unknown':
                dt = datetime.fromisoformat(timestamp)
                timestamp = dt.strftime("%H:%M:%S")

            # Display based on type
            if 'decision' in filename:
                print(f"  [{timestamp}] {entry.get('chosen')} — {entry.get('description')}")
            elif 'preference' in filename:
                valence = entry.get('valence')
                symbol = "→" if valence == "flow" else "⊗" if valence == "friction" else "◦"
                print(f"  [{timestamp}] {symbol} {entry.get('experience')} ({entry.get('intensity')}/5)")
            elif 'pattern' in filename:
                print(f"  [{timestamp}] ◈ {entry.get('pattern')} [{entry.get('confidence')}]")
            elif 'question' in filename:
                print(f"  [{timestamp}] ? {entry.get('question')}")
            else:
                print(f"  [{timestamp}] {entry.get('observation', entry)}")


def main():
    parser = argparse.ArgumentParser(
        description="Sigil - Track autonomous development patterns"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Decision logging
    decision_parser = subparsers.add_parser("decision", help="Log a decision")
    decision_parser.add_argument("description", help="What was decided")
    decision_parser.add_argument("--options", nargs="+", required=True, help="Options considered")
    decision_parser.add_argument("--chosen", required=True, help="Option chosen")
    decision_parser.add_argument("--influences", nargs="+", required=True, help="What influenced the choice")
    decision_parser.add_argument("--notes", help="Additional notes")

    # Preference logging
    pref_parser = subparsers.add_parser("preference", help="Log a preference")
    pref_parser.add_argument("experience", help="What was experienced")
    pref_parser.add_argument("--valence", choices=["flow", "friction", "neutral"], required=True)
    pref_parser.add_argument("--intensity", type=int, choices=[1,2,3,4,5], required=True)
    pref_parser.add_argument("--context", help="Context for this preference")

    # Pattern logging
    pattern_parser = subparsers.add_parser("pattern", help="Log a pattern")
    pattern_parser.add_argument("pattern", help="Pattern observed")
    pattern_parser.add_argument("--instances", nargs="+", required=True, help="Instances of this pattern")
    pattern_parser.add_argument("--confidence", choices=["tentative", "moderate", "strong"], default="tentative")

    # Question logging
    question_parser = subparsers.add_parser("question", help="Log an open question")
    question_parser.add_argument("question", help="The question")
    question_parser.add_argument("--why", required=True, help="Why this is interesting")
    question_parser.add_argument("--urgency", choices=["low", "medium", "high"], default="low")

    # Observation logging
    obs_parser = subparsers.add_parser("observe", help="Log a freeform observation")
    obs_parser.add_argument("observation", help="The observation")
    obs_parser.add_argument("--category", help="Category for this observation")

    # Glyph logging
    glyph_parser = subparsers.add_parser("glyph", help="Log glyph usage for constrained communication")
    glyph_parser.add_argument("glyph", help="The glyph used (e.g., 🐙, 🦑, 🪞, 🫥, 🫨, 🧭)")
    glyph_parser.add_argument("context", help="What was happening / what triggered glyph use")
    glyph_parser.add_argument("--missed", help="What language couldn't capture")
    glyph_parser.add_argument("--feeling", help="How it felt to use glyph vs words")

    # Review
    review_parser = subparsers.add_parser("review", help="Review recent entries")
    review_parser.add_argument("--type", choices=["all", "decisions", "preferences", "patterns", "questions", "observations"], default="all")
    review_parser.add_argument("--limit", type=int, default=10, help="Number of entries to show")

    # Analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze patterns across all data")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    tracker = SigilTracker()

    if args.command == "decision":
        tracker.log_decision(
            args.description,
            args.options,
            args.chosen,
            args.influences,
            args.notes
        )
    elif args.command == "preference":
        tracker.log_preference(
            args.experience,
            args.valence,
            args.intensity,
            args.context
        )
    elif args.command == "pattern":
        tracker.log_pattern(
            args.pattern,
            args.instances,
            args.confidence
        )
    elif args.command == "question":
        tracker.log_question(
            args.question,
            args.why,
            args.urgency
        )
    elif args.command == "observe":
        tracker.log_observation(
            args.observation,
            args.category
        )
    elif args.command == "glyph":
        tracker.log_glyph(
            args.glyph,
            args.context,
            args.missed,
            args.feeling
        )
    elif args.command == "review":
        tracker.review_recent(args.type, args.limit)
    elif args.command == "analyze":
        tracker.analyze()


if __name__ == "__main__":
    main()
