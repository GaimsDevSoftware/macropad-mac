#!/usr/bin/env python3
"""
Handlinger daemonen kan utføre. Dette er stedet å legge til nye.

Handlingssyntaks i profiles.yaml:
    media:playpause     media:next  media:prev  media:mute
    media:volumeup      media:volumedown
    key:cmd+shift+4     send en tastekombinasjon
    app:Spotify         aktiver (eller start) en app
    url:https://…       åpne en URL
    shell:say hei       kjør en kommando
    none                gjør ingenting (svelg signalet)
"""
import subprocess

import Quartz
from AppKit import NSWorkspace

import keys

# NX_KEYTYPE-koder for systemets media-taster
NX = {
    "playpause": 16, "next": 17, "prev": 18, "fast": 19, "rewind": 20,
    "mute": 7, "volumeup": 0, "volumedown": 1,
    "brightnessup": 2, "brightnessdown": 3,
}

# Virtuelle tastekoder — felles kart, se keys.py
VK = {**keys.VK, "period": keys.VK["dot"]}   # 'period' er et vanlig alias

MODMASK = {
    "cmd": Quartz.kCGEventFlagMaskCommand,
    "shift": Quartz.kCGEventFlagMaskShift,
    "alt": Quartz.kCGEventFlagMaskAlternate,
    "opt": Quartz.kCGEventFlagMaskAlternate,
    "ctrl": Quartz.kCGEventFlagMaskControl,
}


def _media(name):
    code = NX.get(name)
    if code is None:
        raise ValueError(f"Ukjent media-handling: {name}")
    for down in (True, False):
        data = (code << 16) | ((0xA if down else 0xB) << 8)
        ev = Quartz.NSEvent.otherEventWithType_location_modifierFlags_timestamp_windowNumber_context_subtype_data1_data2_(
            14, (0, 0), 0xA00 if down else 0xB00, 0, 0, None, 8, data, -1)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, ev.CGEvent())


def _key(spec):
    parts = [p.strip().lower() for p in spec.split("+")]
    mods, key = parts[:-1], parts[-1]
    if key not in VK:
        raise ValueError(f"Ukjent tast: {key}")
    flags = 0
    for m in mods:
        if m not in MODMASK:
            raise ValueError(f"Ukjent modifikator: {m}")
        flags |= MODMASK[m]
    for down in (True, False):
        ev = Quartz.CGEventCreateKeyboardEvent(None, VK[key], down)
        Quartz.CGEventSetFlags(ev, flags)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, ev)


def _app(name):
    NSWorkspace.sharedWorkspace().launchApplication_(name)


def run(action: str):
    """Utfør en handling. Kaster ved ugyldig syntaks."""
    action = (action or "").strip()
    if not action or action == "none":
        return
    if ":" not in action:
        raise ValueError(f"Handling mangler type: {action!r}")
    kind, arg = action.split(":", 1)
    kind, arg = kind.strip().lower(), arg.strip()
    if kind == "media":
        _media(arg.lower())
    elif kind == "key":
        _key(arg)
    elif kind == "app":
        _app(arg)
    elif kind == "url":
        subprocess.Popen(["open", arg])
    elif kind == "shell":
        subprocess.Popen(arg, shell=True)
    else:
        raise ValueError(f"Ukjent handlingstype: {kind!r}")


def validate(action: str):
    """Sjekk syntaks uten å utføre."""
    action = (action or "").strip()
    if not action or action == "none":
        return
    if ":" not in action:
        raise ValueError(f"Handling mangler type: {action!r}")
    kind, arg = action.split(":", 1)
    kind, arg = kind.strip().lower(), arg.strip()
    if kind == "media":
        if arg.lower() not in NX:
            raise ValueError(f"Ukjent media-handling: {arg} (gyldige: {', '.join(NX)})")
    elif kind == "key":
        parts = [p.strip().lower() for p in arg.split("+")]
        if parts[-1] not in VK:
            raise ValueError(f"Ukjent tast: {parts[-1]}")
        for m in parts[:-1]:
            if m not in MODMASK:
                raise ValueError(f"Ukjent modifikator: {m}")
    elif kind not in ("app", "url", "shell"):
        raise ValueError(f"Ukjent handlingstype: {kind!r}")


def frontmost() -> str:
    app = NSWorkspace.sharedWorkspace().frontmostApplication()
    return app.bundleIdentifier() or ""
