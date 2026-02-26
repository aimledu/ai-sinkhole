#!/bin/bash

CONTAINER_NAME="pihole"
OUTPUT_FILE="pihole_dns_logs.csv"
DNS_DB="/etc/pihole/pihole-FTL.db"

# Current version exports ALL of the domains queried by clients.
docker exec "$CONTAINER_NAME" pihole-FTL sqlite3 "$DNS_DB" -csv "SELECT DISTINCT domain FROM queries WHERE status IN (2, 3, 12, 13, 14);" > ./"$OUTPUT_FILE"

echo "DNS logs saved to: $OUTPUT_FILE"
