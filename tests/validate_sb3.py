#!/usr/bin/env python3
"""Structural validation of a Scratch 3.0 .sb3 file (no Scratch install needed)."""
import hashlib
import json
import sys
import zipfile

EXPECTED_SPRITES = ["Rescue Runner", "Emergency Supply", "Rising Water", "Game Controller"]
CORE_PREFIXES = ("motion_", "looks_", "sound_", "event_", "control_", "sensing_",
                 "operator_", "data_", "procedures_")
problems = []


def bad(msg):
    problems.append(msg)


def main(path):
    z = zipfile.ZipFile(path)
    names = set(z.namelist())
    if z.testzip() is not None:
        bad("corrupt zip member")
    if "project.json" not in names:
        bad("no project.json")
        return
    proj = json.loads(z.read("project.json"))
    for key in ("targets", "monitors", "extensions", "meta"):
        if key not in proj:
            bad("project.json missing key " + key)
    if proj.get("extensions"):
        bad("uses extensions: %s" % proj["extensions"])
    if proj["meta"].get("semver") != "3.0.0":
        bad("meta.semver is not 3.0.0")

    targets = proj["targets"]
    stages = [t for t in targets if t["isStage"]]
    sprites = [t for t in targets if not t["isStage"]]
    if len(stages) != 1:
        bad("need exactly one stage, found %d" % len(stages))
    if [s["name"] for s in sprites] != EXPECTED_SPRITES:
        bad("sprites are %s, expected exactly %s" % ([s["name"] for s in sprites], EXPECTED_SPRITES))
    if targets[0]["isStage"] is not True:
        bad("stage must be the first target")

    stage = stages[0]
    all_broadcasts = stage["broadcasts"]
    global_var_ids = set(stage["variables"])
    used_assets = set()
    stats = {"blocks": 0, "scripts": 0}

    for t in targets:
        tname = t["name"]
        blocks = t["blocks"]
        var_ids = global_var_ids | set(t["variables"])
        list_ids = set(t["lists"])
        # assets
        for kind in ("costumes", "sounds"):
            for a in t[kind]:
                f = a["md5ext"]
                used_assets.add(f)
                if f not in names:
                    bad("%s: missing asset %s" % (tname, f))
                else:
                    if hashlib.md5(z.read(f)).hexdigest() != a["assetId"]:
                        bad("%s: asset %s md5 mismatch" % (tname, f))
        if not t["costumes"]:
            bad("%s has no costumes/backdrops" % tname)
        if not (0 <= t["currentCostume"] < len(t["costumes"])):
            bad("%s: currentCostume out of range" % tname)
        # blocks
        defined = set()
        for bid, b in blocks.items():
            stats["blocks"] += 1
            if not b["opcode"].startswith(CORE_PREFIXES):
                bad("%s: non-core opcode %s" % (tname, b["opcode"]))
            if b["topLevel"]:
                stats["scripts"] += 1
            if b["parent"] is not None and b["parent"] not in blocks:
                bad("%s/%s: dangling parent" % (tname, bid))
            if b["next"] is not None:
                if b["next"] not in blocks:
                    bad("%s/%s: dangling next" % (tname, bid))
                elif blocks[b["next"]]["parent"] != bid:
                    bad("%s/%s: next block's parent mismatch" % (tname, bid))
            if b["topLevel"] and b["parent"] is not None:
                bad("%s/%s: top-level block has parent" % (tname, bid))
            if b["opcode"] == "procedures_prototype":
                defined.add(b["mutation"]["proccode"])
            for iname, inp in b["inputs"].items():
                for ref in inp[1:]:
                    if isinstance(ref, str):
                        if ref not in blocks:
                            bad("%s/%s: input %s references missing block %s" % (tname, bid, iname, ref))
                    elif isinstance(ref, list):
                        if ref[0] == 12 and ref[2] not in var_ids:
                            bad("%s/%s: unknown variable id %s" % (tname, bid, ref[2]))
                        if ref[0] == 11 and ref[2] not in all_broadcasts:
                            bad("%s/%s: unknown broadcast id %s" % (tname, bid, ref[2]))
            for fname, fld in b["fields"].items():
                if fname == "VARIABLE" and fld[1] not in var_ids:
                    bad("%s/%s: unknown variable field" % (tname, bid))
                if fname == "LIST" and fld[1] not in list_ids:
                    bad("%s/%s: unknown list field" % (tname, bid))
                if fname == "BROADCAST_OPTION" and fld[1] not in all_broadcasts:
                    bad("%s/%s: unknown broadcast field" % (tname, bid))
            if "comment" in b and b["comment"] not in t["comments"]:
                bad("%s/%s: block comment missing" % (tname, bid))
        for bid, b in blocks.items():
            if b["opcode"] == "procedures_call" and b["mutation"]["proccode"] not in defined:
                bad("%s: call to undefined custom block %s" % (tname, b["mutation"]["proccode"]))
        # every top-level script must begin with a hat (or be a custom-block definition)
        for bid, b in blocks.items():
            if b["topLevel"] and not (b["opcode"].startswith("event_when") or
                                      b["opcode"] == "procedures_definition" or
                                      b["opcode"] == "control_start_as_clone"):
                bad("%s/%s: loose script starts with %s (no hat)" % (tname, bid, b["opcode"]))

    unused = names - used_assets - {"project.json"}
    if unused:
        bad("unreferenced files in the archive: %s" % sorted(unused))
    broadcasts = sorted(all_broadcasts.values())
    print("targets:", [t["name"] for t in targets])
    print("global variables:", sorted(v[0] for v in stage["variables"].values()))
    print("broadcasts:", broadcasts)
    print("blocks: %(blocks)d in %(scripts)d scripts" % stats)
    print("costumes:", {t["name"]: len(t["costumes"]) for t in targets},
          " sounds:", {t["name"]: len(t["sounds"]) for t in targets})
    print("file size: %.1f KB" % (sum(i.file_size for i in z.infolist()) / 1024))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../Rescue_Runner.sb3")
    if problems:
        print("\nFAILED with %d problem(s):" % len(problems))
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("\nSTRUCTURE OK")
