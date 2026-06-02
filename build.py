#!/usr/bin/env python3
"""
Script de build - génère un exécutable portable avec PyInstaller.
Usage : python3 build.py
"""

import subprocess
import sys
import shutil
from pathlib import Path

APP_DIR = Path(__file__).parent


def check_pyinstaller():
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} trouvé")
        return True
    except ImportError:
        print("⚠ PyInstaller non trouvé, installation...")
        subprocess.check_call([sys.executable, "-m", "pip", "install",
                               "pyinstaller==6.11.0", "--quiet"])
        return True


def build():
    check_pyinstaller()

    args = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",               # Tout dans un seul exécutable
        "--windowed",              # Pas de console (Windows)
        "--name", "ProjectScaffolder",
        "--add-data", f"config.json{':' if sys.platform != 'win32' else ';'}.",
        "--clean",
        str(APP_DIR / "app.py"),
    ]

    print("\n🔨 Build en cours...")
    subprocess.check_call(args, cwd=APP_DIR)

    # Copier config.json à côté de l'exe dans dist/
    dist = APP_DIR / "dist"
    src_cfg = APP_DIR / "config.json"
    dst_cfg = dist / "config.json"
    if src_cfg.exists() and not dst_cfg.exists():
        shutil.copy(src_cfg, dst_cfg)
        print(f"✓ config.json copié dans {dist}/")

    exe = "ProjectScaffolder.exe" if sys.platform == "win32" else "ProjectScaffolder"
    print(f"\n✅ Terminé ! Exécutable : dist/{exe}")
    print("   Distribue le dossier dist/ tel quel (exe + config.json).")


if __name__ == "__main__":
    build()
