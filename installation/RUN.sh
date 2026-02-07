#!/bin/bash
# Tax Helper - Run Script for Mac/Linux

echo "💷 Starting Tax Helper..."
echo ""
cd "$(dirname "$0")/.."
python3 -m streamlit run app.py
