#!/usr/bin/env python3
"""
Hvor ting ligger.

Når appen kjører fra en .app-bundle er koden skrivebeskyttet, så brukerens
konfigurasjon kan ikke ligge ved siden av den. Den hører hjemme i
~/Library/Application Support/Makropad/.

Kjører vi fra kildekoden (utvikling), brukes prosjektmappa — da slipper man å
lete etter filene mens man jobber.
"""
import os
import shutil
import sys

FROZEN = getattr(sys, "frozen", False)
BUNDLE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

if FROZEN:
    DATA = os.path.expanduser("~/Library/Application Support/Makropad")
else:
    DATA = os.path.dirname(os.path.abspath(__file__))

PROFILES = os.path.join(DATA, "profiles.yaml")
EXAMPLE = os.path.join(BUNDLE, "profiles.example.yaml")


def resource(name):
    """Fil som følger med programmet (ui.html, ikoner, eksempelprofil)."""
    p = os.path.join(BUNDLE, name)
    return p if os.path.exists(p) else None


def ensure_profiles():
    """Sørg for at det finnes en profiles.yaml å jobbe mot. Returnerer stien."""
    os.makedirs(DATA, exist_ok=True)
    if not os.path.exists(PROFILES) and os.path.exists(EXAMPLE):
        shutil.copy(EXAMPLE, PROFILES)
    return PROFILES
