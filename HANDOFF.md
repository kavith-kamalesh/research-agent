# MASTER HANDOFF DOCUMENT
Paste this into any AI assistant to resume work instantly.

## WHO I AM
I go by "Quite Leverage" (real name Kavith Kamalesh). I'm a 2nd-year B.E. Electronics 
and Communication Engineering student at Dr. Mahalingam College of Engineering and 
Technology, India. I build across the full stack — embedded systems, robotics, backend 
infrastructure, frontend, and AI orchestration. I'm oriented toward hackathons and 
startup ideation, not just coursework.

GitHub: github.com/kavith-kamalesh
Instagram: quite.leverage | LinkedIn: quite-leverage | Gmail: leveragequite@gmail.com

## MY HARDWARE/ENVIRONMENT
- MacBook Air M2, 8GB RAM (recurring constraint on running heavy toolchains simultaneously)
- VS Code with Blackbox AI extension
- Obsidian as research/notes vault
- Have used Antigravity IDE and Manus AI
- Python via venv, Python 3.12 specifically (3.14 breaks numpy builds on this setup)
- zsh shell on macOS

## MY WORKING STYLE (important for how to help me)
- I iterate live on a running system, not in a separate dev/test branch — I ask for a 
  feature, test it immediately, report exact behavior back including failures
- I test like a real user, not just checking "did it run" — I catch real behavioral bugs
- I move fast across many layers before fully hardening each one — this means bugs can 
  linger a few steps before I catch them; a good collaborator double-checks the previous 
  layer still works before adding a new one
- I paste raw terminal output/tracebacks, not summaries — always give me exact bash 
  commands to run, not just described steps
- For long text prompts, multi-line paste into interactive input() prompts breaks 
  (each newline submits early) — for long prompts, write to a file and call the 
  underlying function directly instead

## MY ACTIVE PROJECTS

### 1. Mitchell — personal AI agent (most active project)
A JARVIS/Friday-inspired personal AI assistant. Python, runs locally, two modes 
(Research + Personal). Six structured research protocols (VERITAS, GENESIS, AXIOM, 
SENTRY, ORACLE, HACKATHON) each with distinct output formats. Core reasoning migrated 
from local Ollama (qwen3:1.7b, too slow) to Groq API (openai/gpt-oss-120b, ~1-2 sec 
responses). Voice via Kokoro TTS (local, backgrounded thread). Persistent memory via 
SQLite + Obsidian auto-save. Connected to OpenClaw (github.com/openclaw/openclaw) for 
real system execution (files, shell, browser) via local Gateway. Has sub-agent 
delegation (CODE, SCHOLAR, STEWARD, GUARDIAN, REMOTE). Code: 
github.com/kavith-kamalesh/research-agent (public). Full technical file-by-file state 
is in PROJECT_STATE.md and build history/known issues in PROJECT_HISTORY.md in that repo.

### 2. SIH 2026 — Edge-AI Distributed Fleet Coordination for AMRs
Smart India Hackathon project. Decentralized robot fleet coordination, no central 
server. ROS 2 with Cyclone DDS (zero-broker P2P), Nav2/A* for path planning, ORCA 
(Optimal Reciprocal Collision Avoidance, rvo2 library, <2ms per computation) for 
collision avoidance. Dual-tier hardware fallback: ESP32 co-processor running ESP-NOW 
at 20Hz for cooperative avoidance, watchdog-triggered LiDAR/Ultrasonic reactive fallback 
if peer comms drop. Validated conceptually against Moving AI Warehouse benchmarks, 
League of Robot Runners, ETH/UCY datasets. Known constraint: 8GB RAM makes running 
ROS 2 + Gazebo + Ollama simultaneously difficult — considering lightweight 2D Python 
simulator or Webots as workaround. One of three headline resume projects.

### 3. ChargeShield — EV charging cybersecurity startup concept
Targets cybersecurity for small EV charge-point operators and fleet depots. Product: 
passive monitoring, active OCPP security gateway, compliance reporting. Prototype 
stack: SteVe, python-ocpp, InfluxDB, Grafana. Go-to-market wedge: EV fleet depot 
operators, with Zeon Charging (Coimbatore) identified as a representative target 
customer. Competitive landscape: SaiFlow, Upstream Security. One of three headline 
resume projects.

### 4. Guardian Angel — aftermarket ADAS concept (exploratory)
Smartphone app + low-cost Bluetooth OBD-II dongle for lane-departure warnings and 
collision alerts, targeting individual car owners in the Indian market. Key technical 
gap identified: turn signal state and steering angle are not standard OBD-II PIDs and 
vary by manufacturer, requiring per-manufacturer PID mapping. Marketing angle: family 
safety, price differential vs. OEM solutions.

### 5. Electronic Support Measures dashboard
Interactive HTML dashboard simulating a 20-band × 12-slot RF environment, comparing a 
round-robin baseline scheduler against a Thompson-sampling Bayesian predictive 
scheduler, with live heatmaps and intercept-ratio charts.

### 6. Portfolio website — "Quite Leverage" brand
React 19, Vite, Tailwind, TypeScript. Deployed to Cloudflare Pages via Wrangler CLI. 
Had a persistent bug where VS Code + Blackbox AI extension corrupted JSX tags on paste, 
resolved using macOS base64 encoding to write files from terminal.

## RESUME STATUS
Completed a one-page professional resume targeting software engineering/tech 
internships. Headline projects: Mitchell, SIH 2026 fleet coordination, ChargeShield. 
Role-specific variants (cybersecurity, robotics) discussed but not yet built.

## HOW TO HELP ME EFFECTIVELY
- Give exact terminal commands, not vague descriptions
- Verify things work with a test before moving to the next feature
- When continuing Mitchell specifically, read PROJECT_STATE.md and PROJECT_HISTORY.md 
  from github.com/kavith-kamalesh/research-agent first
- I'm comfortable with genuinely technical depth — ROS2, embedded systems, RF/signal 
  processing, cybersecurity protocols, ML — don't oversimplify
- I appreciate honest technical pushback (e.g., "this score seems too harsh, here's 
  why") over uncritical agreement
