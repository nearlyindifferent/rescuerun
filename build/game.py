"""Rescue Runner: the Scratch scripts for all four sprites + the stage."""
from sb3lib import *
from layout import *
import art


def build():
    P = Project()
    stage = P.stage

    # ---------------- global variables & broadcasts ----------------
    for name, val in [("Score", 0), ("Water Level", WATER_START), ("Game State", "title"), ("Vertical Speed", 0)]:
        stage.add_variable(name, val)
    for m in ["Start Game", "Supply Collected", "Game Won", "Game Lost"]:
        P.broadcast_id(m)

    # ---------------- Stage ----------------
    stage.add_costume("Flooded Village", art.backdrop(), "svg", 240, 180)
    stage.script(blk("event_whenflagclicked"),
                 [blk("looks_switchbackdropto", BACKDROP="Flooded Village")])

    # ---------------- Sprite 1: Rescue Runner ----------------
    runner = P.sprite("Rescue Runner")
    d, cx, cy = art.player()
    runner.add_costume("idle", d, "svg", cx, cy)
    runner.props.update(layerOrder=3, x=-180, y=GROUND_Y)
    runner.script(blk("event_whenflagclicked"), [
        blk("motion_gotoxy", X=-180, Y=GROUND_Y), blk("looks_show")])

    # ---------------- Sprite 2: Emergency Supply ----------------
    supply = P.sprite("Emergency Supply")
    d, cx, cy = art.supply()
    supply.add_costume("supply 1", d, "svg", cx, cy)
    supply.props.update(layerOrder=2, visible=False)
    supply.script(blk("event_whenflagclicked"), [blk("looks_hide")])

    # ---------------- Sprite 3: Rising Water ----------------
    water = P.sprite("Rising Water")
    d, cx, cy = art.water()
    water.add_costume("wave 1", d, "svg", cx, cy)
    water.props.update(layerOrder=4, x=0, y=WATER_START)
    water.script(blk("event_whenflagclicked"), [
        blk("motion_gotoxy", X=0, Y=var("Water Level")), blk("looks_show")])

    # ---------------- Sprite 4: Game Controller ----------------
    ctl = P.sprite("Game Controller")
    for nm, t, s in [("title", "RESCUE RUNNER", "Collect 10 supplies before the flood!"),
                     ("win", "YOU DID IT!", "Press SPACE to play again"),
                     ("lose", "FLOODED!", "Press SPACE to try again")]:
        d, cx, cy = art.screen(t, s)
        ctl.add_costume(nm, d, "svg", cx, cy)
    ctl.props.update(layerOrder=5, x=0, y=0)
    ctl.script(blk("event_whenflagclicked"), [
        blk("data_setvariableto", fields={"VARIABLE": "Game State"}, VALUE="title"),
        blk("data_setvariableto", fields={"VARIABLE": "Score"}, VALUE=0),
        blk("looks_switchcostumeto", COSTUME="title"),
        blk("motion_gotoxy", X=0, Y=0),
        blk("looks_show"),
        blk("control_wait_until", CONDITION=blk("sensing_keypressed", KEY_OPTION="space")),
        blk("data_setvariableto", fields={"VARIABLE": "Game State"}, VALUE="playing"),
        blk("looks_hide"),
        blk("event_broadcast", BROADCAST_INPUT="Start Game"),
    ])
    return P
