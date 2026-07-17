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
.venv/bin/pip install hidapi pyyaml pyobjc-framework-Quartz pyobjc-framework-Cocoa
.venv/bin/python app.py          # åpner http://127.0.0.1:8777
```

<img src="design/taktil_stillhet_makropad.png" width="720" alt="Grensesnitt">

1. **Klargjør padden** — én gang. Skriver 24 usynlige signaler til tastaturet.
2. Klikk en tast eller knott i tegningen, velg hva den skal gjøre.
3. Start daemonen: `.venv/bin/python daemon.py`

Padden trenger aldri reflashes igjen. Alt du endrer i grensesnittet får virkning
umiddelbart — daemonen laster profilen på nytt når den lagres.

**Tilgjengelighet kreves** for daemonen: Systeminnstillinger → Personvern og sikkerhet
→ Tilgjengelighet → legg til programmet du starter den fra.

## Hva en tast kan gjøre

| Type | Eksempel | |
|---|---|---|
| `media` | `playpause` `next` `prev` `mute` `volumeup` | via macOS' egne media-taster |
| `key` | `cmd+c` `cmd+shift+4` | send en tastekombinasjon |
| `app` | `Spotify` | aktiver eller start en app |
| `url` | `https://…` | åpne en lenke |
| `shell` | `say ferdig` | kjør en kommando |

Hver knott gir tre uavhengige handlinger: **vri venstre · trykk · vri høyre**.

### Profiler

Tre profiler — **Profil 1 / 2 / 3** — hver med sitt eget komplette oppsett (standard +
app-overstyringer). Bytt aktiv profil øverst i grensesnittet eller fra menylinja
(**Profil**-menyen). Daemonen dispatcher fra den aktive; bytte får virkning umiddelbart.

Profilene lever i software, ikke på padden. Det er med vilje: på denne enheten kan ikke
verten lese hvilket fysisk lag padden står på (firmware sender ingen beskjed), og
signal-modellen har ikke plass til tre lag med unike, kollisjonsfrie signaler. Software-
profiler gir samme resultat uten den usikkerheten.

### Per app

Legg til en app med **+** i grensesnittet, så overstyrer du bare tastene du vil ha
annerledes der — resten arves fra standardprofilen (vist nedtonet i tegningen).
Samme knott kan spole i Spotify og zoome i VS Code. App-overstyringer er per profil.

```yaml
default:
  knob3.press: media:playpause
apps:
  com.spotify.client:
    knob3.left:  media:prev
    knob3.right: media:next
```

Se [docs/DAEMON.md](docs/DAEMON.md) for hvordan det virker.

## Uten daemon

Vil du heller ha faste bindinger lagret i padden — uten noe kjørende programvare og
uten Tilgjengelighet-tilgang — bruker du CLI-en. Da mister du app-avhengighet og
mediatransport, men volum, taster og mus virker:

```bash
.venv/bin/python macroctl.py flash config.example.yaml
.venv/bin/python macroctl.py list-keys
```

Syntaks: `cmd+c`, `cmd+shift+4`, `h,e,i` (sekvens), `c@100` (forsinkelse),
`volumeup`/`volumedown`/`mute`, `mouse:left`.

## Status

- ✅ Tastebindinger, modifikatorer, sekvenser, forsinkelser
- ✅ Volum opp/ned/mute direkte fra padden
- ✅ Museklikk
- ✅ App-avhengige taster og full mediatransport via daemonen
- ✅ Tre software-profiler (Profil 1/2/3), byttes i UI-et eller menylinja
- ⚠️ Play/pause/neste/forrige *direkte fra padden* — consumer-format ikke funnet
      (daemonen gjør dette overflødig i praksis)
- ⬜ LED-styring
- ⬜ Fysiske hardware-lag (protokollen har `layer`-byte, men verten kan ikke lese
      aktivt lag — software-profiler brukes i stedet)

Se [docs/PROTOCOL.md](docs/PROTOCOL.md) for key-ID-kartet og protokolldetaljene.

## Takk til

[kriomant/ch57x-keyboard-tool](https://github.com/kriomant/ch57x-keyboard-tool), og særlig
[@yawor sitt arbeid i issue #153](https://github.com/kriomant/ch57x-keyboard-tool/issues/153)
som knekket `03 fd`-rammeformatet på en beslektet 16-key/3-knob-variant. Dette prosjektet
kartlegger 12-key/4-knob-varianten og finner at media-taster her bruker keyboard-siden,
ikke consumer-siden.

## Lisens

MIT
