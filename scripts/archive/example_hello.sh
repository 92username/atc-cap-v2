#!/bin/bash
#
# Example Script: Hello World on VPS
# 
# This is a simple example to demonstrate remote script execution
#

echo "Hello from VPS!"
echo "Current directory: $(pwd)"
echo "Current user: $(whoami)"
echo "Current date: $(date)"
echo ""
echo "Arguments received: $@"
