# run.py
"""
Entry point for the Siploma Smart Drink Heater & Chiller

Usage Examples:
---------------
Run the IoT controller (main device logic):
    python run.py controller

Run the Flask dashboard (web UI):
    python run.py dashboard
"""

import sys
from dashboard.app import app as flask_app

def print_usage():
    print("Usage:")
    print("  python run.py dashboard      # Start Flask web dashboard")
    print("  python run.py help           # Show usage")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "dashboard":
        print("[INFO] Starting Flask dashboard...")
        flask_app.run(host="0.0.0.0", port=5000, debug=True)

    elif mode == "help":
        print_usage()

    else:
        print(f"[ERROR] Unknown mode: {mode}")
        print_usage()
        sys.exit(1)
