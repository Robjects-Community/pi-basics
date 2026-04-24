"""Centralized runtime configuration checks for notebooks and scripts."""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from pathlib import Path
import platform
import sys
from typing import Dict, List, Optional


@dataclass
class SetupResult:
    """Structured result returned by configure_python_runtime."""

    project_root: Path
    python_version: str
    platform_name: str
    missing_packages: List[str]
    package_versions: Dict[str, str]
    warnings: List[str]
    raspberry_pi_model: Optional[str] = None
    install_hints: List[str] = field(default_factory=list)


REQUIRED_PACKAGES = {
    "numpy": "numpy",
    "pandas": "pandas",
    "scipy": "scipy",
    "sklearn": "scikit-learn",
    "cv2": "opencv-python",
}


def _find_project_root(start_path: Optional[Path] = None) -> Path:
    start = (start_path or Path.cwd()).resolve()
    for candidate in [start, *start.parents]:
        if (candidate / "README.md").exists() and (candidate / "tutorials").exists():
            return candidate
    return start


def _python_version_string() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def _detect_raspberry_pi() -> Optional[str]:
    """Return a short Raspberry Pi model string when running on Pi OS."""

    if platform.system() != "Linux":
        return None

    model_path = Path("/proc/device-tree/model")
    if model_path.exists():
        try:
            model = model_path.read_text(errors="ignore").strip("\x00").strip()
        except OSError:
            model = ""
        if "Raspberry Pi" in model:
            return model

    cpuinfo_path = Path("/proc/cpuinfo")
    if cpuinfo_path.exists():
        try:
            cpuinfo = cpuinfo_path.read_text(errors="ignore")
        except OSError:
            cpuinfo = ""
        for line in cpuinfo.splitlines():
            if line.lower().startswith("model") and "raspberry pi" in line.lower():
                return line.split(":", 1)[-1].strip()

    return None


def _platform_warnings(raspberry_pi_model: Optional[str]) -> List[str]:
    warnings: List[str] = []
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        warnings.append(
            "Apple Silicon detected. If binary installs fail, prefer conda-forge packages."
        )
    if raspberry_pi_model:
        machine = platform.machine()
        warnings.append(
            f"Raspberry Pi detected ({raspberry_pi_model}, arch={machine}). "
            "Use the Pi install hints below if pip wheels are missing."
        )
        if machine == "armv7l":
            warnings.append(
                "32-bit Raspberry Pi OS detected. Some packages (e.g. recent opencv) "
                "only ship 64-bit wheels; consider 64-bit Pi OS or piwheels."
            )
    return warnings


def _raspberry_pi_install_hints() -> List[str]:
    return [
        "sudo apt update && sudo apt install -y python3-venv python3-pip libatlas-base-dev libopenjp2-7",
        "python3 -m venv .venv && source .venv/bin/activate",
        "pip install --upgrade pip",
        "pip install --extra-index-url https://www.piwheels.org/simple -r requirements.txt",
    ]


def _import_status() -> tuple[List[str], Dict[str, str]]:
    missing: List[str] = []
    versions: Dict[str, str] = {}

    for module_name, package_name in REQUIRED_PACKAGES.items():
        try:
            module = import_module(module_name)
        except Exception:
            missing.append(package_name)
            continue

        module_version = getattr(module, "__version__", None)
        if module_version:
            versions[package_name] = str(module_version)
        else:
            versions[package_name] = "unknown"

    return missing, versions


def configure_python_runtime(start_path: Optional[Path] = None, verbose: bool = True) -> SetupResult:
    """Validate runtime dependencies and report reproducible remediation commands."""

    project_root = _find_project_root(start_path)
    missing_packages, package_versions = _import_status()
    raspberry_pi_model = _detect_raspberry_pi()
    warnings = _platform_warnings(raspberry_pi_model)
    install_hints = _raspberry_pi_install_hints() if raspberry_pi_model else []
    result = SetupResult(
        project_root=project_root,
        python_version=_python_version_string(),
        platform_name=f"{platform.system()}-{platform.machine()}",
        missing_packages=missing_packages,
        package_versions=package_versions,
        warnings=warnings,
        raspberry_pi_model=raspberry_pi_model,
        install_hints=install_hints,
    )

    if verbose:
        print(f"Python: {result.python_version}")
        print(f"Platform: {result.platform_name}")
        if raspberry_pi_model:
            print(f"Device: {raspberry_pi_model}")
        print(f"Project root: {result.project_root}")
        if warnings:
            for warning in warnings:
                print(f"Warning: {warning}")

        if missing_packages:
            missing_text = ", ".join(sorted(missing_packages))
            print(f"Missing packages: {missing_text}")
            if raspberry_pi_model:
                print("Raspberry Pi setup (recommended):")
                for hint in install_hints:
                    print(f"  {hint}")
            else:
                print("Conda-first setup:")
                print("  conda env create -f environment.yml")
                print("  conda activate pi-basics")
                print("Pip fallback:")
                print("  pip install -r requirements.txt")
        else:
            print("Core dependencies are available.")

    return result
