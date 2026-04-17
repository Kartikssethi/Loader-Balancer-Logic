#!/bin/bash

# Simple, reliable startup script for load balancer
# This script keeps the process alive and shows errors

echo "⚖️  Starting Load Balancer..."
python3 load_balancer.py
