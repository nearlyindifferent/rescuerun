#!/usr/bin/env python3
"""Builds Rescue_Runner.sb3 (a genuine Scratch 3.0 project)."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import game

out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(os.path.dirname(__file__), "..", "Rescue_Runner.sb3")
proj = game.build()
data = proj.save(out)
nblocks = sum(len(t["blocks"]) for t in data["targets"])
print("wrote %s  (%d targets, %d blocks)" % (os.path.normpath(out), len(data["targets"]), nblocks))

# optional: dump every costume as a file so the art can be reviewed visually
if "--dump-art" in sys.argv:
    art_dir = os.path.join(os.path.dirname(__file__), "..", "tests", "out", "art")
    os.makedirs(art_dir, exist_ok=True)
    for t in proj.targets:
        for c in t.costumes:
            fn = "%s__%s.svg" % (t.name.replace(" ", "_"), c["name"].replace(" ", "_"))
            open(os.path.join(art_dir, fn), "wb").write(c["data"])
    print("dumped art to", os.path.normpath(art_dir))
