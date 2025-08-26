#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "openai",
#     "openai[voice_helpers]",
#     "python-dotenv",
# ]
# ///

"""
Claude Code Notification Hook with OpenAI Integration

This hook is triggered when Claude needs user attention.
Uses OpenAI TTS to speak the notification message dynamically.
"""

import json
import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add utils to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def speak_notification(message, project_name=None):
    """Speak notification using OpenAI TTS."""
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False
    
    try:
        from openai import AsyncOpenAI
        import tempfile
        import subprocess
        
        client = AsyncOpenAI(api_key=api_key)
        
        # Create a more conversational version of the message
        tts_message = message.replace("Claude needs your permission to", "I need permission to")
        
        # Add project name if provided
        if project_name:
            tts_message = f"In {project_name}: {tts_message}"
        
        # Generate speech
        response = await client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="nova",
            input=tts_message,
            response_format="mp3",
        )
        
        # Save to temporary file and play
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            tmp_file.write(response.content)
            tmp_file.flush()
            
            # Try different audio players
            players = [
                ["paplay", tmp_file.name],
                ["ffplay", "-nodisp", "-autoexit", tmp_file.name],
                ["mpg123", "-q", tmp_file.name],
                ["play", tmp_file.name],  # sox
                ["cvlc", "--play-and-exit", "--intf", "dummy", tmp_file.name],
            ]
            
            for player_cmd in players:
                try:
                    subprocess.run(player_cmd, check=True, capture_output=True)
                    os.unlink(tmp_file.name)
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            # Try Windows PowerShell as fallback (for WSL)
            try:
                powershell_path = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
                if os.path.exists(powershell_path):
                    # Convert WSL path to Windows path
                    windows_path = subprocess.check_output(["wslpath", "-w", tmp_file.name]).decode().strip()
                    ps_cmd = f'(New-Object Media.SoundPlayer "{windows_path}").PlaySync()'
                    subprocess.run([powershell_path, "-Command", ps_cmd], check=True, capture_output=True)
                    os.unlink(tmp_file.name)
                    return True
            except Exception:
                pass
            
            # Clean up if no player worked
            os.unlink(tmp_file.name)
        
        return False
    except Exception as e:
        print(f"TTS Error: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return False


def main():
    # Read JSON from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)

    # Extract fields
    hook_event = input_data.get("hook_event", {})
    hook_event_name = hook_event.get("name", "")
    message = hook_event.get("message", "")
    
    cwd = input_data.get("cwd", "")
    session_id = input_data.get("session_id", "")
    transcript_path = input_data.get("transcript_path", "")

    # Check for notify flag
    notify = "--notify" in sys.argv

    # Log event
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "transcript_path": transcript_path,
        "cwd": cwd,
        "hook_event_name": hook_event_name,
        "message": message,
    }

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Append to log file
    log_file = logs_dir / "notification_openai.json"
    try:
        if log_file.exists():
            with open(log_file, "r") as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)
    except:
        pass

    # Speak notification if --notify flag is present
    if notify:
        # Extract project name from cwd
        project_name = os.path.basename(cwd) if cwd and cwd != "." else None
        
        # Use default message if no message provided
        if not message:
            message = f"{project_name or 'Claude'} needs an action"
        
        asyncio.run(speak_notification(message, project_name))

    sys.exit(0)


if __name__ == "__main__":
    main()