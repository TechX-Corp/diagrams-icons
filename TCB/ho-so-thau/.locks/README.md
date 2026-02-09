# Document Locks

This folder tracks who is currently editing which documents to prevent conflicts.

## How It Works

When a team member starts editing a document:
1. They create a lock file: `filename_REVIEW.lock`
2. Commit and push the lock to notify others
3. Work on the document
4. Delete the lock when done
5. Commit and push both document + lock removal

## Lock File Format

```
Editor: John Doe
Started: 2026-02-09 16:30:00
Document: output/proposal_REVIEW.docx
Phase: 3 (Fix & Update)
```

## Commands

```bash
# Check for locks
./scripts/check_locks.sh

# Create lock (done automatically by workflow)
./scripts/lock_document.sh output/proposal_REVIEW.docx "John Doe" "Phase 3"

# Release lock (done automatically by workflow)
./scripts/unlock_document.sh output/proposal_REVIEW.docx
```

## Manual Override

If a lock is stale (person left, forgot to unlock):
1. Coordinate with team (Slack/chat)
2. Remove the lock file manually
3. Commit with message: `"chat: Override stale lock for [filename]"`
