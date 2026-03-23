# BlenderObjects
A script to automate objects creation

**Current layout and STL batch animation:** see `LAYOUT.txt`. Entries: `fixed_blender_centering.py` (abstract-25), `animate_alice_stl.py` (ALICE / Xu & Sandhofer 2024). Shared logic: `scripts/stl_spin_render.py`.

---

#run the script
blender --background --python blender_objects.py
#run the script with a different file
blender --background --python blender_objects.py -- --file test.txt --output test.blend

for example: 
blender --background --python /Users/samahabdelrahim/git-repos/BlenderObjects/add-on5-stl.py 
or
blender --background --python /Users/samahabdelrahim/git-repos/BlenderObjects/add-on5-stl.py -- --file /Users/samahabdelrahim/git-repos/BlenderObjects/test.txt --output test.blend

./blender-4.5.0-linux-x64/blender -b -P /path/to/BlenderObjects/fixed_blender_centering.py