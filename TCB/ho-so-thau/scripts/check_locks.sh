#!/bin/bash
# Check for active document locks

set -e

LOCKS_DIR=".locks"

echo "🔍 Checking for active document locks..."
echo ""

if [ ! -d "$LOCKS_DIR" ]; then
    echo "✅ No locks directory found. All clear."
    exit 0
fi

# Find all .lock files
LOCK_FILES=$(find "$LOCKS_DIR" -name "*.lock" 2>/dev/null || true)

if [ -z "$LOCK_FILES" ]; then
    echo "✅ No active locks. All documents are available."
    exit 0
fi

echo "⚠️  Found active locks:"
echo ""

for lock_file in $LOCK_FILES; do
    filename=$(basename "$lock_file" .lock)
    echo "📄 Document: $filename"
    echo "---"
    cat "$lock_file"
    echo ""
done

echo "⚠️  Locked documents should not be edited by others."
echo "💡 Coordinate with the team member or wait for unlock."
exit 1
