#!/usr/bin/env python3
"""Kartleggingstest: programmerer ID 1–24 til å skrive sitt eget nummer + mellomrom."""
import xzkj

DIGIT = {str(d): xzkj.HID_CODES[str(d)] for d in range(10)}
SPACE = xzkj.HID_CODES["space"]

h = xzkj.open_vendor_interface()
try:
    for key_id in range(1, 25):
        s = f"{key_id:02d}"
        entries = [(0, DIGIT[c]) for c in s] + [(0, SPACE)]
        xzkj.bind_key_sequence(h, key_id, entries, layer=1)
        print(f"ID {key_id:2d} -> '{s} '")
    xzkj.finish(h)
    print("Ferdig. Trykk på alle taster og vri/trykk alle knotter i et tekstfelt.")
finally:
    h.close()
