#!/usr/bin/env python3
"""Builds Rescue_Runner.sb3 (a genuine Scratch 3.0 project)."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import game

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "Rescue_Runner.sb3")
proj = game.build()
data = proj.save(out)
nblocks = sum(len(t["blocks"]) for t in data["targets"])
print("wrote %s  (%d targets, %d blocks)" % (os.path.normpath(out), len(data["targets"]), nblocks))
