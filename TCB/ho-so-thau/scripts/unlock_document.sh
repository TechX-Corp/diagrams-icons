#!/bin/bash
# Unlock a document after editing

set -e

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <document_path>"
    echo "Example: $0 output/proposal_REVIEW.docx"
    exit 1
fi

DOCUMENT_PATH="$1"
LOCKS_DIR=".locks"
DOCUMENT_NAME=$(basename "$DOCUMENT_PATH")
LOCK_FILE="$LOCKS_DIR/${DOCUMENT_NAME}.lock"

# Check if lock exists
if [ ! -f "$LOCK_FILE" ]; then
    echo "⚠️  No lock file found for: $DOCUMENT_NAME"
    echo "   Lock file expected at: $LOCK_FILE"
    exit 0
fi

# Show lock info before removing
echo "🔓 Removing lock:"
cat "$LOCK_FILE"
echo ""

# Remove lock file
rm "$LOCK_FILE"

echo "✅ Lock removed: $LOCK_FILE"
echo ""
echo "💡 Remember to commit and push the unlock!"
echo "   git add $LOCK_FILE && git commit -m 'chat: Unlock $DOCUMENT_NAME' && git push"
