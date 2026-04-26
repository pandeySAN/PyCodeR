#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: ./run.sh <python_file> [options]"
    echo ""
    echo "Examples:"
    echo "  ./run.sh example.py"
    echo "  ./run.sh mycode.py -o html -f report.html"
    echo "  ./run.sh mycode.py --cfg-dot"
    exit 1
fi

python -m src.cli "$@"
