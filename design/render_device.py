#!/usr/bin/env python3
"""Enhetsmockup for README — XZKJ 12-key/4-knob, geometri avlest fra fotoet."""
import cairosvg

W, H = 1180, 1120
SANS = "Instrument Sans"
THIN = "Jura Light"
MONO = "Geist Mono"

# Kropp: avrundet rektangel + sirkulær utbulning (lobe) for den store knotten.
import math

L, R, T, B = 115, 660, 190, 1260           # rektangel
LCX, LCY, LR = 743, 353, 150               # lobe: senter, radius
# der lobe skjærer rektangelets høyre kant (x = R)
DY = math.sqrt(LR**2 - (R - LCX)**2)       # = 124.9
P1Y, P2Y = LCY - DY, LCY + DY
BODY = (f"M {L+30} {T} L {R} {T} L {R} {P1Y:.1f} "
        f"A {LR} {LR} 0 1 1 {R} {P2Y:.1f} L {R} {B-30} "
        f"Q {R} {B} {R-30} {B} L {L+30} {B} Q {L} {B} {L} {B-30} "
        f"L {L} {T+30} Q {L} {T} {L+30} {T} Z")

KNOBS = {1: (200, 268, 62), 2: (197, 475, 62), 3: (432, 353, 84), 4: (743, 353, 112)}
COLS, ROWS = (195, 350, 522), (665, 827, 987, 1152)
KW, KH = 118, 108

s = []
s.append(f'<svg width="{W}" height="{H}" viewBox="60 150 1050 1200" xmlns="http://www.w3.org/2000/svg">')
s.append('''<defs>
<linearGradient id="alu" x1="0.1" y1="0" x2="0.5" y2="1">
  <stop offset="0" stop-color="#EDEDF0"/><stop offset="1" stop-color="#D9D9DE"/></linearGradient>
<linearGradient id="key" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#FEFEFE"/><stop offset="1" stop-color="#F0F0F2"/></linearGradient>
<radialGradient id="knob" cx="0.4" cy="0.34" r="0.86">
  <stop offset="0" stop-color="#FAFAFB"/><stop offset="1" stop-color="#CFCFD5"/></radialGradient>
</defs>''')
s.append('<rect x="0" y="0" width="1400" height="1400" fill="#F7F7F9"/>')

# kropp: myk skygge bygget av lag (unngår filterhalo)
for i in (18, 12, 7, 3):
    s.append(f'<g transform="translate(0,{i*0.7:.1f})" opacity="0.035">'
             f'<path d="{BODY}" fill="#1D1D1F" transform="scale({1+i*0.0009:.4f}) '
             f'translate({-i*0.32:.1f},{-i*0.62:.1f})"/></g>')
s.append(f'<path d="{BODY}" fill="url(#alu)"/>')
s.append(f'<path d="{BODY}" fill="none" stroke="#C4C4CA" stroke-width="2.5"/>')
# indre høylys langs kanten
s.append(f'<path d="{BODY}" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.55" '
         f'transform="translate(0,2)"/>')

# knotter
for n, (cx, cy, r) in KNOBS.items():
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r+3}" fill="#000" opacity="0.06"/>')
    s.append(f'<circle cx="{cx}" cy="{cy+4}" r="{r}" fill="#A2A2A8" opacity="0.5"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#knob)" stroke="#AEAEB4" stroke-width="3"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r-11}" fill="none" stroke="#E4E4E8" stroke-width="1.2"/>')
    s.append(f'<circle cx="{cx - r*0.52:.0f}" cy="{cy - r*0.52:.0f}" r="5" fill="#96969D"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="16" fill="#8A8A90"/>')
    s.append(f'<text x="{cx}" y="{cy+5.5}" text-anchor="middle" font-family="{MONO}" '
             f'font-size="16" fill="#FFFFFF" font-weight="bold">{n}</text>')

# taster
for i in range(12):
    x, y = COLS[i % 3], ROWS[i // 3]
    s.append(f'<rect x="{x-KW/2}" y="{y-KH/2+5}" width="{KW}" height="{KH}" rx="14" fill="#B6B6BC"/>')
    s.append(f'<rect x="{x-KW/2}" y="{y-KH/2}" width="{KW}" height="{KH}" rx="14" '
             f'fill="url(#key)" stroke="#C2C2C8" stroke-width="2"/>')
    s.append(f'<text x="{x}" y="{y+9}" text-anchor="middle" font-family="{MONO}" '
             f'font-size="25" fill="#A4A4AA">{i+5}</text>')

# etiketter
s.append(f'<line x1="900" y1="248" x2="948" y2="248" stroke="#D6D6DB" stroke-width="2"/>')
s.append(f'<text x="960" y="256" font-family="{THIN}" font-size="28" fill="#AEAEB4" letter-spacing="1">4 knotter</text>')
s.append(f'<text x="960" y="290" font-family="{SANS}" font-size="16" fill="#C6C6CC">vri · trykk · vri</text>')
s.append(f'<line x1="600" y1="900" x2="700" y2="900" stroke="#D6D6DB" stroke-width="2"/>')
s.append(f'<text x="712" y="908" font-family="{THIN}" font-size="28" fill="#AEAEB4" letter-spacing="1">12 taster</text>')
s.append(f'<text x="115" y="1322" font-family="{MONO}" font-size="16" fill="#C2C2C8" letter-spacing="3">'
         f'514C:8850 · @XZKJ-12key_4knob</text>')

s.append('</svg>')
doc = "\n".join(s)
with open("device.svg", "w") as f:
    f.write(doc)
cairosvg.svg2png(bytestring=doc.encode(), write_to="device.png", output_width=W*2, output_height=H*2)
print("ok")
