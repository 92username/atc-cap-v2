#!/bin/bash
#
# Backup Database and Outputs
#
# Creates a timestamped backup of uploads and outputs directories
#

APP_DIR="/root/atc-cap-v2"
BACKUP_DIR="/root/backups/atc-cap-v2"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "Creating backup: $BACKUP_FILE"
echo ""

cd "$APP_DIR"
tar -czf "$BACKUP_FILE" uploads/ outputs/ data/ || {
    echo "Error: Backup failed"
    exit 1
}

echo "✓ Backup created successfully"
echo "  Size: $(du -h "$BACKUP_FILE" | cut -f1)"
echo "  Location: $BACKUP_FILE"

# Cleanup old backups (keep last 10)
echo ""
echo "Cleaning up old backups (keeping last 10)..."
ls -t "$BACKUP_DIR"/backup_*.tar.gz | tail -n +11 | xargs -r rm
echo "✓ Cleanup completed"
