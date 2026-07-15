#!/usr/bin/env python3
"""
Signaler — broen mellom padden og daemonen.

Padden vet ingenting om hvilken app du bruker; den sender bare tastetrykk. Så vi
binder hver fysisk tast/knott til et *signal*: en kombinasjon ingenting annet bruker.
Daemonen fanger signalet og bestemmer hva som faktisk skal skje.

macOS har virtuelle tastekoder kun for F13–F20 (åtte). Vi trenger 24 signaler
(12 taster + 4 knotter × 3), så vi bruker tre modifikatornivåer:

    nivå 0:  F13–F20              (8)
    nivå 1:  ctrl+alt + F13–F20   (8)
    nivå 2:  ctrl+shift + F13–F20 (8)

F13–F20 finnes ikke på Mac-tastaturer, så de er trygge å kapre.

MERK — ikke bruk «hyper» (cmd+ctrl+shift+alt). Verktøy som Karabiner, SupaKey og
TellyKeys bruker den stakken til Caps Lock, og da slår Caps Lock seg av og på hver
gang du rører padden. Verifisert med research/sniff_tap.py. To modifikatorer holder,
og kolliderer med langt mindre.
"""
import device

FKEYS = [f"f{i}" for i in range(13, 21)]           # F13–F20
TIERS = ["", "ctrl+alt+", "ctrl+shift+"]

# Alle mål i fysisk rekkefølge: 12 taster, så knottene
TARGETS = [f"key{n}" for n in range(5, 17)] + \
          [f"knob{n}.{a}" for n in (1, 2, 3, 4) for a in ("left", "press", "right")]

SIGNALS = {t: TIERS[i // 8] + FKEYS[i % 8] for i, t in enumerate(TARGETS)}
BY_SIGNAL = {v: k for k, v in SIGNALS.items()}

assert len(SIGNALS) == 24 and len(BY_SIGNAL) == 24, "signalene må være unike"


def spec_for(target: str) -> str:
    """Bindingen som skal flashes til padden for et gitt mål."""
    return SIGNALS[target]


def key_id_for(target: str) -> int:
    return device.resolve(target)


if __name__ == "__main__":
    for t in TARGETS:
        print(f"{t:16s}  id {key_id_for(t):2d}   ->  {SIGNALS[t]}")
