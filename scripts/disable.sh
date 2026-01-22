#!/bin/bash

CONTAINER_NAME="pihole"
COMMENT_NAME="ai-sinkhole"
GRAVITY_DB="/etc/pihole/gravity.db"

# Enable the adlist with the given comment
docker exec "$CONTAINER_NAME" bash -c \
  "pihole-FTL sqlite3 '$GRAVITY_DB' \"UPDATE adlist SET enabled = 0 WHERE comment = '$COMMENT_NAME';\""

# Rebuild gravity so the change takes effect
docker exec "$CONTAINER_NAME" pihole -g -q

echo "Blocklist with comment '$COMMENT_NAME' has been disabled."
