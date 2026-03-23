"""ALICE stimuli (Xu & Sandhofer, 2024) — STL batch → MP4, same render as abstract-25."""
import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parent / "scripts"
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))

from stl_spin_render import main

# ./blender-4.5.0-linux-x64/blender -b -P animate_alice_stl.py

_PROJECT = Path(__file__).resolve().parent
_ALICE = _PROJECT / "data" / "ALICE_stl_(Xu & Sandhofer, 2024)"
main(
    str(_ALICE),
    str(_ALICE / "animations"),
)
