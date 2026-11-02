"""Root-level entry point: python run_all.py [--download --clean --build --estimate --robustness --report | --all]"""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
runpy.run_path(str(Path(__file__).parent / "src" / "run_all.py"), run_name="__main__")
