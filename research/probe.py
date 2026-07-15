#!/usr/bin/env python3
"""Probe: finn og åpne vendor-HID-grensesnittet på XZKJ-makropaden (514C:8850)."""
import hid

VID, PID = 0x514C, 0x8850

devs = [d for d in hid.enumerate(VID, PID)]
if not devs:
    print("Fant ingen enhet 514C:8850 — er den koblet til?")
    raise SystemExit(1)

for d in devs:
    print(f"path={d['path'].decode()} usage_page={d['usage_page']:#06x} "
          f"usage={d['usage']:#04x} interface={d['interface_number']}")

vendor = [d for d in devs if d["usage_page"] == 0xFF00]
if not vendor:
    print("\nFant ikke usage_page 0xFF00 — prøver interface-nummer i stedet.")
    raise SystemExit(2)

path = vendor[0]["path"]
print(f"\nÅpner vendor-grensesnitt: {path.decode()}")
h = hid.device()
h.open_path(path)
print("Åpnet OK:", h.get_manufacturer_string(), "/", h.get_product_string())
h.close()
