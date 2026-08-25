from dotenv import load_dotenv
load_dotenv()

from agent.planner import run
from agent.claude_bridge import refine_with_claude
from agent.chat_memory import save_message, load_recent_history, clear_history
from agent.protocol_picker import suggest_protocol
from agent.router import classify_message
from agent.voice_output import speak
from agent.voice_summary import get_spoken_summary
from agent.obsidian_bridge import save_note
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

while True:
    user_input = input("You: ")

    if user_input.lower() in ("exit", "quit"):
        break

    if user_input.lower() == "voice on":
        voice_enabled = True
        console.print("[green]Voice enabled.[/green]")
        continue

    if user_input.lower() == "voice off":
        voice_enabled = True
        console.print("[yellow]Voice disabled.[/yellow]")
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
        confirm = input("Use this protocol? (yes / or type VERITAS, GENESIS, AXIOM, SENTRY, ORACLE, HACKATHON to override): ").strip()
        if confirm.lower() not in ("yes", "y", ""):
            user_input = f"[Use protocol {confirm.upper()}] {user_input}"

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
