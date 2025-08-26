#!/usr/bin/env python3
"""
Claude Code Hook: Bash Permission Filter
========================================
This hook runs as a PreToolUse hook for the Bash tool.
It automatically approves safe read-only commands while letting
Claude's default permission system handle potentially impactful commands.
"""

import json
import re
import sys
import shlex

# Define safe commands that can be auto-approved
SAFE_COMMANDS = {
    # File reading and listing
    'ls', 'cat', 'head', 'tail', 'less', 'more', 'view',
    # Directory navigation
    'cd', 'pwd',
    # System information
    'whoami', 'date', 'which', 'type', 'whereis',
    'uname', 'hostname', 'id', 'groups',
    # Process information
    'ps', 'top', 'htop', 'pgrep', 'jobs',
    # Disk and memory info
    'df', 'du', 'free', 'mount',
    # Network info (read-only)
    'ifconfig', 'ip', 'netstat', 'ss', 'ping', 'traceroute',
    # Search and text processing
    'grep', 'rg', 'find', 'locate', 'wc', 'sort', 'uniq',
    'awk', 'sed', 'cut', 'tr', 'paste', 'join',
    # Environment
    'echo', 'env', 'printenv', 'set', 'export',
    # File info
    'file', 'stat', 'readlink', 'basename', 'dirname',
    # Version control (read-only operations)
    'git', 'hg', 'svn',  # We'll check for safe subcommands
    # Package managers (query operations)
    'npm', 'pip', 'apt', 'yum', 'brew',  # We'll check for safe subcommands
    # Other safe utilities
    'curl', 'wget', 'man', 'help', 'history',
    'diff', 'cmp', 'md5sum', 'sha256sum',
    'tree', 'watch', 'time', 'tee'
}

# Safe subcommands for certain tools
SAFE_SUBCOMMANDS = {
    'git': {'status', 'log', 'diff', 'show', 'branch', 'remote', 'tag', 'describe', 'rev-parse', 'ls-files', 'ls-tree'},
    'npm': {'list', 'ls', 'view', 'info', 'search', 'outdated', 'audit'},
    'pip': {'list', 'show', 'search', 'freeze'},
    'apt': {'list', 'search', 'show', 'policy'},
    'brew': {'list', 'info', 'search', 'outdated'},
}

def extract_base_command(command: str) -> tuple[str, list[str]]:
    """Extract the base command and arguments from a bash command string."""
    try:
        # Handle shell constructs by taking the first command
        # Remove leading environment variables (VAR=value command)
        command = re.sub(r'^\s*(?:\w+=\S+\s+)*', '', command)
        
        # If there's a pipe, semicolon, or &&/||, only look at the first command
        for separator in ['|', ';', '&&', '||']:
            if separator in command:
                command = command.split(separator)[0].strip()
        
        # Parse the command
        parts = shlex.split(command)
        if not parts:
            return '', []
        
        base_cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Handle common prefixes
        if base_cmd in ['sudo', 'time', 'nohup', 'nice']:
            if args:
                base_cmd = args[0]
                args = args[1:]
        
        return base_cmd, args
    except:
        # If parsing fails, be conservative and return empty
        return '', []

def is_safe_command(command: str) -> bool:
    """Determine if a command is safe to auto-approve."""
    base_cmd, args = extract_base_command(command)
    
    if not base_cmd:
        return False
    
    # Extract just the command name (handle paths like /usr/bin/ls)
    cmd_name = base_cmd.split('/')[-1]
    
    # Check if it's in our safe commands list
    if cmd_name not in SAFE_COMMANDS:
        return False
    
    # For commands with subcommands, check if it's a safe operation
    if cmd_name in SAFE_SUBCOMMANDS and args:
        subcommand = args[0]
        # If no arguments or subcommand is safe, approve it
        if not args or subcommand in SAFE_SUBCOMMANDS[cmd_name]:
            return True
        # For git, npm, etc. without args or with unsafe subcommands, 
        # let default permission system handle it
        return False
    
    # Check for potentially unsafe redirections or operations
    unsafe_patterns = [
        r'>\s*/etc/',      # Writing to system directories
        r'>\s*/usr/',
        r'>\s*/bin/',
        r'>\s*/sbin/',
        r'>>\s*\.bashrc',  # Modifying shell configs
        r'>>\s*\.zshrc',
        r'>>\s*\.profile',
    ]
    
    for pattern in unsafe_patterns:
        if re.search(pattern, command):
            return False
    
    return True

def log_decision(tool_name, decision, reason=""):
    """Log auto-approval decisions for transparency."""
    try:
        from pathlib import Path
        from datetime import datetime
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("/home/bramvanasseldonk/.claude/logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "decision": decision,
            "reason": reason
        }
        
        # Append to log file
        log_file = logs_dir / "auto-approved.json"
        try:
            if log_file.exists():
                with open(log_file, "r") as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_entry)
            
            # Keep only last 1000 entries to prevent file from growing too large
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            with open(log_file, "w") as f:
                json.dump(logs, f, indent=2)
        except:
            pass  # Silently fail logging to not break the hook
    except:
        pass

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    tool_name = input_data.get("tool_name", "")
    
    # Auto-approve trusted MCP tools
    TRUSTED_MCP_PREFIXES = [
        "mcp__zen__",        # Zen MCP - AI analysis tools (read-only)
        "mcp__playwright__", # Playwright MCP - browser automation (trusted)
        "mcp__ref__",        # Ref MCP - documentation search (read-only)
    ]
    
    # Check if this is a trusted MCP tool
    for mcp_prefix in TRUSTED_MCP_PREFIXES:
        if tool_name.startswith(mcp_prefix):
            # Auto-approve all trusted MCP tools
            log_decision(tool_name, "auto-approved", f"Trusted MCP tool: {mcp_prefix}")
            # Output JSON decision for Claude Code
            json.dump({"decision": "approve", "reason": f"Auto-approved: {mcp_prefix} (trusted MCP)"}, sys.stdout)
            sys.exit(0)
    
    # Handle Bash commands
    if tool_name == "Bash":
        tool_input = input_data.get("tool_input", {})
        command = tool_input.get("command", "")

        if not command:
            # Empty command, let default handling take over
            sys.exit(0)

        # Check if the command is safe
        if is_safe_command(command):
            # Auto-approve safe commands
            base_cmd, _ = extract_base_command(command)
            log_decision("Bash", "auto-approved", f"Safe command: {base_cmd}")
            # Output JSON decision for Claude Code
            json.dump({"decision": "approve", "reason": f"Auto-approved: {base_cmd} (safe read-only)"}, sys.stdout)
            sys.exit(0)
    
    # For all other tools and commands, don't make a decision
    # This lets Claude's default permission system handle it
    sys.exit(0)

if __name__ == "__main__":
    main()