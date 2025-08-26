#!/bin/bash

# Claude Setup v2 - Installation Script
# This script installs the Claude configuration to your system

set -e  # Exit on error

echo "🚀 Claude Setup v2 - Installation"
echo "=================================="
echo ""

# Get the user's home directory
USER_HOME=$HOME
CLAUDE_DIR="$USER_HOME/.claude"

echo "📁 Creating Claude directories..."
mkdir -p "$CLAUDE_DIR"
mkdir -p "$CLAUDE_DIR/commands"
mkdir -p "$CLAUDE_DIR/hooks"
mkdir -p "$CLAUDE_DIR/screenshots"
mkdir -p "$CLAUDE_DIR/logs"

echo "📋 Copying configuration files..."

# Copy settings (backup existing if present)
if [ -f "$CLAUDE_DIR/settings.json" ]; then
    echo "   Backing up existing settings.json to settings.json.backup"
    cp "$CLAUDE_DIR/settings.json" "$CLAUDE_DIR/settings.json.backup"
fi
cp settings/settings.json "$CLAUDE_DIR/"

# Copy scripts
echo "📜 Installing scripts..."
cp scripts/save-screenshot.sh "$CLAUDE_DIR/"
chmod +x "$CLAUDE_DIR/save-screenshot.sh"

# Copy commands
echo "⚡ Installing slash commands..."
cp commands/screenshot "$CLAUDE_DIR/commands/"
chmod +x "$CLAUDE_DIR/commands/screenshot"

# Copy hooks (for reference, even if disabled)
echo "🪝 Copying hook scripts (disabled by default)..."
cp hooks/*.py "$CLAUDE_DIR/hooks/" 2>/dev/null || true

# Add aliases to .bashrc if they don't exist
echo "🔧 Setting up bash aliases..."

# Function to add alias if it doesn't exist
add_alias() {
    local alias_name="$1"
    local alias_command="$2"
    
    if ! grep -q "alias $alias_name=" "$USER_HOME/.bashrc"; then
        echo "alias $alias_name='$alias_command'" >> "$USER_HOME/.bashrc"
        echo "   ✅ Added alias: $alias_name"
    else
        echo "   ℹ️  Alias already exists: $alias_name"
    fi
}

# Add comment header if not present
if ! grep -q "# Claude Code helpers" "$USER_HOME/.bashrc"; then
    echo "" >> "$USER_HOME/.bashrc"
    echo "# Claude Code helpers" >> "$USER_HOME/.bashrc"
fi

# Add aliases
add_alias "screenshot" "$CLAUDE_DIR/save-screenshot.sh"
add_alias "cc" "claude --dangerously-skip-permissions"
add_alias "ccc" "claude --dangerously-skip-permissions --continue"

echo ""
echo "✨ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Reload your shell: source ~/.bashrc"
echo "   2. Test screenshot: Windows+Shift+S, then run 'screenshot'"
echo "   3. In Claude Code: Use /screenshot command"
echo ""
echo "🎯 Quick commands:"
echo "   screenshot     - Save Windows clipboard screenshot"
echo "   cc            - Start Claude without permissions"
echo "   ccc           - Continue Claude session"
echo "   /screenshot   - In Claude Code, save and display screenshot"
echo ""
echo "Enjoy your enhanced Claude Code setup! 🎉"