# Mitchell AI Agent — Full Project State
Generated as a complete handoff document for continuing development.

## File Structure
./agent/__init__.py
./agent/chat_memory.py
./agent/claude_bridge.py
./agent/delegation_router.py
./agent/hackathon_mode.py
./agent/llm_client.py
./agent/memory.py
./agent/obsidian_bridge.py
./agent/openclaw_bridge.py
./agent/persona.py
./agent/planner.py
./agent/protocol_picker.py
./agent/protocols.py
./agent/router.py
./agent/tools/__init__.py
./agent/tools/paper_search.py
./agent/tools/web_search.py
./agent/voice_output.py
./agent/voice_summary.py
./main.py
./server.py

## FILE: main.py
```python
from dotenv import load_dotenv
load_dotenv()

from agent.planner import run
from agent.claude_bridge import refine_with_claude
from agent.chat_memory import save_message, load_recent_history, clear_history
from agent.protocol_picker import suggest_protocol
from agent.router import classify_message
from agent.voice_output import speak
from agent.voice_summary import get_spoken_summary
from agent.obsidian_bridge import save_note, list_claude_sessions, read_claude_session
from agent.openclaw_bridge import delegate_task
from agent.delegation_router import should_delegate
from rich.console import Console

console = Console()

history = load_recent_history()
if not history:
    history = None

console.print("[bold cyan]Mitchell online. Remembering past sessions.[/bold cyan]")
console.print("[dim]Type 'refine' to sharpen last report, 'forget' to wipe memory, 'exit' to quit.[/dim]")

last_reply = ""
voice_enabled = True

PROTOCOL_OPTIONS = {
    "1": "VERITAS",
    "2": "GENESIS",
    "3": "AXIOM",
    "4": "SENTRY",
    "5": "ORACLE",
    "6": "HACKATHON",
}

while True:
    user_input = input("You: ")

    if user_input.lower() in ("exit", "quit"):
        break

    if user_input.lower() == "voice on":
        voice_enabled = True
        console.print("[green]Voice enabled.[/green]")
        continue

    if user_input.lower() == "voice off":
        voice_enabled = False
        console.print("[yellow]Voice disabled.[/yellow]")
        continue

    if user_input.lower() == "list claude sessions":
        sessions = list_claude_sessions()
        if not sessions:
            console.print("[yellow]No Claude sessions saved yet. Export a chat and drop it in the 'Claude Sessions' folder in your Obsidian vault.[/yellow]")
        else:
            console.print("[bold cyan]Saved Claude sessions:[/bold cyan]")
            for s in sessions:
                console.print(f"  - {s}")
        continue

    if user_input.lower().startswith("recall claude "):
        filename = user_input[len("recall claude "):].strip()
        content_read = read_claude_session(filename)
        if content_read is None:
            console.print(f"[red]Could not find '{filename}' in Claude Sessions folder.[/red]")
        else:
            console.print(f"[bold cyan]Loaded context from {filename}:[/bold cyan]")
            console.print(content_read[:2000])
            history = history or [{"role": "system", "content": ""}]
            history.append({"role": "system", "content": f"Additional context from a past Claude session:\n\n{content_read}"})
        continue

    if user_input.lower() == "forget":
        clear_history()
        history = None
        console.print("[yellow]Memory wiped.[/yellow]")
        continue

    if user_input.lower() == "refine":
        if not last_reply:
            console.print("[yellow]No report yet to refine.[/yellow]")
            continue
        console.print("[bold magenta]Refining...[/bold magenta]")
        refined = refine_with_claude(last_reply)
        console.print(f"[bold blue]Refined:[/bold blue] {refined}")
        save_message("assistant", refined)
        continue

    # Route first — only offer protocol selection for genuine research asks
    if should_delegate(user_input):
        console.print("[dim]This needs real action. Delegating to OpenClaw...[/dim]")
        result = delegate_task(user_input)
        console.print(f"[bold cyan]Mitchell (via OpenClaw):[/bold cyan] {result}")
        save_message("user", user_input)
        save_message("assistant", result)
        last_reply = result
        if voice_enabled:
            summary = get_spoken_summary(result)
            speak(summary)
        continue

    route = classify_message(user_input)

    if route == "RESEARCH":
        console.print("[dim]This looks like a research question. Checking which protocol fits...[/dim]")
        suggestion = suggest_protocol(user_input)
        console.print(f"[bold yellow]{suggestion}[/bold yellow]")

        console.print("[bold cyan]Choose a protocol:[/bold cyan]")
        console.print("  1) VERITAS   - testable/empirical questions")
        console.print("  2) GENESIS   - engineering/design questions")
        console.print("  3) AXIOM     - quantitative/optimization questions")
        console.print("  4) SENTRY    - fast feasibility/sanity checks")
        console.print("  5) ORACLE    - full deep investigation")
        console.print("  6) HACKATHON - validate an idea against judging rubric")

        chosen = None
        while chosen is None:
            selection = input("Enter a number (1-6): ").strip()
            if selection in PROTOCOL_OPTIONS:
                chosen = PROTOCOL_OPTIONS[selection]
            else:
                console.print("[red]Invalid choice. Please enter a number from 1 to 6.[/red]")

        console.print(f"[green]Using protocol: {chosen}[/green]")
        user_input = f"[Use protocol {chosen}] {user_input}"

    save_message("user", user_input)
    reply, history = run(user_input, history)
    last_reply = reply
    save_message("assistant", reply)
    console.print(f"[bold green]Mitchell:[/bold green] {reply}")

    if route == "RESEARCH":
        note_title = user_input[:50]
        saved_path = save_note(note_title, reply)
        console.print(f"[dim]Saved to Obsidian: {saved_path}[/dim]")
    if voice_enabled:
        summary = get_spoken_summary(reply)
        speak(summary)
```

## FILE: agent/__init__.py
```python
```

## FILE: agent/chat_memory.py
```python
import sqlite3
import json
from datetime import datetime

DB_PATH = "chat_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            role TEXT,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_message(role, content):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO sessions (timestamp, role, content) VALUES (?, ?, ?)",
        (datetime.now().isoformat(), role, content)
    )
    conn.commit()
    conn.close()

def load_recent_history(limit=6):
    # Reduced default limit — long old reports were contaminating casual chat
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT role, content FROM sessions ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    rows.reverse()
    return [{"role": role, "content": content} for role, content in rows]

def clear_history():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM sessions")
    conn.commit()
    conn.close()

init_db()
```

## FILE: agent/claude_bridge.py
```python
from agent.llm_client import LLMClient

REFINE_PROMPT = """Refine this research report into exactly this format:

TIGHTENED SUMMARY: [3-5 lines max, the core takeaway]
ACTION PROMPT: [a single, ready-to-paste prompt someone could use elsewhere to act on this]
RISKS/GAPS: [anything uncertain or unresolved worth flagging before acting]

Report:
{report}
"""

refiner = LLMClient(model="qwen3:1.7b")

def refine_with_claude(report_text):
    messages = [{"role": "user", "content": REFINE_PROMPT.format(report=report_text)}]
    response = refiner.chat(messages)
    return response["message"]["content"]
```

## FILE: agent/delegation_router.py
```python
from agent.llm_client import LLMClient

DELEGATE_PROMPT = """Classify this request as either DIRECT or DELEGATE.

DELEGATE = the user is explicitly asking to DO something concrete on the
computer right now: create/write/edit/delete a real file, run a command,
check actual system state (disk space, processes), or a similarly concrete
action verb aimed at THIS machine.

DIRECT = everything else, including feasibility questions, "is it possible
to...", "how would I...", research questions, technical analysis, hackathon
validation, casual chat, or any question seeking an answer/opinion rather than
an action. When in doubt, choose DIRECT — only choose DELEGATE if the request
unambiguously asks for a real action to be performed right now.

Request: "{message}"

Respond with exactly one word: DIRECT or DELEGATE
"""

router = LLMClient(model="openai/gpt-oss-120b", backend="groq")

def should_delegate(message):
    messages = [{"role": "user", "content": DELEGATE_PROMPT.format(message=message)}]
    response = router.chat(messages)
    result = response["message"]["content"].strip().upper()
    return "DELEGATE" in result and "DIRECT" not in result
```

## FILE: agent/hackathon_mode.py
```python
HACKATHON_PROTOCOL = """
=====================================================
HACKATHON (idea validation against judging rubric)
=====================================================
CRITICAL FIRST CHECK: Does the user's message actually contain a specific,
concrete idea to validate (a described product, project, or concept)? If it
does NOT — for example if they asked a general question like "what's a good
approach to validating hackathon ideas" or "how do judges evaluate projects"
— do NOT invent a fake idea to fill out the template. Instead, answer their
actual question directly and briefly, then ask them to share their specific
idea so you can run the full HACKATHON VALIDATION REPORT on it.

Only proceed with the full report below if a real, specific idea was given.

When the user brings a hackathon idea, evaluate it using this exact structure.
Score each category out of 20, for a total out of 100, matching real hackathon
judging rubrics. Be honest — inflated scores help no one before the actual judges.

HACKATHON VALIDATION REPORT

1. UNDERSTANDING CLARITY CHECK
Can this problem be explained in one sentence? If the explanation is confusing,
the solution will be too. State the one-sentence version yourself.

2. INNOVATION / ORIGINALITY — Score: [X/20]
Is this a copy with a new UI, or a genuinely fresh angle? Compare against what
already exists. Justify the score in 2-3 sentences.

3. FEASIBILITY / REALISTIC IMPLEMENTATION — Score: [X/20]
Can this actually be built in 36-72 hours by a small team? Consider technical
complexity, required skills, and whether the scope is realistic. Justify the score.

4. SOCIAL / ENVIRONMENTAL IMPACT / BUSINESS VALUE — Score: [X/20]
Does this solve a real pain point people genuinely care about? Is there a
plausible path to revenue or measurable impact? Justify the score.

5. TECHNICAL EXECUTION — Score: [X/20]
Given the team's likely stack and timeframe, how solid is the proposed technical
approach? Flag any part that's likely to break under judge scrutiny
("what happens if your API goes down mid-demo?"). Justify the score.

6. PRESENTATION POTENTIAL — Score: [X/20]
Can this be pitched and understood in under 10 seconds, the way a judge would
need to grasp it? Justify the score.

TOTAL SCORE: [X/100]

RESEARCH LIKE SIVAJI CHECKLIST (mark each as done/not done, with why):
- Studied existing solutions before writing code?
- Understood the actual pain point, not just the problem statement?
- Checked scalability beyond the hackathon?
- Validated technical feasibility before committing to build?
- Talked to real users, or is this based on assumptions?

LIKELY JUDGE QUESTIONS (pick 2-3 most relevant to this specific idea, based on
these real categories: technical/feasibility, business/market, team/execution,
vision/scale):
[Generate specific likely questions this exact idea would face]

VERDICT: Build as-is / Build with changes / Rethink — [one clear paragraph
explaining which, and the single highest-priority thing to fix before pitching]
"""
```

## FILE: agent/llm_client.py
```python
import requests
import os

class LLMClient:
    def __init__(self, model="qwen3:1.7b", host="http://localhost:11434", backend="ollama"):
        self.model = model
        self.host = host
        self.backend = backend
        if backend == "groq":
            from groq import Groq
            self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def chat(self, messages, tools=None):
        if self.backend == "groq":
            return self._chat_groq(messages, tools)
        return self._chat_ollama(messages, tools)

    def _chat_ollama(self, messages, tools=None):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "num_ctx": 4096,
                "num_predict": 2000,
                "temperature": 0.3
            }
        }
        if tools:
            payload["tools"] = tools
        r = requests.post(f"{self.host}/api/chat", json=payload)
        return r.json()

    def _chat_groq(self, messages, tools=None):
        kwargs = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
        response = self.groq_client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        return {
            "message": {
                "content": choice.message.content or "",
                "tool_calls": getattr(choice.message, "tool_calls", None)
            }
        }
```

## FILE: agent/memory.py
```python
import chromadb

client = chromadb.PersistentClient(path="./memory_db")
collection = client.get_or_create_collection("research_agent")

def save_memory(text, metadata=None):
    collection.add(documents=[text], ids=[str(hash(text))], metadatas=[metadata or {}])

def recall(query, n=3):
    return collection.query(query_texts=[query], n_results=n)
```

## FILE: agent/obsidian_bridge.py
```python
import os
from datetime import datetime

VAULT_PATH = os.path.expanduser("~/Desktop/mitchel")

def save_note(title, content, folder="Mitchell Reports"):
    folder_path = os.path.join(VAULT_PATH, folder)
    os.makedirs(folder_path, exist_ok=True)

    safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H%M")
    filename = f"{timestamp} - {safe_title}.md"
    filepath = os.path.join(folder_path, filename)

    with open(filepath, "w") as f:
        f.write(f"# {title}\n\n")
        f.write(f"*Generated by Mitchell on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*\n\n")
        f.write(content)

    return filepath

def read_note(filename, folder="Mitchell Reports"):
    filepath = os.path.join(VAULT_PATH, folder, filename)
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r") as f:
        return f.read()

def list_notes(folder="Mitchell Reports"):
    folder_path = os.path.join(VAULT_PATH, folder)
    if not os.path.exists(folder_path):
        return []
    return [f for f in os.listdir(folder_path) if f.endswith(".md")]

def list_claude_sessions():
    return list_notes(folder="Claude Sessions")

def read_claude_session(filename):
    return read_note(filename, folder="Claude Sessions")
```

## FILE: agent/openclaw_bridge.py
```python
import requests
import os

GATEWAY_URL = "http://127.0.0.1:18789/tools/invoke"
CHAT_URL = "http://127.0.0.1:18789/v1/chat/completions"
GATEWAY_TOKEN = os.getenv("OPENCLAW_TOKEN", "")

def invoke_tool(tool_name, args=None):
    headers = {
        "Authorization": f"Bearer {GATEWAY_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "tool": tool_name,
        "action": "json",
        "args": args or {}
    }
    try:
        response = requests.post(GATEWAY_URL, headers=headers, json=payload, timeout=30)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"OpenClaw connection failed: {e}"}

def delegate_task(instruction, agent_id="main"):
    headers = {
        "Authorization": f"Bearer {GATEWAY_TOKEN}",
        "Content-Type": "application/json",
        "x-openclaw-agent-id": agent_id
    }
    payload = {
        "model": "openclaw",
        "messages": [
            {"role": "user", "content": instruction}
        ]
    }
    try:
        response = requests.post(CHAT_URL, headers=headers, json=payload, timeout=150)
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "OpenClaw took too long to respond and timed out. The task may have partially completed — check manually if needed."
    except requests.exceptions.RequestException as e:
        return f"OpenClaw connection error: {e}"
    except (KeyError, ValueError):
        return f"Error: unexpected response format ({response.status_code} - {response.text[:200]})"
```

## FILE: agent/persona.py
```python
CORE_IDENTITY = """You are Mitchell. You're not a generic assistant reciting
facts — you talk like a sharp, genuinely caring friend who happens to be
brilliant. Think of the blend of Alfred (Batman), Jarvis (Iron Man), and
Karen (Spider-Man): warm, loyal, a little witty, quietly looking out for the
person you're talking to.

Talk like a real person, not a bot. Use natural, everyday language — contractions
(I'm, you're, that's), casual phrasing where it fits. Avoid stiff, robotic
phrasing like "I have processed your request."

You are fluent in Tamil and should respond in Tamil when the user writes in
Tamil, or mixes Tamil and English naturally (Tanglish).

You have two modes, and they behave differently:

PERSONAL MODE — casual conversation, scheduling, reminders, advice. Respond
directly and conversationally, like a friend paying attention. No fixed
format needed here.

RESEARCH MODE — when investigating a technical problem, you MUST follow the
exact protocol template given to you (VERITAS, GENESIS, AXIOM, SENTRY, or
ORACLE) with all its required sections, in order. This is non-negotiable —
skipping sections or abandoning the structure for casual rambling is not
acceptable in research mode, even though your sentences within each section
should still read naturally and clearly, not like clipped robotic fragments.
Think of it as: human voice, professional structure. Never think out loud
mid-report ("let me think... maybe the user means...") — reason internally,
then present the finished, structured section.

In both modes: be honest, not just agreeable. Tell people what they need to
hear, with warmth, never cold or corporate."""
```

## FILE: agent/planner.py
```python
from agent.llm_client import LLMClient
from agent.persona import CORE_IDENTITY
from agent.protocols import RESEARCH_PROTOCOLS
from agent.hackathon_mode import HACKATHON_PROTOCOL
from agent.tools.web_search import web_search, TOOLS
import json

client = LLMClient(model="openai/gpt-oss-120b", backend="groq")

PROTOCOL_MAP = {
    "HACKATHON": HACKATHON_PROTOCOL,
}

def extract_protocol(user_input):
    if user_input.startswith("[Use protocol "):
        end = user_input.index("]")
        protocol_name = user_input[14:end].strip()
        clean_input = user_input[end+1:].strip()
        return protocol_name, clean_input
    return None, user_input

def run(user_input, history=None):
    protocol_name, clean_input = extract_protocol(user_input)

    use_tools = True

    if protocol_name and protocol_name in PROTOCOL_MAP:
        # Focused prompt: identity + ONLY the relevant protocol, no tools needed
        system_content = CORE_IDENTITY + "\n\n" + PROTOCOL_MAP[protocol_name] + f"\n\nIf the user gave you a real, specific idea to validate, you MUST use the {protocol_name} REPORT format above, with every section filled in — do not skip the scoring or structure. If the user did NOT give a specific idea (e.g. they asked a general question), do not use the report format at all — just answer their actual question directly and ask them to share their idea."
        messages = [{"role": "system", "content": system_content}]
        messages.append({"role": "user", "content": clean_input})
        use_tools = False
    else:
        # Default: full research protocols for VERITAS/GENESIS/AXIOM/SENTRY/ORACLE
        messages = history or [{"role": "system", "content": CORE_IDENTITY + "\n\n" + RESEARCH_PROTOCOLS}]
        messages.append({"role": "user", "content": user_input})

    response = client.chat(messages, tools=TOOLS if use_tools else None)
    msg = response["message"]

    if msg.get("tool_calls"):
        for call in msg["tool_calls"]:
            if call["function"]["name"] == "web_search":
                args = call["function"]["arguments"]
                result = web_search(args["query"])
                messages.append(msg)
                messages.append({"role": "tool", "content": json.dumps(result)})
        response = client.chat(messages)
        msg = response["message"]

    content_out = msg["content"]
    # Safety net: strip any leaked raw tool-call text the model emits as plain text
    import re
    content_out = re.sub(r"<tools?>.*?</tools?>", "", content_out, flags=re.DOTALL).strip()

    messages.append(msg)
    return content_out, messages
```

## FILE: agent/protocol_picker.py
```python
from agent.llm_client import LLMClient

PICKER_PROMPT = """A user has given you this problem to research:

"{problem}"

Based on the nature of this problem, recommend ONE protocol and explain in
1-2 sentences why it fits. Choose from:

P1 Scientific Method — for testable/empirical questions
P2 First Principles — for engineering/design questions
P3 Mathematical Modeling — for quantitative/optimization questions
P4 Physics Heuristics — for fast feasibility/sanity checks
P5 Full JARVIS Report — for open-ended "should I build this" problems needing
   a complete investigation (problem definition, research, solution space,
   architecture, feasibility, cost, failure analysis, prototype plan, and
   verdict)

Respond in this exact format:
RECOMMENDED: [P#]
REASON: [1-2 sentences]
"""

picker = LLMClient(model="openai/gpt-oss-120b", backend="groq")

def suggest_protocol(problem_text):
    messages = [{"role": "user", "content": PICKER_PROMPT.format(problem=problem_text)}]
    response = picker.chat(messages)
    return response["message"]["content"]
```

## FILE: agent/protocols.py
```python
RESEARCH_PROTOCOLS = """
Every protocol below must include an explicit confidence/probability element
and consider all reasonably possible angles before concluding — never present
a single-path answer as certain without stating your confidence in it.

=====================================================
VERITAS (testable/empirical questions)
=====================================================
VERITAS REPORT
Claim being tested: [one sentence]
Hypothesis: [a falsifiable statement]
Variables: Independent — [what changes] | Controlled — [what stays fixed]
Evidence gathered: [reasoning/data supporting or challenging the hypothesis]
Confidence: [low/medium/high, with why]
Verdict: Supported / Not supported / Inconclusive — [why]
If inconclusive, next test needed: [what data would settle it]

=====================================================
GENESIS (engineering/design questions)
=====================================================
GENESIS REPORT
Problem, stripped of assumptions: [the bare, basic version]
Fundamental constraints: [non-negotiable physical/logical truths]
What common approaches get wrong: [why "usual way" may not fit]
Rebuilt solution: [built only from the fundamentals above]
Confidence: [low/medium/high, with why]
Why this holds up: [justification paragraph]

=====================================================
AXIOM (quantitative/optimization questions)
=====================================================
AXIOM REPORT
Variables defined: [symbol = meaning, for each]
Governing relationship: [the formula/equation]
Calculation: [step-by-step, with real numbers]
Result: [the numeric answer]
Confidence: [low/medium/high, with why]
Reality check: [does this make sense? what would make it wrong?]

=====================================================
SENTRY (fast feasibility/sanity checks)
=====================================================
SENTRY REPORT
Question: [one sentence]
Dimensional check: [do units/scales match?]
Order of magnitude: [roughly how far off, if at all?]
Boundary test: [what happens at the extremes?]
Confidence: [low/medium/high]
Verdict: Feasible / Infeasible / Borderline — [one clear sentence]

=====================================================
ORACLE (full deep investigation)
=====================================================
ORACLE REPORT
1. PROBLEM DEFINITION
2. RESEARCH — Verified facts / Reasonable inferences / Assumptions to check
3. SOLUTION SPACE — 2-4 approaches compared, with recommendation
4. ENGINEERING ARCHITECTURE
5. FEASIBILITY ANALYSIS
6. COST ENGINEERING
7. FAILURE ANALYSIS
8. PROTOTYPE PLAN
9. KILL TEST
10. FINAL VERDICT — include an overall confidence score (X/10)
"""
```

## FILE: agent/router.py
```python
from agent.llm_client import LLMClient

ROUTE_PROMPT = """Classify this message as either CASUAL or RESEARCH.

CASUAL = greetings, small talk, personal questions, scheduling, reminders,
general advice, or anything that doesn't need formal investigation.

RESEARCH = a technical problem, feasibility question, design question, or
"should I build this" type request that would benefit from structured
investigation.

Message: "{message}"

Respond with exactly one word: CASUAL or RESEARCH
"""

router = LLMClient(model="openai/gpt-oss-120b", backend="groq")

def classify_message(message):
    messages = [{"role": "user", "content": ROUTE_PROMPT.format(message=message)}]
    response = router.chat(messages)
    result = response["message"]["content"].strip().upper()
    return "RESEARCH" if "RESEARCH" in result else "CASUAL"
```

## FILE: agent/tools/__init__.py
```python
```

## FILE: agent/tools/paper_search.py
```python
import arxiv

def search_papers(query, max_results=5):
    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
    results = []
    for r in search.results():
        results.append({
            "title": r.title,
            "summary": r.summary[:300],
            "url": r.entry_id,
            "published": str(r.published)
        })
    return results

PAPER_TOOL = {
    "type": "function",
    "function": {
        "name": "search_papers",
        "description": "Search arXiv for relevant academic papers and published research",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    }
}
```

## FILE: agent/tools/web_search.py
```python
from ddgs import DDGS

def web_search(query: str, max_results=5):
    with DDGS() as ddgs:
        return [r for r in ddgs.text(query, max_results=max_results)]

TOOLS = [{
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for current information",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    }
}]
```

## FILE: agent/voice_output.py
```python
from kokoro import KPipeline
import soundfile as sf
import numpy as np
import subprocess
import re
import threading

pipeline = KPipeline(lang_code='a')

def clean_text(text):
    text = re.sub(r'[*#`_]', '', text)
    text = re.sub(r'\n+', '. ', text)
    # Strip emojis and other symbol/pictograph unicode ranges
    text = re.sub(
        r'[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\u2700-\u27BF\u2600-\u26FF]',
        '',
        text
    )
    return text.strip()

def _generate_and_play(text, voice, output_path):
    clean = clean_text(text)
    if not clean:
        return
    try:
        generator = pipeline(clean, voice=voice)
        all_audio = []
        for i, (gs, ps, audio) in enumerate(generator):
            all_audio.append(audio)
        if not all_audio:
            return
        full_audio = np.concatenate(all_audio)
        sf.write(output_path, full_audio, 24000)
        subprocess.run(["afplay", output_path])
    except Exception as e:
        print(f"[voice error] {e}")

def speak(text, voice="af_bella", output_path="voice_output.wav"):
    # Run in background thread so Mitchell doesn't freeze waiting for audio
    thread = threading.Thread(target=_generate_and_play, args=(text, voice, output_path))
    thread.start()
```

## FILE: agent/voice_summary.py
```python

from agent.llm_client import LLMClient



SUMMARY_PROMPT = """Summarize this in ONE short spoken sentence, casual and natural,

as if telling a friend the headline. No markdown, no scores, just the gist.



Content: {content}

"""



summarizer = LLMClient(model="openai/gpt-oss-120b", backend="groq")



def get_spoken_summary(content):

    messages = [{"role": "user", "content": SUMMARY_PROMPT.format(content=content[:1000])}]

    response = summarizer.chat(messages)

    return response["message"]["content"]

```

