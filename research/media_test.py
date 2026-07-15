#!/usr/bin/env python3
"""Test 5 hypoteser for media-binding ('volum opp') på knott 1 og 2."""
import xzkj

h = xzkj.open_vendor_interface()
send = lambda msg: xzkj._send(h, bytes(msg))

L = 1  # lag

# Knott 1: venstre=19 trykk=20 høyre=21 | Knott 2: venstre=16 trykk=17 høyre=18
tests = [
    ("H1 knott1-venstre: kbd-type, keyboard-page VolumeUp 0x80",
     [0x03, 0xFD, 19, L, 0x01, 0x00, 0x01, 0x00, 0x00, 0x80]),
    ("H2 knott1-trykk:   type2, count=1, 3-byte-entry [00 00 E9]",
     [0x03, 0xFD, 20, L, 0x02, 0x00, 0x01, 0x00, 0x00, 0xE9]),
    ("H3 knott1-høyre:   type2, count=1, kode LE på offset 7-8",
     [0x03, 0xFD, 21, L, 0x02, 0x00, 0x01, 0xE9, 0x00]),
    ("H4 knott2-venstre: type2, count=0, kode LE på offset 7-8 (k884x-stil)",
     [0x03, 0xFD, 16, L, 0x02, 0x00, 0x00, 0xE9, 0x00]),
    ("H5 knott2-høyre:   type3 m/ offset5=2, 3-byte-entry",
     [0x03, 0xFD, 18, L, 0x03, 0x02, 0x01, 0x00, 0x00, 0xE9]),
]

try:
    for desc, msg in tests:
        send(msg)
        print(desc)
    xzkj.finish(h)
    print("\nFlashet. Test: vri knott 1 begge veier + trykk, vri knott 2 begge veier.")
finally:
    h.close()
