#!/bin/bash

# Open the GUI in the default browser
echo "🌐 Opening GUI in browser..."
sleep 2

# Try different methods to open the browser
if command -v open &> /dev/null; then
    open "http://127.0.0.1:8000"
elif command -v xdg-open &> /dev/null; then
    xdg-open "http://127.0.0.1:8000"
elif command -v firefox &> /dev/null; then
    firefox "http://127.0.0.1:8000"
elif command -v chrome &> /dev/null; then
    chrome "http://127.0.0.1:8000"
else
    echo "⚠️  Could not open browser automatically."
    echo "🔗 Open this URL manually: http://127.0.0.1:8000"
fi
