#!/bin/bash
# Script to clean up old files and virtual environment

# Set the base directory to the current directory
BASE_DIR=$(pwd)
echo "Cleaning up project directory: $BASE_DIR"

# Remove Python cache files
echo "Removing Python cache files..."
find $BASE_DIR -type d -name "__pycache__" -exec rm -rf {} +
find $BASE_DIR -name "*.pyc" -delete
find $BASE_DIR -name "*.pyo" -delete
find $BASE_DIR -name "*.pyd" -delete

# Remove old virtual environment if it exists
if [ -d "venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf venv
fi

# Remove other temporary files
echo "Removing temporary files..."
find $BASE_DIR -name ".DS_Store" -delete
find $BASE_DIR -name "*.log" -delete
find $BASE_DIR -name ".coverage" -delete
find $BASE_DIR -name "htmlcov" -type d -exec rm -rf {} +

# Optional: Clean test job directories if needed
echo "Cleaning old test job directories..."
TEST_DIRS=$(find $BASE_DIR/outputs -type d -name "job_*" | grep "test" | tr '\n' ' ')
if [ -n "$TEST_DIRS" ]; then
    echo "Removing test job directories: $TEST_DIRS"
    rm -rf $TEST_DIRS
fi

# Optional: Clean out uploads directory (if desired)
# echo "Cleaning uploads directory..."
# find $BASE_DIR/uploads -type d -name "job_*" -exec rm -rf {} +

echo "Cleanup complete!"