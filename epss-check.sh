#!/usr/bin/env bash

#this helper script filters the grype vulnerability scan output
#it checks for EPSS scores below a certain threshold for Severity level Critical and filters them out

set -euo pipefail

JSON_FILES=("grype-amd64.json" "grype-arm64.json")
EPSS_THRESHOLD="${EPSS_THRESHOLD:-0.2}" #only fails in EPSS score is >= this threshold

#Count crtical vulns above EPSS threshold
for FILE in "${JSON_FILES[@]}"; do
    if [[ ! -f "$FILE" ]]; then
        echo "ERROR: Grype JSON file not found: $FILE"
        exit 1
    fi

    CRITICAL_COUNT=$(jq --argjson epss "$EPSS_THRESHOLD" '[.matches[] | select(.vulnerability.severity=="Critical" and ((.vulnerability.epss[]?.score // 0) >= $epss))] | length' "$FILE")

    if [[ "$CRITICAL_COUNT" -gt 0 ]]; then
        echo "FAIL: $CRITICAL_COUNT exploitable crtical vulnerabilities found (EPSS >= $EPSS_THRESHOLD)"
        exit 1
    else
        echo "PASS: No exploitable critical vulnerabilities above EPSS $EPSS_THRESHOLD"
    fi
done