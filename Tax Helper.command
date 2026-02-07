#!/bin/bash

# UK Tax Helper - macOS Double-Click Launcher
# This file can be double-clicked from Finder to start the app

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to that directory
cd "$DIR" || exit 1

# Clear the terminal
clear

# Run the launcher
./start_tax_helper.sh
