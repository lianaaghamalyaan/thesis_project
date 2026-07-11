"""Launch the thesis dashboard.

Usage:
    python main.py

Then open:
    http://localhost:8501
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
APP = ROOT / "dashboard" / "app.py"


def main() -> int:
    try:
        import streamlit  # noqa: F401
    except ModuleNotFoundError:
        print("Streamlit is not installed.")
        print("Install dashboard dependencies first:")
        print("  python -m pip install -r dashboard/requirements.txt")
        return 1

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP),
        "--server.address",
        "localhost",
        "--server.port",
        "8501",
    ]
    print("Starting dashboard at http://localhost:8501")
    return subprocess.call(command, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
