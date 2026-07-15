#!/usr/bin/env python3
"""
Enhetsmodell for XZKJ-makropaden — nummerering følger den fysiske enheten:

    Knotter:  1 (liten, øverst v.)  2 (liten, nederst v.)  3 (medium)  4 (stor)
    Taster:   5  6  7        (rad 1, øverst)
              8  9 10        (rad 2)
             11 12 13        (rad 3)
             14 15 16        (rad 4, nederst)

Alle key-ID-er er kartlagt empirisk mot den fysiske enheten.
"""

# knott-nr -> (venstre, trykk, høyre)
KNOB_IDS = {1: (19, 20, 21), 2: (16, 17, 18), 3: (22, 23, 24), 4: (13, 14, 15)}

# tast-nr (5-16) -> key-ID. Enheten teller nedenfra og opp, kolonnevis.
KEY_IDS = {
    5: 4, 6: 8, 7: 12,
    8: 3, 9: 7, 10: 11,
    11: 2, 12: 6, 13: 10,
    14: 1, 15: 5, 16: 9,
}

KNOB_SIZES = {1: "liten", 2: "liten", 3: "medium", 4: "stor"}
ACTIONS = ("left", "press", "right")
ACTION_LABELS = {"left": "vri venstre", "press": "trykk", "right": "vri høyre"}


def all_targets():
    """[(target_key, key_id, beskrivelse)] for alt som kan bindes."""
    out = []
    for n in sorted(KNOB_IDS):
        for i, act in enumerate(ACTIONS):
            out.append((f"knob{n}.{act}", KNOB_IDS[n][i],
                        f"Knott {n} ({KNOB_SIZES[n]}) — {ACTION_LABELS[act]}"))
    for n in sorted(KEY_IDS):
        out.append((f"key{n}", KEY_IDS[n], f"Tast {n}"))
    return out


def resolve(target: str) -> int:
    """'knob3.left' | 'key7' -> key-ID."""
    if target.startswith("knob"):
        num, act = target[4:].split(".")
        return KNOB_IDS[int(num)][ACTIONS.index(act)]
    if target.startswith("key"):
        return KEY_IDS[int(target[3:])]
    raise ValueError(f"Ukjent mål: {target!r}")
