#!/bin/bash
PORT=${1:-5555}
echo "Starting Chess Online Server on port $PORT..."
python3 server.py --port $PORT 