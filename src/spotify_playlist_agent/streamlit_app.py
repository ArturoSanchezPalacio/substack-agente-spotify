from __future__ import annotations

import os
import subprocess
import sys

from dotenv import load_dotenv


def main() -> None:
    script_path = os.path.join(os.path.dirname(__file__), "ui.py")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", script_path],
        check=True,
    )


if __name__ == "__main__":
    load_dotenv()
    main()
