#!/bin/bash

CONTAINER_NAME="pihole"
COMMENT_NAME="ai-sinkhole"
GRAVITY_DB="/etc/pihole/gravity.db"

#Accept user input for the action
echo "Enter 0 to disable the blocklist or enter 1 to enable the blocklist: "
read ACTION

#Accept user input for duration of the action
echo "Enter duration for the change: "
read DURATION

# Disable the adlist with the given comment
docker exec "$CONTAINER_NAME" bash -c \
  "pihole-FTL sqlite3 '$GRAVITY_DB' \"UPDATE adlist SET enabled = '$ACTION' WHERE comment = '$COMMENT_NAME';\""

# Rebuild gravity so the change takes effect
docker exec "$CONTAINER_NAME" pihole -g

echo "The changes have been made, please do not exit for $DURATION."

sleep "$DURATION"

#Revert changes
docker exec "$CONTAINER_NAME" bash -c \
  "pihole-FTL sqlite3 '$GRAVITY_DB' \"UPDATE adlist SET enabled = $((1-ACTION))  WHERE comment = '$COMMENT_NAME';\""

# Rebuild gravity so the change takes effect
docker exec "$CONTAINER_NAME" pihole -g

echo "The changes have been reverted. "
