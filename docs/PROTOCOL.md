# Protokoll — XZKJ 12-key/4-knob (514C:8850)

Reverse-engineeret på macOS mot en fysisk enhet, juli 2026. Bygger på
[ch57x-keyboard-tool issue #153](https://github.com/kriomant/ch57x-keyboard-tool/issues/153),
som dokumenterte `03 fd`-rammen for 16-key/3-knob-varianten med samme VID/PID.

## Transport

USB HID, vendor-grensesnittet (usage page `0xFF00`, interface 0). Enheten eksponerer også
vanlige HID-grensesnitt (keyboard/mouse/consumer) på interface 1 — de er kun for input.

```python
devs = [d for d in hid.enumerate(0x514C, 0x8850) if d["usage_page"] == 0xFF00]
h = hid.device(); h.open_path(devs[0]["path"])
```

Output-rapporter er **65 byte** inkludert report-ID `0x03`, nullpolstret.

## Tastebinding (type 0x01)

```
offset  0     1     2       3      4     5     6      7...
        0x03  0xFD  key_id  layer  0x01  0x00  count  (delay_hi, delay_lo, hid_code) × count
```

- `layer` er 1-basert (1–3 på denne enheten)
- `count` ≤ 18 — modifikatorer teller med
- Hver oppføring er 3 byte: 16-bit big-endian forsinkelse i ms, så HID usage-ID

Modifikatorer er egne koder i sekvensen, og gjelder **den første ikke-modifikatoren som
følger**:

| Kode | Modifikator | Kode | Modifikator |
|---|---|---|---|
| `0xF1` | Venstre Ctrl | `0xF5` | Høyre Ctrl |
| `0xF2` | Venstre Shift | `0xF6` | Høyre Shift |
| `0xF3` | Venstre Alt | `0xF7` | Høyre Alt |
| `0xF4` | Venstre Meta/Cmd | `0xF8` | Høyre Meta |

Eksempel — `Ctrl+Alt+Delete` på tast-ID 1, lag 1:

```
03 fd 01 01 01 00 03  00 00 f1  00 00 f3  00 00 4c
```

## Museklikk (type 0x03)

```
03 fd key_id layer 03 00 01 00 buttons
```

`buttons` er en bitmaske: `1` = venstre, `2` = høyre, `4` = midt.

## Media

**Funn for denne varianten:** volum og mute ligger på **keyboard usage-siden**, ikke
consumer-siden, og bindes som helt vanlige tastekoder med type `0x01`:

| Kode | Funksjon |
|---|---|
| `0x7F` | Mute |
| `0x80` | Volum opp |
| `0x81` | Volum ned |

Consumer-typen (`0x02`) i k884x-stil ble testet i fem varianter og ga ingen respons på
denne enheten. Play/pause/neste/forrige er derfor fortsatt uløst — de finnes ikke på
keyboard-siden, så de må gå gjennom et consumer-format vi ennå ikke har funnet.

## Avslutte programmering

```
03 aa aa
03 fd fe ff
03 aa aa
```

## Key-ID-kart

Enheten teller tastene **nedenfra og opp, kolonnevis** — ikke i leserekkefølge. Kartlagt
empirisk ved å binde hver ID til å skrive sitt eget nummer.

Fysisk nummerering (som i programvaren og på README-illustrasjonen):

```
      (1)      (3)        ( 4 )
      (2)

       5    6    7
       8    9   10
      11   12   13
      14   15   16
```

Taster:

| Fysisk | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **key_id** | 4 | 8 | 12 | 3 | 7 | 11 | 2 | 6 | 10 | 1 | 5 | 9 |

Knotter — hver gir tre ID-er:

| Knott | Vri venstre | Trykk | Vri høyre |
|---|---|---|---|
| 1 (liten, øverst v.) | 19 | 20 | 21 |
| 2 (liten, nederst v.) | 16 | 17 | 18 |
| 3 (medium) | 22 | 23 | 24 |
| 4 (stor) | 13 | 14 | 15 |

Merk at knott 4 bruker ID 13–15 — området som på 15-key/3-knob-modeller er allokert til
taster. Samme observasjon er gjort i `k884x.rs` i ch57x-keyboard-tool: en tasterad byttes
i praksis mot en ekstra knott. Rekkefølgen på knottene (2 før 1, og 4 nederst) følger
ingen åpenbar logikk og må kartlegges per modell.

## Metode

`research/map_test.py` binder ID 1–24 til å skrive sitt eget tosifrede nummer; deretter
trykker man alt fysisk i et tekstfelt og leser av rekkefølgen. `research/media_test.py` og
`media_test2.py` tester hypoteser for media-formatet.
