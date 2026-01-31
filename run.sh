#!/bin/bash

echo "Starting Wedding Photo Gallery..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run Streamlit app
streamlit run app.py
