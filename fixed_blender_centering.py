"""Abstract-25 STL batch → MP4 (same settings as Xu & Sandhofer / ALICE script)."""
import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parent / "scripts"
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))

from stl_spin_render import main

# ./blender-4.5.0-linux-x64/blender -b -P fixed_blender_centering.py

_PROJECT = Path(__file__).resolve().parent
main(
    str(_PROJECT / "data" / "abstract-25" / "stl"),
    str(_PROJECT / "data" / "abstract-25" / "animations"),
)
