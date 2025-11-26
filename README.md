# LeetCode DSA Study Co-Pilot

This project is my capstone submission for the **Agents Intensive – Capstone Project** on Kaggle.  
It is built using **Google ADK (Python)** and implements a **multi-agent LeetCode DSA study coach** that plans practice, tracks progress, and adjusts daily goals over time.

## Capstone Context

- **Track:** Concierge Agents
- **Goal:** Help an individual prepare for LeetCode / DSA interviews more efficiently by automating planning and progress tracking.
- **Key agent concepts used (for the capstone rubric):**
  - Multi-agent system (planner, check-in, adjuster agents)
  - Tools (custom tools for saving/loading plans and progress)
  - Sessions & memory (persistent user profile + study history)
  - Observability (logging and traces via ADK)
  - Deployment (agent deployed using Google ADK tooling)

## Problem Statement

Preparing for coding interviews on platforms like LeetCode is time-consuming and hard to plan.  
Many learners:

- Don’t know which topics to focus on each week,
- Struggle to balance easy/medium/hard problems,
- Lose track of what they actually solved,
- And rarely adjust their plan based on real progress.

The **LeetCode DSA Study Co-Pilot** acts as a personal planning and tracking assistant for LeetCode-style practice.

## Solution Overview

The agent:

- Collects the user’s goals (target company/timeline), current level, and daily available time.
- Generates a **weekly topic + problem-count plan** (e.g., “Mon: 2 Easy + 1 Medium Array, Tue: …”).
- Runs daily check-ins to log how many problems were actually solved and in which topics.
- Adjusts the upcoming plan when the user falls behind or struggles with certain topics.
- Persists user profile, plans, and progress across sessions.

## Architecture (High Level)

- **Root Agent:** Orchestrates the overall conversation and delegates to sub-agents.
- **GoalSettingAgent:** Gathers initial profile and LeetCode goals.
- **PlannerAgent:** Creates or updates the weekly plan by topic and difficulty.
- **DailyCheckinAgent:** Records daily progress from the user.
- **AdjusterAgent:** Compares planned vs actual work and rebalances the schedule.

**Tools (planned):**

- `save_profile_and_plan` – stores user profile, active plan, and history.
- `load_profile_and_plan` – retrieves stored state for the current session.
- `log_event` – writes simple logs (for observability).

**Memory and Storage:**

- Lightweight JSON/SQLite store in the project folder (ignored by git).
- ADK session state for short-term context within a conversation.

As the implementation is completed, this section will be updated with more detailed architecture and diagrams.

## Project Structure

- `study_copilot_agent/`
  - `agent.py` – root agent definition (will orchestrate sub-agents and tools).
  - `__init__.py` – package initializer.
  - `.env` – environment variables for local development (not committed).
- `.gitignore` – excludes `.venv`, `.env`, logs, etc.
- `.venv/` – local virtual environment (not committed).

## Getting Started (Local Development)

### Prerequisites

- Python 3.10+ installed
- A Google AI Studio (Gemini) API key

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/SAIVIKRAMCHAVA/leetcode-dsa-study-copilot.git
   cd leetcode-dsa-study-copilot
   ```

2. Create and activate a virtual environment (example for Windows):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install google-adk
   ```

4. Configure your API key:
   Create a file named `.env` inside `study_copilot_agent/` with:
   ```bash
   GOOGLE_API_KEY=your_api_key_here
   ```
   Note: Do NOT commit this file. It is already listed in `.gitignore`.

### Running the Agent

From the project root:

```bash
adk run study_copilot_agent
```

You can then chat with the agent in the terminal.

(Later, this section will be expanded with specific prompts for creating a new study plan, checking in daily, etc.)
