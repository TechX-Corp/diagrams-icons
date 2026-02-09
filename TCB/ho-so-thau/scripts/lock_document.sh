#!/bin/bash
# Lock a document for editing

set -e

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <document_path> <editor_name> [phase]"
    echo "Example: $0 output/proposal_REVIEW.docx \"John Doe\" \"Phase 3\""
    exit 1
fi

DOCUMENT_PATH="$1"
EDITOR_NAME="$2"
PHASE="${3:-Unknown}"

LOCKS_DIR=".locks"
DOCUMENT_NAME=$(basename "$DOCUMENT_PATH")
LOCK_FILE="$LOCKS_DIR/${DOCUMENT_NAME}.lock"

# Create locks directory if not exists
mkdir -p "$LOCKS_DIR"

# Check if already locked
if [ -f "$LOCK_FILE" ]; then
    echo "❌ Document is already locked:"
    cat "$LOCK_FILE"
    exit 1
fi

# Create lock file
cat > "$LOCK_FILE" << EOF
Editor: $EDITOR_NAME
Started: $(date '+%Y-%m-%d %H:%M:%S')
Document: $DOCUMENT_PATH
Phase: $PHASE
EOF

echo "✅ Lock created: $LOCK_FILE"
cat "$LOCK_FILE"
echo ""
echo "💡 Remember to commit and push this lock file!"
echo "   git add $LOCK_FILE && git commit -m 'chat: Lock $DOCUMENT_NAME for editing' && git push"
