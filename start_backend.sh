#!/bin/bash

# Simple, reliable startup script for each server
# This script keeps the process alive and shows errors

echo "🖥️  Starting Backend Server..."
python3 backend_server.py "$@"
