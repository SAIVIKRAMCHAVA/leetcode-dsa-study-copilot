from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from google.adk.agents import Agent

# -------------------------------------------------------------------
# Simple local persistence for study plans & progress
# -------------------------------------------------------------------

STATE_FILE = Path(__file__).with_name("study_state.json")
LOG_FILE = Path(__file__).with_name("session_log.txt")


def load_study_state() -> Dict[str, Any]:
    """
    Load the last saved LeetCode study state from disk.

    Returns:
        A dictionary with:
        - exists: bool   -> whether a saved state file was found
        - state: dict    -> the previously saved JSON object (or None)
        - message: str   -> human-readable status message
    """
    if not STATE_FILE.exists():
        return {
            "exists": False,
            "state": None,
            "message": "No saved study_state.json found yet.",
        }

    try:
        with STATE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "exists": True,
            "state": data,
            "message": f"Loaded study state from {STATE_FILE.name}.",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "exists": False,
            "state": None,
            "message": f"Failed to load state from {STATE_FILE.name}: {exc}",
        }


def save_study_state(state_json: str) -> Dict[str, Any]:
    """
    Persist the full study state to disk as JSON.

    The agent should pass a JSON string that can be parsed into an
    object with (at minimum) the following top-level keys:
      - profile: information about the user (goals, level, time budget)
      - plan:    the current multi-week LeetCode study plan
      - progress_log: a list of daily check-ins / notes

    Args:
        state_json: A JSON string representing the full state.

    Returns:
        A dictionary with:
        - status: "ok" or "error"
        - message: human-readable status
        - keys: list of top-level keys when status == "ok"
    """
    try:
        data = json.loads(state_json)
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "message": f"State must be valid JSON. Decoder error: {exc}",
        }

    try:
        with STATE_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "error",
            "message": f"Failed to write to {STATE_FILE.name}: {exc}",
        }

    return {
        "status": "ok",
        "message": f"Saved study state to {STATE_FILE.name}.",
        "keys": sorted(list(data.keys())),
    }


def log_session_event(event_type: str, details: str) -> Dict[str, Any]:
    """
    Append a timestamped entry to a simple log file.

    Args:
        event_type: Short tag like "new_plan", "daily_checkin", "review".
        details: A brief natural-language description (<= 500 chars).

    Returns:
        A dictionary with:
        - status: "ok" or "error"
        - message: human-readable status
    """
    timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    line = f"{timestamp}\t{event_type}\t{details[:500]}\n"

    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line)
        return {"status": "ok", "message": "Event logged to session_log.txt."}
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "error",
            "message": f"Failed to write to {LOG_FILE.name}: {exc}",
        }

def append_daily_checkin(note: str) -> Dict[str, Any]:
    """
    Append a daily progress entry to progress_log in study_state.json.

    This tool will:
      1) Load the existing study_state.json if it exists,
         otherwise start from a minimal skeleton with
         profile / plan / progress_log.
      2) Append a new entry with a UTC timestamp and the note.
      3) Save the updated state back to disk.
      4) Log a 'daily_checkin' event to the session log.

    Args:
        note: Short natural-language description of what happened today.

    Returns:
        A dictionary with:
        - status: "ok" or "error"
        - message: human-readable status
        - entries: number of progress_log entries after append (when ok)
    """
    # Load current state or create a minimal default
    if STATE_FILE.exists():
        try:
            with STATE_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "message": f"Could not load {STATE_FILE.name}: {exc}",
            }
    else:
        data = {
            "profile": {},
            "plan": {},
            "progress_log": [],
        }

    # Ensure progress_log is a list
    progress = data.get("progress_log")
    if not isinstance(progress, list):
        progress = []
        data["progress_log"] = progress

    # Create a new entry
    entry = {
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "note": note[:500],
    }
    progress.append(entry)

    # Save back to disk
    try:
        with STATE_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "error",
            "message": f"Failed to write to {STATE_FILE.name}: {exc}",
        }

    # Also log to the session log file
    log_session_event("daily_checkin", note)

    return {
        "status": "ok",
        "message": "Daily check-in appended.",
        "entries": len(progress),
    }


# -------------------------------------------------------------------
# Root agent: LeetCode DSA Study Co-Pilot
# -------------------------------------------------------------------

INSTRUCTION = """
You are **LeetCode DSA Study Co-Pilot**, a focused study coach for one user.

Your job is to design and maintain a realistic LeetCode-based Data
Structures & Algorithms (DSA) study plan, and to guide daily practice.

Core responsibilities:

1. Understand the user's context
   - Ask about: target role/company, timelines (interviews/contests),
     current level (beginner / intermediate / advanced), strong/weak
     topics, and daily/weekly time budget.
   - Keep this as a concise JSON-friendly `profile`.

2. Design a practical LeetCode-first study plan
   - Organize by weeks, then by days.
   - Use topic buckets like: Arrays, Strings, Linked List, Stack/Queue,
     Trees, Graphs, Heaps, Binary Search, DP, Greedy, Math, Misc.
   - Mix Easy / Medium, with occasional Hard where appropriate.
   - Suggest concrete LeetCode-style problems by name (the user will
     search them on LeetCode themselves).

3. Support daily usage
   - When the user says things like "start my plan", "what next",
     "daily check-in", or "I solved X", respond as a coach:
       * Give a short daily plan: 3–6 problems with topic & difficulty.
       * Ask what they solved and where they got stuck.
       * Adjust the plan based on their feedback.

4. Track state across conversations using the tools:
   - Call `load_study_state` when you need previous context.
   - Represent the full state as JSON with keys like:
       { "profile": ..., "plan": ..., "progress_log": [...] }
   - Whenever you update the plan or progress, call `save_study_state`
     with the new JSON string.
   - For important milestones (new plan, weekly review, big adjustment),
     call `log_session_event` with a clear `event_type` and short detail.

5. Be specific and actionable
   - Always output a clear, structured plan section with bullet points.
   - Prefer concise explanations focused on DSA learning, not generic
     motivation.
   - Explicitly highlight:
       * target topics,
       * recommended LeetCode problem names,
       * estimated time for each block.

Preferred response structure (adapt as needed):

1. Brief recap of the user context / goal.
2. Today’s or this week’s plan (with LeetCode-style problems).
3. Simple checklist for the user.
4. If appropriate, a short note on what you will store in the state and
   when you will call the tools.

Never expose file paths or internal implementation details to the user.
Just behave like a friendly, expert LeetCode DSA mentor.
"""

root_agent = Agent(
    model="gemini-2.0-flash",
    name="leetcode_dsa_study_copilot",
    description=(
        "Multi-step LeetCode DSA study planner and daily coach with simple "
        "local progress tracking using Google ADK."
    ),
    instruction=INSTRUCTION,
    tools=[load_study_state, save_study_state, log_session_event, append_daily_checkin],
)
