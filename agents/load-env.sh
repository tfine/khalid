#!/bin/bash
# Load API keys from .env for the dialogue system
# Usage: source agents/load-env.sh
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$REPO_ROOT/.env"
if [ -f "$ENV_FILE" ]; then
    while IFS= read -r line; do
        if [[ "$line" =~ ^[A-Z_]+= ]]; then
            export "$line"
        fi
    done < "$ENV_FILE"
    echo "API keys loaded from $ENV_FILE"
else
    echo "No .env file found at $ENV_FILE"
fi
