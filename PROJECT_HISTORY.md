# Mitchell — Build History & Known Issues

## Timeline of major decisions
- Started as a local research agent using Ollama (qwen3:1.7b), designed for hackathon idea validation
- Built 6 structured research protocols with distinct output formats
- Added voice (Kokoro TTS), persistent memory (SQLite), Obsidian auto-save
- Connected to OpenClaw for real system execution ability (files, shell, browser)
- Migrated core reasoning from local Ollama to Groq API (openai/gpt-oss-120b) for ~100x latency 
  reduction (from 20-400+ seconds to ~1-2 seconds per response)
- Added sub-agent delegation pattern (CODE, SCHOLAR, STEWARD, GUARDIAN, REMOTE)
- In progress: SSH access to a friend's laptop so REMOTE sub-agent can inspect his ROS2/Gazebo project

## Known bugs fixed during development
1. Protocol name corruption: a global "ARC to Mitchell" find-replace accidentally mangled 
   "RESEARCH_PROTOCOLS" into "RESEMitchellH_PROTOCOLS" — required manual file recreation
2. HACKATHON protocol hallucinated fake ideas when asked general methodology questions — fixed with 
   explicit guard clause checking if a real idea was actually provided
3. Tool-call leak: model sometimes emitted raw `<tools>{...}</tools>` text instead of using structured 
   tool_calls — fixed with regex stripping as a safety net, and disabling tools for focused single-
   protocol prompts that don't need them
4. Protocol confirmation silently bypassed: empty string input was being treated as "yes, use suggested 
   protocol" — fixed by switching to a mandatory numbered menu (1-6) instead of free-text yes/override
5. Voice delay (~6.7s per Kokoro TTS call) — mitigated by backgrounding playback in a thread and 
   generating a short spoken summary instead of reading full long reports aloud
6. Emojis being read aloud by TTS — fixed with unicode range stripping in clean_text()
7. Multi-line paste into terminal input() breaks interactive prompts — each newline gets submitted as a 
   separate response; workaround is calling agent.planner.run() directly via a Python one-liner instead 
   of the interactive main.py loop for long prompts
8. Delegation misclassification: research/feasibility questions were being incorrectly routed to 
   OpenClaw delegation instead of direct research protocols — fixed by sharpening the classifier prompt 
   to require unambiguous action verbs
9. Environment drift: multiple Python venv/version mismatches across sessions (Python 3.14 vs 3.12, 
   numpy build failures) — resolved by standardizing on Python 3.12 and maintaining requirements.txt

## Security posture
- OpenClaw gateway token was accidentally exposed in chat at one point and was rotated
- Unused OpenClaw skills disabled (1Password, GitHub CLI-dependent skills, Spotify, etc. — only enable 
  what's actually installed/needed)
- Deliberately avoided installing ClawHub community skills due to documented malicious-skill risk in 
  that registry
- .gitignore configured to exclude .env, chat_history.db, venv/, *.wav, voices/

## Still open / not yet built
- Obsidian recall is one-directional in most flows (saves reports, but reading back past context for 
  the main conversation loop is only partially wired via "recall claude <file>" command)
- REMOTE sub-agent SSH setup incomplete — need to verify SSH connectivity to friend's laptop, then wire 
  actual exec-over-SSH commands into the sub-agent
- Command owner not set in OpenClaw config (commands.ownerAllowFrom) — flagged by openclaw doctor as a 
  security gap
- gateway.controlUi.allowInsecureAuth still set to true — should be hardened
- No Siri Shortcut / voice-trigger integration built yet (discussed, not implemented)
- No heartbeat/proactive check-in automation built yet (discussed, not implemented)
- Phone/SMS access (Twilio) discussed but deprioritized in favor of free alternatives
