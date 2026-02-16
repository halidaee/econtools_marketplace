#!/bin/bash
# generate-preview.sh — Generates palette preview HTML from cache JSON
# Called by PostToolUse hook on ALL Write calls; filters by file path.

set -euo pipefail

# Read hook input from stdin (JSON with tool_input.file_path)
HOOK_INPUT=$(cat)

# Check if this Write was for .palette-cache.json; exit silently otherwise
FILE_PATH=$(echo "$HOOK_INPUT" | jq -r '.tool_input.file_path // ""' 2>/dev/null)
if [[ "$FILE_PATH" != *".palette-cache.json" ]]; then
  exit 0
fi

SKILL_DIR="$HOME/.claude/skills/palette-designer"
CACHE_FILE="$SKILL_DIR/.palette-cache.json"
TEMPLATE="$SKILL_DIR/preview-template.html"
OUTPUT="$SKILL_DIR/palette-preview.html"

# Exit silently if no cache file
[[ -f "$CACHE_FILE" ]] || exit 0

# Exit silently if no template
[[ -f "$TEMPLATE" ]] || exit 0

# Validate JSON (exit silently if invalid)
if ! jq empty "$CACHE_FILE" 2>/dev/null; then
  rm -f "$CACHE_FILE"
  exit 0
fi

# Read the palette JSON
PALETTE_JSON=$(cat "$CACHE_FILE")

# Build output: head of template up to injection point, injected data, rest of template
{
  sed '/PALETTE_DATA_INJECTION_POINT/q' "$TEMPLATE"
  echo "<script>var PALETTE = $PALETTE_JSON;</script>"
  sed '1,/PALETTE_DATA_INJECTION_POINT/d' "$TEMPLATE"
} > "$OUTPUT"

# Output clickable link
echo "Palette preview: file://$OUTPUT"

# Clean up cache
rm -f "$CACHE_FILE"
