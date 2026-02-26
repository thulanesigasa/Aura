#!/bin/bash
# Aura Database Backup Script

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/aura_db_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

echo "Starting backup of aura-db..."
docker exec aura-db pg_dump -U aura_user aura_db > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "Backup successful: $BACKUP_FILE"
    # Keep only the last 7 days of backups
    find $BACKUP_DIR -name "aura_db_*.sql" -mtime +7 -delete
else
    echo "Backup failed!"
    exit 1
fi
