# LeetCode DSA Study Co-Pilot (Google ADK)

An AI-powered **study companion for LeetCode data structures & algorithms (DSA)**, built with the **Google AI Agent Development Kit (ADK)** in Python.

The agent helps you:

- Design a **4-week DSA study plan** tailored to your profile.
- **Persist your study state** locally as JSON (`profile`, `plan`, `progress_log`).
- Track your progress through **daily check-ins** (what you solved, what’s pending).

Everything runs **locally** using your **Google API key**. No Google Cloud billing or deployment is required.

---

## 1. Project Overview

### Goal

Support a DSA learner (especially preparing for **product-based company interviews**) by:

1. Understanding their **current level**, **timeline**, and **time budget**.
2. Generating a **structured 4-week LeetCode plan** (topics + daily problem sets).
3. Persisting their **profile, plan, and progress** across sessions.
4. Making **daily check-ins** easy and consistent, so they always know:
   - What they should do today,
   - What they already completed,
   - Where they are stuck.

### Key Features

- **LeetCode-focused planning**: Arrays/Strings, Linked Lists, Trees/Graphs, Dynamic Programming.
- **Stateful**: Uses a local JSON file to save `profile`, `plan`, and `progress_log`.
- **Daily progress logging**: Appends entries such as _“Solved Two Sum and Valid Palindrome but not Reverse String”_ with timestamps.
- **Natural language interface**: You just chat in plain English from the terminal.

---

## 2. Architecture

### 2.1 High-Level

- **Google ADK LLM Agent** (root agent)

  - Backed by a Gemini model (configured when `adk create` was run; e.g., `gemini-2.5-flash`).
  - Knows the user’s context (profile, plan, time budget).
  - Can call **tools** to read/write local JSON files and log events.

- **Tools (Python functions wrapped via ADK)**
  - `load_study_state`  
    Reads a local JSON file (e.g., `study_state.json`) and returns:
    ```json
    {
      "profile": { ... },
      "plan": { ... },
      "progress_log": [ ... ]
    }
    ```
  - `save_study_state`  
    Writes the full JSON state back to disk.
  - `append_daily_checkin` / logging helpers  
    Adds an entry to `progress_log` including a timestamp and human-readable note.
  - `log_event`  
    Optionally writes a short event line to a text log (e.g., `session_log.txt`) for debugging / auditing.

The agent uses these tools in combination with natural language instructions to implement three flows: **A. Plan Design**, **B. State Management**, **C. Daily Check-ins**.

### 2.2 Local State Format

The state is a JSON file, for example `study_copilot_agent/study_state.json`, with this structure:

```json
{
  "profile": {
    "level": "intermediate",
    "timeline": "3 months",
    "time_budget": "2 hours per day",
    "target_role": "product-based interviews",
    "strong_topics": [],
    "weak_topics": []
  },
  "plan": {
    "week_1": { "...": "..." },
    "week_2": { "...": "..." },
    "week_3": { "...": "..." },
    "week_4": { "...": "..." }
  },
  "progress_log": [
    {
      "timestamp": "2025-11-27T13:55:45Z",
      "note": "Solved Two Sum and Valid Palindrome but not Reverse String."
    }
  ]
}
```
