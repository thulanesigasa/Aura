#!/bin/bash
# Aura Dependency Security Audit Script

echo "Running pip-audit on requirements.txt..."
pip-audit -r requirements.txt

if [ $? -eq 0 ]; then
    echo "No vulnerabilities found in dependencies."
else
    echo "Vulnerabilities detected! Please review and update requirements.txt."
    exit 1
fi
 Broadway
