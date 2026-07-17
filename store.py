#!/usr/bin/env python3
"""
Profillager — én kilde til sannhet for profiles.yaml.

Både konfiguratoren (app.py) og daemonen (daemon.py) leser samme fil, så skjemaet
må defineres ett sted. Ellers driver de fra hverandre.

Skjema:

    active: "Profil 1"
    profiles:
      "Profil 1": {default: {...}, apps: {...}}
      "Profil 2": {default: {},    apps: {}}
      "Profil 3": {default: {},    apps: {}}

Hver profil er et komplett sett: en standardprofil pluss app-overstyringer. Du
bytter aktiv profil i menylinja; daemonen dispatcher fra den aktive.

Gammelt format ({default, apps} på toppnivå) migreres til «Profil 1» ved lasting.
"""
import yaml

import paths

# Faste navn i v1 — tre profiler, alltid til stede.
NAMES = ["Profil 1", "Profil 2", "Profil 3"]


def _blank():
    return {"default": {}, "apps": {}}


def normalize(doc):
    """Tving fram et gyldig skjema. Idempotent — trygg å kjøre på alt."""
    doc = doc or {}

    # Migrer gammelt enkeltprofil-format: {default, apps} uten "profiles".
    if "profiles" not in doc:
        legacy = {"default": doc.get("default") or {},
                  "apps": doc.get("apps") or {}}
        doc = {"active": NAMES[0], "profiles": {NAMES[0]: legacy}}

    profs = doc.get("profiles") or {}
    # Garanter at de tre profilene finnes.
    for name in NAMES:
        profs.setdefault(name, _blank())
    # Garanter default+apps i hver.
    for prof in profs.values():
        prof.setdefault("default", {})
        prof.setdefault("apps", {})
    doc["profiles"] = profs

    # active må peke på en profil som finnes.
    if doc.get("active") not in profs:
        doc["active"] = NAMES[0]
    return doc


def load():
    """Les profiles.yaml, normalisert. Lager fila fra eksempelet ved behov."""
    path = paths.ensure_profiles()
    with open(path) as f:
        doc = yaml.safe_load(f) or {}
    return normalize(doc)


def save(doc):
    """Skriv normalisert doc til disk. Returnerer det som ble skrevet."""
    doc = normalize(doc)
    with open(paths.PROFILES, "w") as f:
        # profiles før active leser dårlig; behold active øverst.
        ordered = {"active": doc["active"], "profiles": doc["profiles"]}
        yaml.safe_dump(ordered, f, allow_unicode=True, sort_keys=False,
                       default_flow_style=False)
    return doc


def active_map(doc):
    """{default, apps} for den aktive profilen."""
    doc = normalize(doc)
    return doc["profiles"][doc["active"]]


def set_active(name):
    """Bytt aktiv profil på disk. Ignorerer ukjente navn. Returnerer doc."""
    doc = load()
    if name in doc["profiles"]:
        doc["active"] = name
        doc = save(doc)
    return doc
