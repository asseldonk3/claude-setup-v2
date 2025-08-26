#!/bin/bash

# Save Windows clipboard screenshot to file and optionally display path
# Usage: save-screenshot [filename]
# If no filename provided, uses timestamp

# Create screenshots directory if it doesn't exist
SCREENSHOT_DIR="$HOME/.claude/screenshots"
mkdir -p "$SCREENSHOT_DIR"

# Generate filename
if [ -z "$1" ]; then
    FILENAME="screenshot-$(date +%Y%m%d-%H%M%S).png"
else
    FILENAME="$1"
    # Add .png extension if not present
    [[ "$FILENAME" != *.png ]] && FILENAME="${FILENAME}.png"
fi

# Full path for the screenshot
FILEPATH="$SCREENSHOT_DIR/$FILENAME"

# Convert WSL path to Windows path
WINDOWS_PATH=$(wslpath -w "$FILEPATH")

# Save clipboard image to file using PowerShell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
if([System.Windows.Forms.Clipboard]::ContainsImage()) {
    \$image = [System.Windows.Forms.Clipboard]::GetImage()
    \$image.Save('$WINDOWS_PATH', [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Host 'Screenshot saved successfully'
    exit 0
} else {
    Write-Host 'No image in clipboard. Use Windows+Shift+S to capture first.'
    exit 1
}
" 2>/dev/null

# Check if save was successful
if [ $? -eq 0 ]; then
    echo "Screenshot saved to: $FILEPATH"
    echo ""
    echo "You can now reference this in Claude Code:"
    echo "  $FILEPATH"
    echo ""
    echo "Or drag the file into Claude Code terminal"
else
    echo "Error: No image in clipboard or save failed"
    echo "Tip: Use Windows+Shift+S to capture a screenshot first"
    exit 1
fi