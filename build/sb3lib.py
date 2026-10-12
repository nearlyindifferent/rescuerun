"""A tiny library that writes genuine Scratch 3.0 (.sb3) projects.

It produces the same JSON structure that the Scratch editor saves:
blocks with opcodes, inputs, fields, parent/next links, custom blocks
(procedures), variables, lists, broadcasts, costumes and sounds, zipped
together with their asset files.
"""

import hashlib
import json
import zipfile

# ---------------------------------------------------------------------------
# Primitive type codes used in Scratch's serialised inputs
# ---------------------------------------------------------------------------
T_NUM, T_POSNUM, T_WHOLE, T_INT, T_ANGLE, T_COLOR, T_TEXT, T_BROADCAST, T_VAR, T_LIST = (
    4, 5, 6, 7, 8, 9, 10, 11, 12, 13)
KIND_CODE = {"num": T_NUM, "posnum": T_POSNUM, "whole": T_WHOLE, "int": T_INT,
             "angle": T_ANGLE, "text": T_TEXT}

# input specs: opcode -> {input name: kind}
#   kind: num/posnum/whole/int/angle/text  literal slot
#         bool                              boolean slot (no shadow)
#         stack                             C-block mouth
#         ("menu", shadow opcode, field)    dropdown shadow block
SPEC = {
    # motion
    "motion_movesteps": {"STEPS": "num"},
    "motion_gotoxy": {"X": "num", "Y": "num"},
    "motion_changexby": {"DX": "num"},
    "motion_setx": {"X": "num"},
    "motion_changeyby": {"DY": "num"},
    "motion_sety": {"Y": "num"},
    "motion_pointindirection": {"DIRECTION": "angle"},
    "motion_turnright": {"DEGREES": "num"},
    "motion_setrotationstyle": {},
    # looks
    "looks_switchcostumeto": {"COSTUME": ("menu", "looks_costume", "COSTUME")},
    "looks_switchbackdropto": {"BACKDROP": ("menu", "looks_backdrops", "BACKDROP")},
    "looks_nextcostume": {},
    "looks_say": {"MESSAGE": "text"},
    "looks_sayforsecs": {"MESSAGE": "text", "SECS": "num"},
    "looks_changesizeby": {"CHANGE": "num"},
    "looks_setsizeto": {"SIZE": "num"},
    "looks_changeeffectby": {"CHANGE": "num"},
    "looks_seteffectto": {"VALUE": "num"},
    "looks_cleargraphiceffects": {},
    "looks_show": {}, "looks_hide": {},
    "looks_gotofrontback": {},
    # sound
    "sound_play": {"SOUND_MENU": ("menu", "sound_sounds_menu", "SOUND_MENU")},
    "sound_playuntildone": {"SOUND_MENU": ("menu", "sound_sounds_menu", "SOUND_MENU")},
    "sound_stopallsounds": {},
    "sound_setvolumeto": {"VOLUME": "num"},
    # events
    "event_whenflagclicked": {},
    "event_whenbroadcastreceived": {},
    "event_whenkeypressed": {},
    "event_broadcast": {"BROADCAST_INPUT": "broadcast"},
    "event_broadcastandwait": {"BROADCAST_INPUT": "broadcast"},
    # control
    "control_wait": {"DURATION": "posnum"},
    "control_repeat": {"TIMES": "whole", "SUBSTACK": "stack"},
    "control_forever": {"SUBSTACK": "stack"},
    "control_if": {"CONDITION": "bool", "SUBSTACK": "stack"},
    "control_if_else": {"CONDITION": "bool", "SUBSTACK": "stack", "SUBSTACK2": "stack"},
    "control_wait_until": {"CONDITION": "bool"},
    "control_repeat_until": {"CONDITION": "bool", "SUBSTACK": "stack"},
    "control_stop": {},
    # sensing
    "sensing_touchingobject": {"TOUCHINGOBJECTMENU": ("menu", "sensing_touchingobjectmenu", "TOUCHINGOBJECTMENU")},
    "sensing_keypressed": {"KEY_OPTION": ("menu", "sensing_keyoptions", "KEY_OPTION")},
    "sensing_timer": {}, "sensing_resettimer": {},
    "sensing_distanceto": {"DISTANCETOMENU": ("menu", "sensing_distancetomenu", "DISTANCETOMENU")},
    # operators
    "operator_add": {"NUM1": "num", "NUM2": "num"},
    "operator_subtract": {"NUM1": "num", "NUM2": "num"},
    "operator_multiply": {"NUM1": "num", "NUM2": "num"},
    "operator_divide": {"NUM1": "num", "NUM2": "num"},
    "operator_random": {"FROM": "num", "TO": "num"},
    "operator_lt": {"OPERAND1": "text", "OPERAND2": "text"},
    "operator_gt": {"OPERAND1": "text", "OPERAND2": "text"},
    "operator_equals": {"OPERAND1": "text", "OPERAND2": "text"},
    "operator_and": {"OPERAND1": "bool", "OPERAND2": "bool"},
    "operator_or": {"OPERAND1": "bool", "OPERAND2": "bool"},
    "operator_not": {"OPERAND": "bool"},
    "operator_join": {"STRING1": "text", "STRING2": "text"},
    "operator_mod": {"NUM1": "num", "NUM2": "num"},
    "operator_round": {"NUM": "num"},
    "operator_mathop": {"NUM": "num"},
    "operator_length": {"STRING": "text"},
    # data
    "data_setvariableto": {"VALUE": "text"},
    "data_changevariableby": {"VALUE": "num"},
    "data_addtolist": {"ITEM": "text"},
    "data_deletealloflist": {},
    "data_itemoflist": {"INDEX": "int"},
    "data_lengthoflist": {},
    # motion/looks reporters
    "motion_xposition": {}, "motion_yposition": {}, "motion_direction": {},
    "looks_size": {}, "looks_costumenumbername": {},
}

REPORTER_OPCODES = {
    "motion_xposition", "motion_yposition", "motion_direction", "looks_size",
    "looks_costumenumbername", "sensing_timer", "data_itemoflist",
    "data_lengthoflist", "sensing_distanceto",
}


class Node:
    """One block in a script (before it is flattened to project.json)."""

    def __init__(self, opcode, inputs=None, fields=None, mutation=None):
        self.opcode = opcode
        self.inputs = inputs or {}
        self.fields = fields or {}
        self.mutation = mutation
        self.comment = None


class Var:
    """A reference to a variable reporter (resolved when the project is saved)."""

    def __init__(self, name):
        self.name = name


# ---------------------------------------------------------------------------
# Block constructors (a small readable vocabulary used by game.py)
# ---------------------------------------------------------------------------
def blk(opcode, fields=None, mutation=None, **inputs):
    if opcode not in SPEC:
        raise KeyError("unknown opcode " + opcode)
    for k in inputs:
        if k not in SPEC[opcode]:
            raise KeyError("%s has no input %s" % (opcode, k))
    return Node(opcode, inputs, fields, mutation)


def var(name):
    return Var(name)


def stop(option):
    """control_stop: option is 'all' or 'other scripts in sprite' or 'this script'."""
    hasnext = "true" if option == "other scripts in sprite" else "false"
    return Node("control_stop", {}, {"STOP_OPTION": option},
                {"tagName": "mutation", "children": [], "hasnext": hasnext})


# ---------------------------------------------------------------------------
class IdGen:
    def __init__(self, prefix):
        self.prefix = prefix
        self.n = 0

    def __call__(self):
        self.n += 1
        return "%s%04d" % (self.prefix, self.n)


class Target:
    def __init__(self, project, name, is_stage=False):
        self.project = project
        self.name = name
        self.is_stage = is_stage
        self.variables = {}       # name -> (id, value)
        self.lists = {}           # name -> (id, items)
        self.costumes = []        # dict(name, data(bytes), ext, cx, cy)
        self.sounds = []          # dict(name, data(bytes), rate, count)
        self.scripts = []         # (hat Node, [Nodes], comment)
        self.comments = []        # free-floating notes
        self.procs = {}           # proccode -> (argcount)
        self.props = dict(visible=True, x=0, y=0, size=100, direction=90,
                          draggable=False, rotationStyle="all around",
                          currentCostume=0, volume=100, layerOrder=1)
        self.ids = IdGen(("s" if not is_stage else "stage") + str(len(project.targets)) + "_")
        self.blocks = {}
        self.block_comments = {}
        self.layout_y = [30, 30]

    # -- declarations ------------------------------------------------------
    def add_variable(self, name, value=0):
        scope = "g" if self.is_stage else self.name.replace(" ", "")
        vid = "var_%s_%s" % (scope, name.replace(" ", ""))
        self.variables[name] = (vid, value)
        return vid

    def add_list(self, name, items=()):
        lid = "list_%s_%s" % (self.name.replace(" ", ""), name.replace(" ", ""))
        self.lists[name] = (lid, list(items))
        return lid

    def add_costume(self, name, data, ext, cx, cy, resolution=1):
        self.costumes.append(dict(name=name, data=data, ext=ext, cx=cx, cy=cy, res=resolution))

    def add_sound(self, name, wav):
        self.sounds.append(dict(name=name, wav=wav))

    # -- scripts -----------------------------------------------------------
    def script(self, hat, body, comment=None):
        self.scripts.append((hat, body, comment))

    def define(self, proccode, body, warp=False, comment=None):
        """Create a custom block ("My Blocks") with no inputs."""
        self.procs[proccode] = warp
        hat = Node("procedures_definition")
        hat.proc = proccode
        hat.warp = warp
        self.scripts.append((hat, body, comment))

    # -- variable lookup ---------------------------------------------------
    def find_var(self, name):
        if name in self.variables:
            return self.variables[name][0]
        st = self.project.stage
        if name in st.variables:
            return st.variables[name][0]
        raise KeyError("no variable " + name)

    def find_list(self, name):
        if name in self.lists:
            return self.lists[name][0]
        raise KeyError("no list " + name)

    # -- flattening ----------------------------------------------------------
    def _add(self, node, parent, top=False, shadow=False):
        bid = self.ids()
        b = {"opcode": node.opcode, "next": None, "parent": parent,
             "inputs": {}, "fields": {}, "shadow": shadow, "topLevel": top}
        self.blocks[bid] = b
        spec = SPEC.get(node.opcode, {})
        for name, val in node.inputs.items():
            b["inputs"][name] = self._input(spec[name], val, bid)
        for fname, fval in node.fields.items():
            b["fields"][fname] = self._field(node.opcode, fname, fval)
        if node.mutation is not None:
            b["mutation"] = node.mutation
        node.id = bid
        return bid

    def _field(self, opcode, fname, fval):
        if fname == "VARIABLE":
            return [fval, self.find_var(fval)]
        if fname == "LIST":
            return [fval, self.find_list(fval)]
        if fname == "BROADCAST_OPTION":
            return [fval, self.project.broadcast_id(fval)]
        return [fval, None]

    def _chain(self, nodes, parent, top=False):
        """Create a stack of blocks, return the id of the first one."""
        prev = None
        first = None
        for n in nodes:
            bid = self._add(n, parent if prev is None else prev, top=(top and prev is None))
            if prev is not None:
                self.blocks[prev]["next"] = bid
            else:
                first = bid
            prev = bid
        return first

    def _reporter(self, val, parent):
        if isinstance(val, Var):
            return [T_VAR, val.name, self.find_var(val.name)]
        return self._add(val, parent)

    def _input(self, kind, val, parent):
        # --- C-block mouth
        if kind == "stack":
            if val is None or val == []:
                return None
            first = self._chain(val, parent)
            return [2, first]
        # --- boolean slot
        if kind == "bool":
            if val is None:
                return None
            return [2, self._reporter(val, parent)]
        # --- broadcast
        if kind == "broadcast":
            if isinstance(val, str):
                return [1, [T_BROADCAST, val, self.project.broadcast_id(val)]]
            rid = self._reporter(val, parent)
            return [3, rid, [T_BROADCAST, "", ""]]
        # --- dropdown menu with shadow block
        if isinstance(kind, tuple):
            _, shadow_op, field = kind
            if isinstance(val, str):
                sid = self.ids()
                self.blocks[sid] = {"opcode": shadow_op, "next": None, "parent": parent,
                                    "inputs": {}, "fields": {field: [val, None]},
                                    "shadow": True, "topLevel": False}
                return [1, sid]
            sid = self.ids()
            self.blocks[sid] = {"opcode": shadow_op, "next": None, "parent": parent,
                                "inputs": {}, "fields": {field: ["", None]},
                                "shadow": True, "topLevel": False}
            rid = self._reporter(val, parent)
            return [3, rid, sid]
        # --- literal slot (number or text)
        code = KIND_CODE[kind]
        if isinstance(val, (int, float, str)) and not isinstance(val, bool):
            return [1, [code, _s(val)]]
        rid = self._reporter(val, parent)
        return [3, rid, [code, "" if kind == "text" else "0"]]

    # layout --------------------------------------------------------------
    @staticmethod
    def _count(nodes):
        """Rough number of stacked block rows (used only to space scripts out)."""
        n = 0
        for node in nodes:
            n += 1
            for v in node.inputs.values():
                if isinstance(v, list):
                    n += Target._count(v) + 1
        return n

    def build_blocks(self):
        self.blocks = {}
        y = [20, 20]
        for hat, body, comment in self.scripts:
            height = 70 + 31 * self._count(body)
            col = 0 if y[0] <= y[1] else 1
            x = 20 + col * 560
            if hat.opcode == "procedures_definition":
                top = self._definition(hat, body, x, y[col])
            else:
                hid = self._add(hat, None, top=True)
                self.blocks[hid]["x"], self.blocks[hid]["y"] = x, y[col]
                if body:
                    nxt = self._chain(body, hid)
                    self.blocks[hid]["next"] = nxt
                top = hid
            if comment:
                cid = "c_%s_%s" % (self.name.replace(" ", ""), top)
                self.block_comments[cid] = {
                    "blockId": top, "x": x + 330, "y": y[col], "width": 260,
                    "height": 90, "minimized": False, "text": comment}
                self.blocks[top]["comment"] = cid
            y[col] += height + 40

    def _definition(self, hat, body, x, y):
        proccode = hat.proc
        did = self.ids()
        pid = self.ids()
        self.blocks[did] = {"opcode": "procedures_definition", "next": None, "parent": None,
                            "inputs": {"custom_block": [1, pid]}, "fields": {},
                            "shadow": False, "topLevel": True, "x": x, "y": y}
        self.blocks[pid] = {"opcode": "procedures_prototype", "next": None, "parent": did,
                            "inputs": {}, "fields": {}, "shadow": True, "topLevel": False,
                            "mutation": proc_mutation(proccode, hat.warp, prototype=True)}
        if body:
            self.blocks[did]["next"] = self._chain(body, did)
        return did

    # serialise -------------------------------------------------------------
    def to_json(self, asset_names):
        d = {
            "isStage": self.is_stage,
            "name": self.name,
            "variables": {vid: [n, v] for n, (vid, v) in self.variables.items()},
            "lists": {lid: [n, items] for n, (lid, items) in self.lists.items()},
            "broadcasts": {},
            "blocks": self.blocks,
            "comments": self.block_comments,
            "currentCostume": self.props["currentCostume"],
            "costumes": [],
            "sounds": [],
            "volume": self.props["volume"],
            "layerOrder": 0 if self.is_stage else self.props["layerOrder"],
        }
        for c in self.costumes:
            md5 = hashlib.md5(c["data"]).hexdigest()
            fname = "%s.%s" % (md5, c["ext"])
            asset_names[fname] = c["data"]
            d["costumes"].append({"assetId": md5, "name": c["name"], "md5ext": fname,
                                  "dataFormat": c["ext"], "bitmapResolution": c["res"],
                                  "rotationCenterX": c["cx"], "rotationCenterY": c["cy"]})
        for s in self.sounds:
            md5 = hashlib.md5(s["wav"]).hexdigest()
            fname = md5 + ".wav"
            asset_names[fname] = s["wav"]
            rate, count = wav_info(s["wav"])
            d["sounds"].append({"assetId": md5, "name": s["name"], "dataFormat": "wav",
                                "format": "", "rate": rate, "sampleCount": count,
                                "md5ext": fname})
        if self.is_stage:
            d.update({"tempo": 60, "videoTransparency": 50, "videoState": "on",
                      "textToSpeechLanguage": None})
            d["broadcasts"] = {bid: name for name, bid in self.project.broadcasts.items()}
        else:
            p = self.props
            d.update({"visible": p["visible"], "x": p["x"], "y": p["y"], "size": p["size"],
                      "direction": p["direction"], "draggable": p["draggable"],
                      "rotationStyle": p["rotationStyle"]})
        return d


def _s(v):
    if isinstance(v, float) and v == int(v) and abs(v) < 1e15:
        return str(int(v))
    return str(v)


def proc_mutation(proccode, warp, prototype=False):
    m = {"tagName": "mutation", "children": [], "proccode": proccode,
         "argumentids": "[]"}
    if prototype:
        m["argumentnames"] = "[]"
        m["argumentdefaults"] = "[]"
    m["warp"] = "true" if warp else "false"
    return m


def wav_info(wav):
    import io
    import wave
    with wave.open(io.BytesIO(wav)) as w:
        return w.getframerate(), w.getnframes()


def call(proccode, warp=False):
    return Node("procedures_call", mutation=proc_mutation(proccode, warp))


# ---------------------------------------------------------------------------
class Project:
    def __init__(self):
        self.targets = []
        self.broadcasts = {}
        self.var_ids = {}
        self.stage = Target(self, "Stage", is_stage=True)
        self.targets.append(self.stage)

    def sprite(self, name):
        t = Target(self, name)
        self.targets.append(t)
        return t

    def broadcast_id(self, name):
        if name not in self.broadcasts:
            self.broadcasts[name] = "msg_" + name.replace(" ", "_")
        return self.broadcasts[name]

    def save(self, path):
        # fix proc call warp flags to match their definitions
        for t in self.targets:
            t.build_blocks()
        for t in self.targets:
            for b in t.blocks.values():
                if b["opcode"] == "procedures_call":
                    pc = b["mutation"]["proccode"]
                    b["mutation"]["warp"] = "true" if t.procs.get(pc) else "false"
        assets = {}
        targets = [t.to_json(assets) for t in self.targets]
        monitors = []
        project = {
            "targets": targets,
            "monitors": monitors,
            "extensions": [],
            "meta": {"semver": "3.0.0", "vm": "0.2.0",
                     "agent": "Rescue Runner generator (Python)"},
        }
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("project.json", json.dumps(project, separators=(",", ":")))
            for name, data in assets.items():
                z.writestr(name, data)
        return project
