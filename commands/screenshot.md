---
description: Save Windows clipboard screenshot to file and display
thinking-mode: disabled
---

Save a screenshot from Windows clipboard (captured with Windows+Shift+S) to a file in WSL and display it.

Usage:
- `/screenshot` - Save with auto-generated timestamp
- `/screenshot bug-report` - Save with custom name

The screenshot will be saved to ~/.claude/screenshots/ and automatically displayed.

!`~/.claude/save-screenshot.sh $ARGUMENTS`