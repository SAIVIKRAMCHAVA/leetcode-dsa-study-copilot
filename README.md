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

The exact plan contents are generated dynamically by the agent, but the keys (`profile`, `plan`, `progress_log`) are fixed.

---

## 3. Setup & Running Locally (Windows)

This section shows how to run the agent locally using Python and Google ADK.

### 3.1 Prerequisites

- Windows 10/11
- Python 3.10+ installed and on your PATH (`python --version`)
- A Google API key from [Google AI Studio](https://aistudio.google.com)  
  (used only as `GOOGLE_API_KEY` in a `.env` file)

### 3.2 Clone the repository

```bash
git clone https://github.com/SAIVIKRAMCHAVA/leetcode-dsa-study-copilot.git
cd leetcode-dsa-study-copilot
```

### 3.3 Create and activate a virtual environment (Windows)

```bash
python -m venv .venv
.venv\Scripts\activate
```

When the venv is active, your prompt will start with `(.venv)`.

### 3.4 Install dependencies

```bash
pip install google-adk
```

If a `requirements.txt` file is present, you may also use:

```bash
pip install -r requirements.txt
```

### 3.5 Configure the Google API key

Inside the `study_copilot_agent/` folder there is a `.env` file.  
Open it and set your API key:

```text
GOOGLE_API_KEY=your_api_key_here
```

Notes:

- This file is already listed in `.gitignore`, so it is not committed to GitHub.
- The ADK will automatically read this environment variable when the agent runs.

### 3.6 Run the LeetCode DSA Study Co-Pilot agent

From the project root (`leetcode-dsa-study-copilot`):

```bash
adk run study_copilot_agent
```

You should see:

```text
Running agent leetcode_dsa_study_copilot, type exit to exit.
[user]:
```

You can now start chatting with the agent in the terminal.  
Type `exit` and press Enter to stop the agent.

---

## 4. Usage Scenarios (Flows A, B, C)

The agent is primarily designed around three core flows that match the capstone project requirements.

### 4.1 Flow A – Design a 4-Week LeetCode DSA Plan

**Goal:** Given the user’s level and constraints, create a structured 4-week DSA plan, 2 hours per day.

**Example prompt:**

```text
[user]: I’m intermediate, preparing for product-based interviews in 3 months. I can study 2 hours per day. Help me design a 4-week LeetCode DSA plan.
```

**What the agent does:**

- Clarifies / confirms:
  - Level (e.g., intermediate)
  - Target (product-based SWE interviews)
  - Time budget (2 hours/day)
  - Timeline (3 months overall, 4-week focused plan)
- Generates a plan such as:
  - **Week 1:** Arrays & Strings
  - **Week 2:** Linked Lists
  - **Week 3:** Trees & Graphs
  - **Week 4:** Dynamic Programming
- For each day, suggests **3–6 LeetCode problems** (mix of Easy/Medium/Hard) aligned to the topic.  
  The plan is later persisted in JSON via Flow B.

### 4.2 Flow B – Persist Study State (`profile`, `plan`, `progress_log`)

**Goal:** Load or create a resilient study state file so the agent remembers you across sessions.

**Example prompt:**

```text
[user]: I am intermediate, preparing for product-based interviews in 3 months, and can study 2 hours per day. Please do the following in order:
1) Load any existing study state using your tools.
2) If none exists, create a new JSON state with keys profile, plan, and progress_log.
3) Save that full JSON state using your save_study_state tool.
4) Log an event that a new 4-week plan was created.
```

**What the agent does:**

1. Calls `load_study_state`:
   - If `study_state.json` exists, loads it.
   - If not, starts with an empty structure.
2. If no plan is present:
   - Calls the planning logic from Flow A to create a new 4-week LeetCode plan.
3. Builds a JSON object with:
   - `profile` → derived from the prompt
   - `plan` → daily schedule with LeetCode problems
   - `progress_log` → an empty list `[]` if this is the first run
4. Calls `save_study_state` to write the full JSON to disk.
5. Calls `log_event` to record something like:
   - `"event": "created_new_plan"` with a timestamp.  
     This makes the agent stateful: when you close and reopen it, it can continue from where you left off.

### 4.3 Flow C – Daily Check-ins and Progress Logging

**Goal:** Append structured daily updates to progress_log so you can track your streak and unfinished problems.

**Example prompt:**

```bash
[user]: Please load my existing study state, add a daily check-in that today I solved Two Sum and Valid Palindrome but not Reverse String, then save the updated state and log a daily_checkin event.
```

**What the agent does:**

1. Calls `load_study_state` to get the latest JSON.
2. Constructs a note like:
   - `"Solved Two Sum and Valid Palindrome but not Reverse String."`
3. Appends a new entry to `progress_log`:

```json
{
  "timestamp": "2025-11-27T13:55:45Z",
  "note": "Solved Two Sum and Valid Palindrome but not Reverse String."
}
```

4. Calls `save_study_state` again to persist the updated state.

5. Calls `log_event` with something like `"event": "daily_checkin"`.

You can verify the update by opening `study_copilot_agent/study_state.json` in VS Code.

---

## 5. Example “What Should I Do Today?” Flow

The agent can also answer questions like “What should I do today?” based on your plan and progress.

**Example prompt:**

```text
[user]: Please load my existing study state and tell me exactly what I should do today in 2 hours, based on my current 4-week plan and progress so far. Give me topics and 3–6 LeetCode problems.
```

**Expected behavior:**

- Loads `study_state.json`.
- Determines today’s date and which week/day of the plan you are on.
- Factors in `progress_log` (e.g., incomplete problems like “Reverse String”).
- Responds with, for example:
  - **Topic:** Arrays and Strings
  - **Today’s problems:**
    - Finish “Reverse String (Easy)”
    - “Group Anagrams (Medium)” (retry if needed)
    - “Longest Substring Without Repeating Characters (Medium)”

This makes the agent behave like a personal DSA coach that always knows your next step.

---

## 6. Project Structure

Simplified layout of the repository:

```text
leetcode-dsa-study-copilot/
├─ README.md                  # This file – project overview & setup
├─ .gitignore                 # Ignores venv, .env, state files, etc.
├─ study_copilot_agent/
│  ├─ __init__.py
│  ├─ agent.py                # Main ADK agent definition + tools
│  ├─ .env                    # Holds GOOGLE_API_KEY (not committed)
│  ├─ study_state.json        # Created at runtime to store profile/plan/progress
│  └─ session_log.txt         # Optional text log of events / runs
└─ .venv/                     # Local virtual environment (not committed)
```

---

## 7. Limitations & Future Work

**Current Limitations**

- **Local JSON only:** State is stored in a single JSON file; no database or sync across devices.
- **LeetCode problems are referenced by name** only; the agent does not integrate with the LeetCode API.
- **Static 4-week horizon:** The initial design is optimized for a 4-week plan; longer horizons are possible but not deeply customized yet.

**Possible Extensions**

- Add **topic-wise analytics** (which areas you are strong/weak in, based on progress_log).
- Integrate with LeetCode contest schedules and add **contest reminders**.
- Add support for **company-specific ladders** (e.g., “Google-style questions”, “Meta-style questions”).
- Provide a **simple web UI** (e.g., Streamlit / FastAPI frontend) on top of the same ADK agent.

---

## 8. How This Fits the Capstone Requirements

- Uses the **Google AI Agent Development Kit (ADK)** in Python.
- Implements a **stateful agent** with:
  - Non-trivial tools (`load_study_state`, `save_study_state`, progress logging).
  - Multi-step flows (plan creation, state persistence, daily check-ins).
- Provides a clear local-only run path documented in `README.md`.
- Tracks user behavior (progress log) to adapt future recommendations.

---

## 9. Acknowledgements

- **Google AI Agent Development Kit (ADK)** for the agent runtime and tooling.
- **Gemini models** (via `GOOGLE_API_KEY`) for the underlying LLM capabilities.
- The **LeetCode** community for the extensive set of DSA problems that this project recommends (problem names are used for educational reference only).
