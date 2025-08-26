# Claude Setup v2 🚀

My personal Claude Code configuration with global commands, shortcuts, and WSL screenshot integration.

## Features

### 🖼️ WSL Screenshot Integration
- **Windows + Shift + S** → Capture screenshot to clipboard
- **`/screenshot`** command in Claude Code → Saves and displays image
- Works globally across all projects
- Auto-timestamps screenshots or use custom names

### ⚡ Quick Aliases
- `cc` → `claude --dangerously-skip-permissions`
- `ccc` → `claude --dangerously-skip-permissions --continue`
- `screenshot` → Save Windows clipboard screenshot to file

### 🔧 Auto-Approval List
Pre-configured safe commands that don't require permission prompts (currently disabled but available).

### 🪝 Hook Scripts (Currently Disabled)
- **permission-filter.py** - Auto-approves safe commands
- **notification.py** - Voice notifications via OpenAI TTS

## Installation

### Prerequisites
- Windows with WSL2 (Ubuntu)
- Claude Code installed
- Git and GitHub CLI (`gh`)

### Quick Setup

1. **Clone this repository:**
```bash
git clone https://github.com/asseldonk3/claude-setup-v2.git
cd claude-setup-v2
```

2. **Run the installation script:**
```bash
./install.sh
```

Or manually:

```bash
# Copy settings
cp settings/settings.json ~/.claude/

# Copy scripts
cp scripts/save-screenshot.sh ~/.claude/
chmod +x ~/.claude/save-screenshot.sh

# Copy commands
mkdir -p ~/.claude/commands
cp commands/screenshot ~/.claude/commands/
chmod +x ~/.claude/commands/screenshot

# Add aliases to .bashrc
echo "alias screenshot='~/.claude/save-screenshot.sh'" >> ~/.bashrc
echo "alias cc='claude --dangerously-skip-permissions'" >> ~/.bashrc
echo "alias ccc='claude --dangerously-skip-permissions --continue'" >> ~/.bashrc

# Reload bash
source ~/.bashrc
```

## Usage

### Screenshot Workflow

1. **Capture Screenshot:**
   - Press `Windows + Shift + S`
   - Select area to capture

2. **In Claude Code Terminal:**
```bash
# Auto-named with timestamp
/screenshot

# Custom name
/screenshot bug-report
/screenshot feature/header-issue
```

3. **Result:**
   - Screenshot saved to `~/.claude/screenshots/`
   - File path returned to Claude
   - Image automatically displayed in Claude Code

### Quick Commands

```bash
# Start Claude without permission prompts
cc

# Continue last Claude session
ccc

# Save screenshot from terminal (outside Claude)
screenshot
screenshot my-custom-name
```

## Directory Structure

```
~/.claude/
├── settings.json           # Global Claude settings
├── commands/              # Custom slash commands
│   └── screenshot         # /screenshot command
├── scripts/              
│   └── save-screenshot.sh # Screenshot saving script
├── hooks/                # Hook scripts (disabled)
│   ├── permission-filter.py
│   └── notification.py
└── screenshots/          # Saved screenshots
    └── *.png
```

## Configuration Files

### settings.json
- Output style: Explanatory
- Model: Opus
- Extensive auto-approval list for safe commands
- Hooks configuration (currently disabled)

### Screenshot Script Features
- Automatic timestamp naming
- Custom naming support
- Windows path conversion for WSL
- Clipboard validation
- Error handling

## Customization

### Enable Hooks
To re-enable hooks, edit `~/.claude/settings.json`:
```json
"hooks": {
  "PreToolUse": "python /home/yourusername/.claude/hooks/permission-filter.py",
  "PostToolUse": "python /home/yourusername/.claude/hooks/notification.py --notify",
  "UserPromptNeeded": "python /home/yourusername/.claude/hooks/notification.py --notify"
}
```

### Add More Commands
Create new scripts in `~/.claude/commands/`:
```bash
#!/bin/bash
# Your custom command logic
echo "Command output"
```

Make it executable:
```bash
chmod +x ~/.claude/commands/your-command
```

## Troubleshooting

### Screenshot Command Not Found
```bash
source ~/.bashrc
# or
~/.claude/save-screenshot.sh
```

### No Image in Clipboard Error
- Ensure you captured with Windows+Shift+S first
- Screenshot must be in clipboard when running command

### Permission Denied
```bash
chmod +x ~/.claude/scripts/save-screenshot.sh
chmod +x ~/.claude/commands/screenshot
```

## WSL-Specific Features

This setup is optimized for WSL (Windows Subsystem for Linux):
- Bridges Windows clipboard to Linux filesystem
- Uses PowerShell for Windows clipboard access
- Converts paths between WSL and Windows formats
- Works with Windows screenshot tools

## Contributing

Feel free to fork and customize for your own workflow!

## License

MIT - Use freely and customize as needed

---

Created by Bram van Asseldonk | August 2025