#!/bin/bash
# Agent-Trace Installer
# Detects your CLI tool and installs the right adapter.

set -e

# Check Python version (scripts require 3.10+)
if command -v python3 &>/dev/null; then
  if ! python3 -c "import sys; assert sys.version_info >= (3, 10)" 2>/dev/null; then
    echo "Warning: Python 3.10+ recommended for scripts. Some features may not work."
  fi
fi

echo "🔍  Agent-Trace Installer"
echo "========================="
echo ""

# Detect CLI tool
if [ -d ".claude" ]; then
    CLI="claude-code"
    echo "Detected: Claude Code"
elif [ -d ".cursor" ]; then
    CLI="cursor"
    echo "Detected: Cursor"
elif [ -f ".aider.conf.yml" ]; then
    CLI="aider"
    echo "Detected: Aider"
elif [ -f "AGENTS.md" ]; then
    CLI="codex"
    echo "Detected: Codex"
else
    CLI="generic"
    echo "No specific CLI detected — installing generic prompts"
fi

echo ""
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Copy core prompts
echo "Installing prompts..."
cp -r "$SCRIPT_DIR/prompts" .

# Copy scripts
echo "Installing scripts..."
mkdir -p repo_universe/scripts
cp "$SCRIPT_DIR/scripts/"*.py repo_universe/scripts/

# Copy curated overlay templates
echo "Installing overlay templates..."
mkdir -p repo_universe/curated
for f in invariants.yaml ownership.yaml source_of_truth.yaml; do
    if [ ! -f "repo_universe/curated/$f" ]; then
        cp "$SCRIPT_DIR/templates/$f" "repo_universe/curated/$f"
        echo "  Created repo_universe/curated/$f (from template — customize for your repo)"
    else
        echo "  Skipped repo_universe/curated/$f (already exists)"
    fi
done

# Create generated directory
mkdir -p repo_universe/generated

# Install CLI-specific adapter
echo ""
echo "Installing $CLI adapter..."
case $CLI in
    claude-code)
        mkdir -p .claude/commands .claude/agents .claude/skills/safe-remediation
        cp "$SCRIPT_DIR/adapters/claude-code/commands/"*.md .claude/commands/
        cp "$SCRIPT_DIR/.claude/agents/"*.md .claude/agents/
        cp "$SCRIPT_DIR/.claude/skills/safe-remediation/SKILL.md" .claude/skills/safe-remediation/
        cp -r "$SCRIPT_DIR/references" .
        echo ""
        echo "Plugin hook: Add this to your .claude/settings.json hooks:"
        echo '  "hooks": { "SessionStart": [{ "command": "echo 🔍 Agent-Trace loaded. Commands: /trace, /map, /query, /validate-universe" }] }'
        ;;
    codex)
        if [ -f "AGENTS.md" ]; then
            echo "" >> AGENTS.md
            cat "$SCRIPT_DIR/adapters/codex/AGENTS.md" >> AGENTS.md
            echo "Appended trace commands to existing AGENTS.md"
        else
            cp "$SCRIPT_DIR/adapters/codex/AGENTS.md" .
        fi
        ;;
    cursor)
        mkdir -p .cursor/rules
        cp "$SCRIPT_DIR/adapters/cursor/.cursor/rules/trace.md" .cursor/rules/
        ;;
    aider)
        if [ -f ".aider.conf.yml" ]; then
            echo "" >> .aider.conf.yml
            cat "$SCRIPT_DIR/adapters/aider/.aider.conf.yml" >> .aider.conf.yml
            echo "Appended trace config to existing .aider.conf.yml"
        else
            cp "$SCRIPT_DIR/adapters/aider/.aider.conf.yml" .
        fi
        ;;
    generic)
        echo "Prompts and scripts installed. See prompts/ for usage."
        ;;
esac

echo ""
echo "✅ Agent-Trace installed for $CLI"
echo ""
echo "Commands available:"
echo "  /trace              — Safe remediation (full workflow)"
echo "  /map                — Build repo universe"
echo "  /query <target>     — Query impact of a change"
echo "  /validate-universe  — Validate repo universe integrity"
echo ""
echo "Next steps:"
echo "  1. Run /map to generate the repo universe"
echo "  2. Customize repo_universe/curated/*.yaml for your invariants"
echo "  3. Run /validate-universe to check integrity"
echo "  4. Use /trace before risky edits"
