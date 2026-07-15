#!/usr/bin/env python3
"""
Klargjør padden for daemonen: flash alle 24 mål til hvert sitt signal.

Dette gjøres én gang. Etterpå styres alt fra profiles.yaml — padden trenger aldri
reflashes selv om du endrer hva tastene gjør.

    .venv/bin/python setup_daemon.py          # flash
    .venv/bin/python setup_daemon.py --dry    # bare vis hva som ville skjedd
"""
import sys

import signals
import xzkj


def build(target):
    """Signalspesifikasjon -> (delay, kode)-oppføringer for protokollen."""
    parts = signals.spec_for(target).split("+")
    mods, key = parts[:-1], parts[-1]
    entries = [(0, xzkj.MODIFIERS[m]) for m in mods]
    entries.append((0, xzkj.HID_CODES[key]))
    return entries


def main():
    dry = "--dry" in sys.argv
    plan = [(t, signals.key_id_for(t), signals.spec_for(t), build(t))
            for t in signals.TARGETS]

    for t, kid, spec, entries in plan:
        print(f"  {t:16s}  id {kid:2d}  ->  {spec:26s} ({len(entries)} trykk)")
    if dry:
        print(f"\n{len(plan)} bindinger — ingenting skrevet (--dry).")
        return

    h = xzkj.open_vendor_interface()
    try:
        for _, kid, _, entries in plan:
            xzkj.bind_key_sequence(h, kid, entries, layer=1)
        xzkj.finish(h)
    finally:
        h.close()
    print(f"\n{len(plan)} signaler skrevet til padden.")
    print("Start daemonen:  .venv/bin/python daemon.py")


if __name__ == "__main__":
    main()
