# Daemonen — app-avhengige taster

Padden alene kan bare sende faste tastetrykk. Daemonen gjør den om til noe som vet
hvilken app du bruker: samme knott kan spole i Spotify og zoome i Figma.

Den løser også media-transporten. Padden har ingen fungerende consumer-koder for
play/pause/neste/forrige (se [PROTOCOL.md](PROTOCOL.md)) — men det trenger den ikke,
for daemonen sender dem via macOS' egne API-er i stedet.

## Slik henger det sammen

```
   Padden              Daemonen                    macOS
   ──────              ────────                    ─────
   knott 3 høyre  →  cmd+ctrl+shift+alt+F17  →  slår opp i profiles.yaml
                                                 ├─ Spotify i front?  → media:next
                                                 └─ ellers            → media:next
                                              →  sender NX_KEYTYPE_NEXT, svelger signalet
```

Padden flashes **én gang** med 24 unike signaler. Etterpå endrer du bare
`profiles.yaml` — padden trenger aldri røres igjen.

### Hvorfor F13–F20?

De finnes ikke på Mac-tastaturer, så ingenting annet bruker dem. macOS definerer
virtuelle tastekoder kun for F13–F20 (åtte), så vi bruker tre modifikatornivåer for
å få 24 unike signaler: rene, `ctrl+shift+alt+`, og `cmd+ctrl+shift+alt+`.
Se `signals.py` for kartet.

## Oppsett

```bash
.venv/bin/python setup_daemon.py --dry    # se planen
.venv/bin/python setup_daemon.py          # flash signalene (én gang)
cp profiles.example.yaml profiles.yaml    # din konfigurasjon
.venv/bin/python daemon.py
```

**Tilgjengelighet kreves.** Daemonen bruker en `CGEventTap`, og macOS krever
tillatelse: Systeminnstillinger → Personvern og sikkerhet → Tilgjengelighet → legg
til programmet du starter daemonen fra (Terminal, iTerm, VS Code …). Uten dette
returnerer `CGEventTapCreate` null, og daemonen sier fra.

## profiles.yaml

```yaml
default:
  knob3.press: media:playpause
  key5:        key:cmd+c

apps:
  com.spotify.client:          # delstreng av bundle-ID, ikke versalfølsom
    knob3.left:  media:prev
```

Alt som ikke er overstyrt for appen i front faller tilbake til `default`.
Filen leses på nytt automatisk når du lagrer.

### Handlinger

| Syntaks | Gjør |
|---|---|
| `media:playpause` `media:next` `media:prev` | mediatransport |
| `media:mute` `media:volumeup` `media:volumedown` | volum |
| `key:cmd+shift+4` | send en tastekombinasjon |
| `app:Spotify` | aktiver eller start en app |
| `url:https://…` | åpne en URL |
| `shell:…` | kjør en kommando |
| `none` | svelg signalet |

Finn bundle-ID-en til en app:

```bash
osascript -e 'id of app "Spotify"'
```

## Start automatisk ved innlogging

```bash
cp launchd/no.macropad.daemon.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/no.macropad.daemon.plist
```

Logg: `/tmp/macropad-daemon.log`. Stopp med `launchctl unload …`.

## Feilsøking

**«Kunne ikke opprette event tap»** — Tilgjengelighet mangler, se over. Har du gitt
tillatelsen før, kan den ha festet seg til gammel binærsti; fjern og legg til på nytt.

**Ingenting skjer når du trykker** — kjør `setup_daemon.py` på nytt, og sjekk at
padden faktisk sender: bind en tast til noe synlig med `app.py` og test i et tekstfelt.

**Signalene lekker ut i andre apper** — daemonen svelger kun signaler den kjenner
igjen. Kjører den ikke, går F13–F20 rett til appen i front (som regel ufarlig).
