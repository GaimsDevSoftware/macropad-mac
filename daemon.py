#!/usr/bin/env python3
"""
Daemon — gjør padden app-avhengig.

Padden sender signaler (F13–F24, med og uten hyper). Denne prosessen fanger dem,
sjekker hvilken app som er i front, og utfører handlingen fra profiles.yaml.
Signalet svelges, så ingen andre apper ser F13.

Start:   .venv/bin/python daemon.py
Krever:  Systeminnstillinger → Personvern og sikkerhet → Tilgjengelighet
         (legg til appen du kjører dette fra — Terminal, iTerm e.l.)
"""
import os
import sys

import yaml
import Quartz
from AppKit import NSWorkspace

import actions
import signals

HERE = os.path.dirname(os.path.abspath(__file__))
PROFILES = os.path.join(HERE, "profiles.yaml")

# Virtuelle tastekoder for F13–F20 (de eneste macOS definerer)
VK_F = {105: "f13", 107: "f14", 113: "f15", 106: "f16",
        64: "f17", 79: "f18", 80: "f19", 90: "f20"}

HYPER = (Quartz.kCGEventFlagMaskControl | Quartz.kCGEventFlagMaskShift |
         Quartz.kCGEventFlagMaskAlternate)
CMD = Quartz.kCGEventFlagMaskCommand


def signal_name(keycode, flags):
    """Oversett et tastetrykk til signalnavnet i signals.py, eller None."""
    name = VK_F.get(keycode)
    if not name:
        return None
    if (flags & (HYPER | CMD)) == (HYPER | CMD):
        return "cmd+ctrl+shift+alt+" + name
    if (flags & HYPER) == HYPER:
        return "ctrl+shift+alt+" + name
    if not (flags & (HYPER | CMD)):
        return name
    return None


class Daemon:
    def __init__(self):
        self.profiles = {}
        self.mtime = 0
        self.load()

    def load(self):
        try:
            with open(PROFILES) as f:
                self.profiles = yaml.safe_load(f) or {}
            self.mtime = os.path.getmtime(PROFILES)
            n = sum(len(v or {}) for k, v in self.profiles.items() if k != "apps")
            apps = list((self.profiles.get("apps") or {}).keys())
            print(f"Profiler lastet: standard + {len(apps)} app-overstyring(er)"
                  + (f" ({', '.join(apps)})" if apps else ""))
        except FileNotFoundError:
            print(f"Fant ikke {PROFILES} — lager ingen bindinger.")
            self.profiles = {}

    def maybe_reload(self):
        try:
            if os.path.getmtime(PROFILES) != self.mtime:
                self.load()
        except OSError:
            pass

    def action_for(self, target: str, bundle: str):
        apps = self.profiles.get("apps") or {}
        for pattern, mapping in apps.items():
            if pattern.lower() in bundle.lower() and target in (mapping or {}):
                return (mapping[target], pattern)
        default = self.profiles.get("default") or {}
        return (default.get(target), None)

    def handle(self, target: str):
        bundle = actions.frontmost()
        action, via = self.action_for(target, bundle)
        if not action:
            print(f"  {target}: ingen handling for {bundle}")
            return
        label = f"[{via}]" if via else "[standard]"
        print(f"  {target} {label} -> {action}")
        try:
            actions.run(action)
        except Exception as e:
            print(f"  ! feil: {e}")


def make_callback(d: Daemon):
    def cb(proxy, etype, event, refcon):
        if etype in (Quartz.kCGEventTapDisabledByTimeout,
                     Quartz.kCGEventTapDisabledByUserInput):
            Quartz.CGEventTapEnable(TAP, True)
            return event
        keycode = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
        flags = Quartz.CGEventGetFlags(event)
        sig = signal_name(keycode, flags)
        target = signals.BY_SIGNAL.get(sig) if sig else None
        if not target:
            return event  # ikke vårt signal — la den passere
        d.maybe_reload()
        d.handle(target)
        return None  # svelg signalet
    return cb


TAP = None


def main():
    d = Daemon()
    global TAP
    mask = Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown)
    TAP = Quartz.CGEventTapCreate(
        Quartz.kCGSessionEventTap, Quartz.kCGHeadInsertEventTap,
        Quartz.kCGEventTapOptionDefault, mask, make_callback(d), None)
    if not TAP:
        print("Kunne ikke opprette event tap.\n\n"
              "Gi Tilgjengelighet-tilgang til programmet du kjører dette fra:\n"
              "  Systeminnstillinger → Personvern og sikkerhet → Tilgjengelighet\n"
              "Legg til Terminal (eller iTerm/VS Code), huk av, og start på nytt.")
        sys.exit(1)
    src = Quartz.CFMachPortCreateRunLoopSource(None, TAP, 0)
    Quartz.CFRunLoopAddSource(Quartz.CFRunLoopGetCurrent(), src, Quartz.kCFRunLoopCommonModes)
    Quartz.CGEventTapEnable(TAP, True)
    print("Daemon kjører. Trykk på padden. Ctrl+C for å avslutte.\n")
    try:
        Quartz.CFRunLoopRun()
    except KeyboardInterrupt:
        print("\nAvsluttet.")


if __name__ == "__main__":
    main()
