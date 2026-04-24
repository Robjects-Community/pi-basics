# pi-basics

Modularized Python configuration for tutorials with a conda-first workflow.

## Environment Setup (Conda-first)

1. Create the environment:

   conda env create -f environment.yml

2. Activate it:

   conda activate pi-basics

3. Optional: install all Python dependencies via pip:

   pip install -r requirements.txt

4. Optional: enable the heavy ML stack by uncommenting the marked block in requirements.txt before installing.

## Pip Fallback

If you are not using conda:

pip install -r requirements.txt

## Dependencies

All Python dependencies live in a single requirements.txt at the project root. The file is organized into three sections:

- Core tutorial dependencies (always installed).

- Developer / notebook tooling (always installed).- Optional heavy ML / graph stack (commented out by default; uncomment lines to enable).

## Modular Python Runtime Configuration

Reusable setup code lives in src/pi_basics/setup_utils.py and exports:

- configure_python_runtime(...)
- SetupResult

Typical usage from notebooks/scripts:

from pathlib import Path
import sys

project_root = Path.cwd().resolve()
sys.path.insert(0, str(project_root / "src"))

from pi_basics import configure_python_runtime
result = configure_python_runtime(start_path=project_root, verbose=True)

The function reports:

- Python version and platform
- missing core packages
- package version visibility
- macOS Apple Silicon warning guidance

## CLI Setup Check

For non-notebook workflows, run:

python scripts/check_setup.py

Use quiet mode if you only want the final status:

python scripts/check_setup.py --quiet

The script exits with status code 0 when the core setup is ready and 1 when core dependencies are missing.

## Raspberry Pi (Pi 4 and Pi 5) Setup

The setup module auto-detects Raspberry Pi hardware via `/proc/device-tree/model` and prints Pi-specific install hints. Recommended flow on Raspberry Pi OS (64-bit preferred for Pi 4 and Pi 5):

1. Install system prerequisites:

   sudo apt update
   sudo apt install -y python3-venv python3-pip libatlas-base-dev libopenjp2-7

2. Create and activate a virtual environment in the project:

   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip

3. Install dependencies using piwheels (prebuilt ARM wheels):

   pip install --extra-index-url https://www.piwheels.org/simple -r requirements.txt

4. Verify with the CLI check:

   python scripts/check_setup.py

Notes:

- 64-bit Raspberry Pi OS (aarch64) is recommended for the widest wheel support, especially opencv-python.
- 32-bit Pi OS (armv7l) may need older package versions; consider upgrading to 64-bit Pi OS if installs fail.
- Conda is not the recommended path on Raspberry Pi; the venv + piwheels flow above is preferred.
- The notebook setup cell calls the same module, so Pi-specific guidance also appears in the notebook output.

## Notebook Integration

The first cell in tutorials/tutorial.ipynb now runs project setup checks before tutorial code.
Run that setup cell first after opening the notebook kernel.
