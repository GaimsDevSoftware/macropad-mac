# macropad-mac

macOS-konfigurator for AliExpress-makropaden **XZKJ 12-key / 4-knob** (USB `514C:8850`) —
enheten som bare leveres med kinesisk Windows-programvare.

Protokollen er reverse-engineeret fra bunnen for denne varianten. Konfigurasjonen lagres i
tastaturets eget minne, så programvaren trengs bare når du endrer oppsettet.

## Er dette enheten din?

<img src="design/device.png" width="560" alt="XZKJ 12-key/4-knob makropad">

Tolv taster i 4×3, fire knotter — to små, én medium, én stor i en utstikkende lobe øverst til
høyre. Selges under mange navn. Sjekk USB-ID-en for å være sikker:

```bash
hidutil list | grep 514c
```

## Kom i gang

```bash
python3 -m venv .venv
.venv/bin/pip install hidapi pyyaml
.venv/bin/python app.py          # åpner http://127.0.0.1:8777
```

<img src="design/taktil_stillhet_makropad.png" width="720" alt="Grensesnitt">

Klikk en tast eller knott, skriv inn bindingen, trykk **Skriv til tastatur**.

### CLI-alternativ

```bash
.venv/bin/python macroctl.py flash config.example.yaml
.venv/bin/python macroctl.py validate config.example.yaml
.venv/bin/python macroctl.py list-keys
```

## Bindingssyntaks

| Eksempel | Betydning |
|---|---|
| `cmd+c` | Cmd + C |
| `cmd+shift+4` | flere modifikatorer |
| `h,e,i` | sekvens av trykk (maks 18 inkl. modifikatorer) |
| `c@100` | 100 ms forsinkelse før trykket |
| `volumeup` / `volumedown` / `mute` | volumkontroll |
| `mouse:left` | museklikk (`left` / `right` / `middle`) |

Modifikatorer: `cmd` `shift` `alt` `ctrl`, samt `rshift`, `ralt` osv. for høyre side.
Hver knott gir tre uavhengige bindinger: **vri venstre · trykk · vri høyre**.

## App-avhengige taster

Vil du at samme knott skal spole i Spotify og zoome i VS Code — eller ha play/pause i
det hele tatt — kjører du daemonen. Padden flashes med 24 usynlige signaler, og
daemonen oversetter dem etter hvilken app som er i front:

```bash
.venv/bin/python setup_daemon.py       # flash signalene — én gang
cp profiles.example.yaml profiles.yaml
.venv/bin/python daemon.py             # krever Tilgjengelighet-tilgang
```

```yaml
default:
  knob3.press: media:playpause
  key5:        key:cmd+c

apps:
  com.spotify.client:
    knob3.left:  media:prev
    knob3.right: media:next
```

Handlinger: `media:` (transport og volum), `key:`, `app:`, `url:`, `shell:`.
Filen lastes på nytt når du lagrer. Se [docs/DAEMON.md](docs/DAEMON.md).

Dette løser også play/pause/neste/forrige, som padden ikke får til på egen hånd —
daemonen sender dem gjennom macOS' egne media-API-er.

## Status

- ✅ Tastebindinger, modifikatorer, sekvenser, forsinkelser
- ✅ Volum opp/ned/mute direkte fra padden
- ✅ Museklikk
- ✅ App-avhengige taster og full mediatransport via daemonen
- ⚠️ Play/pause/neste/forrige *direkte fra padden* — consumer-format ikke funnet
      (daemonen gjør dette overflødig i praksis)
- ⬜ LED-styring
- ⬜ Lag 2 og 3 (protokollen støtter det; ikke testet)

Se [docs/PROTOCOL.md](docs/PROTOCOL.md) for key-ID-kartet og protokolldetaljene.

## Takk til

[kriomant/ch57x-keyboard-tool](https://github.com/kriomant/ch57x-keyboard-tool), og særlig
[@yawor sitt arbeid i issue #153](https://github.com/kriomant/ch57x-keyboard-tool/issues/153)
som knekket `03 fd`-rammeformatet på en beslektet 16-key/3-knob-variant. Dette prosjektet
kartlegger 12-key/4-knob-varianten og finner at media-taster her bruker keyboard-siden,
ikke consumer-siden.

## Lisens

MIT
